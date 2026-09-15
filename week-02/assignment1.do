version 19.0
clear all
set more off
* Run from week-02, or use run-week-02.do from the repository root.
* Frozen July 2026 data vintage.
capture mkdir output
capture log close assignment1
log using "output/assignment1.log", text replace name(assignment1)

* 1. Downloaded from Kenneth French's Data Library on 15 September 2026.
* Raw ZIPs and CSVs are preserved in data/raw for reproducibility.
* Original URLs:
* https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Portfolios_Formed_on_OP_CSV.zip
* https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip
* Row ranges select only the monthly blocks in this frozen vintage.
* OP columns 10-19 are the ten value-weighted decile portfolios.
import delimited using "data/raw/Portfolios_Formed_on_OP.csv", ///
    rowrange(26:782) varnames(nonames) clear
rename v1 yyyymm
forvalues d = 1/10 {
    local c = `d' + 9
    rename v`c' ret`d'
}
keep yyyymm ret1-ret10
isid yyyymm
tempfile portfolios
save `portfolios'

* Monthly RF is column 5 of the Fama/French three-factor file.
import delimited using "data/raw/F-F_Research_Data_Factors.csv", ///
    rowrange(6:1206) varnames(nonames) clear
rename v1 yyyymm
rename v5 rf
keep yyyymm rf
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
foreach v of varlist ret1-ret10 rf {
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

* 3. One-sample, two-sided t tests: H0: E[excess_d] = 0.
* t = mean / (sample SD / sqrt(N)); p = 2*ttail(N-1,abs(t)).
tempfile statistics
tempname results
postfile `results' byte decile int n double mean sd t p ///
    using `statistics', replace
forvalues d = 1/10 {
    quietly ttest excess`d' == 0
    post `results' (`d') (r(N_1)) (r(mu_1)) (r(sd_1)) (r(t)) (r(p))
}
postclose `results'
preserve
use `statistics', clear
format mean sd t %9.4f
format p %10.7f
list, noobs separator(0)
save "output/summary_statistics.dta", replace
export delimited using "output/summary_statistics.csv", replace
restore

* 4. Time-series figure: highest operating-profitability decile.
twoway line excess10 month, ///
    title("Highest-profitability decile: monthly excess return") ///
    subtitle("Value-weighted OP decile 10 | July 1963-July 2026") ///
    ytitle("Excess return (% per month)") xtitle("Year") ///
    xlabel(0(120)720, format(%tmCCYY)) ///
    yline(0, lcolor(gs9) lpattern(dash)) ///
    lcolor(navy) lwidth(thin) graphregion(color(white)) ///
    note("Source: Kenneth French Data Library; portfolio return minus RF.") ///
    name(op_decile10, replace)
graph save "output/op_decile10.gph", replace
graph export "output/op_decile10.png", width(2400) replace
log close assignment1
