version 19.0
clear all
set more off

* 1. Downloaded from Kenneth French's Data Library on 15 September 2026.
* Raw ZIPs and CSVs are preserved in data/raw for reproducibility.
* Original URLs:
* https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Portfolios_Formed_on_OP_CSV.zip
* https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip
* Row ranges select only the monthly blocks in this frozen vintage.
* OP columns 10-19 are the ten value-weighted decile portfolios.
import delimited using "data/raw/Portfolios_Formed_on_OP.csv", ///
    rowrange(26:782) varnames(nonames) asdouble clear
rename v1 yyyymm
forvalues d = 1/10 {
    local c = `d' + 9
    rename v`c' ret`d'
}
keep yyyymm ret1-ret10
isid yyyymm
tempfile portfolios
save `portfolios'

* Market excess return is column 2; RF is column 5.
* Mkt-RF is already an excess return: do not subtract RF again.
import delimited using "data/raw/F-F_Research_Data_Factors.csv", ///
    rowrange(6:1206) varnames(nonames) asdouble clear
rename v1 yyyymm
rename v2 market
rename v5 rf
keep yyyymm market rf
isid yyyymm
merge 1:1 yyyymm using `portfolios'
assert _merge != 2
keep if _merge == 3
drop _merge
generate month = ym(floor(yyyymm/100), mod(yyyymm,100))
format month %tm
sort month
tsset month
assert month == month[_n-1] + 1 if _n > 1
assert _N == 757
assert month[1] == ym(1963,7) & month[_N] == ym(2026,7)

* 2. Returns and RF are in percent per month; retain these units.
foreach v of varlist ret1-ret10 market rf {
    replace `v' = . if inlist(`v', -99.99, -999)
    assert !missing(`v')
}
forvalues d = 1/10 {
    generate double excess`d' = ret`d' - rf
    label variable excess`d' "OP decile `d': excess return (%)"
}
label variable month "Month"
label variable rf "One-month risk-free return (%)"
label data "Value-weighted OP deciles: July 1963-July 2026"
save "output/op_excess_returns.dta", replace
export delimited using "output/op_excess_returns.csv", replace

* 3. CAPM: excess_d = alpha_d + beta_d * market + error_d.
* Default OLS standard errors; coefficient t-statistics test zero.
tempfile statistics hacstats
tempname results hacresults bgstat bgpval
postfile `results' byte decile int n double alpha se_alpha t_alpha ///
    beta se_beta t_beta r2 t_beta1 p_beta1 bp_chi2 bp_p bg_chi2 bg_p ///
    using `statistics', replace
postfile `hacresults' byte decile int n double alpha se_alpha t_alpha ///
    beta se_beta t_beta r2 t_beta1 p_beta1 using `hacstats', replace
forvalues d = 1/10 {
    quietly regress excess`d' market
    * Breusch-Pagan test: H0 is constant error variance.
    quietly estat hettest
    local bp = r(chi2)
    local bpp = r(p)
    * Joint Breusch-Godfrey test of residual lags 1 through 12.
    quietly estat bgodfrey, lags(12)
    matrix `bgstat' = r(chi2)
    matrix `bgpval' = r(p)
    local fit = e(r2)
    local t1 = (_b[market] - 1) / _se[market]
    local p1 = 2*ttail(e(df_r), abs(`t1'))
    post `results' (`d') (e(N)) (_b[_cons]) (_se[_cons]) ///
        (_b[_cons]/_se[_cons]) (_b[market]) (_se[market]) ///
        (_b[market]/_se[market]) (e(r2)) (`t1') (`p1') (`bp') (`bpp') ///
        (`bgstat'[1,1]) (`bgpval'[1,1])
    * 4. Two-sided test of beta = 1; equivalent to t1 squared.
    test market = 1
    assert abs(r(p) - `p1') < 1e-8
    * Newey-West HAC: heteroskedasticity and 12 monthly serial lags.
    quietly newey excess`d' market, lag(12)
    local t1 = (_b[market] - 1) / _se[market]
    local p1 = 2*ttail(e(df_r), abs(`t1'))
    post `hacresults' (`d') (e(N)) (_b[_cons]) (_se[_cons]) ///
        (_b[_cons]/_se[_cons]) (_b[market]) (_se[market]) ///
        (_b[market]/_se[market]) (`fit') (`t1') (`p1')
    test market = 1
    assert abs(r(p) - `p1') < 1e-8
}
postclose `hacresults'
postclose `results'
use `statistics', clear
generate str16 classification = "Not distinguish."
replace classification = "Cyclical" if p_beta1 < .05 & beta > 1
replace classification = "Defensive" if p_beta1 < .05 & beta < 1
format alpha-r2 t_beta1 %9.4f
format p_beta1 %10.7f
list, noobs separator(0)
save "output/capm_results.dta", replace
export delimited using "output/capm_results.csv", replace

use `hacstats', clear
generate str16 classification = "Not distinguish."
replace classification = "Cyclical" if p_beta1 < .05 & beta > 1
replace classification = "Defensive" if p_beta1 < .05 & beta < 1
format alpha-r2 t_beta1 %9.4f
format p_beta1 %10.7f
list, noobs separator(0)
save "output/capm_hac_results.dta", replace
export delimited using "output/capm_hac_results.csv", replace
