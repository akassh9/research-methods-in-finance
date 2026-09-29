* Stata Group Assignment 3 - Group 10
* Run from the week-04 folder. Original January 2026 XLS files are preserved.
version 19.0
clear all
set more off
cd "."
capture log close
log using "output/assignment3.log", text replace

* 1. U.S. industry data: dividend yield, market debt/capital, beta, EPS growth.
tempfile dividends debt betas
import excel "data/divfund.xls", sheet("Industry Averages") cellrange(A9) clear
keep A F
rename (A F) (industry dividend_yield)
replace industry = strtrim(industry)
drop if industry == "" | strpos(industry, "Total Market") == 1
isid industry
save `dividends'
import excel "data/dbtfund.xls", sheet("Industry Averages") cellrange(A9) clear
keep A F
rename (A F) (industry debt_capital)
replace industry = strtrim(industry)
drop if industry == "" | strpos(industry, "Total Market") == 1
isid industry
save `debt'
import excel "data/betas.xls", sheet("Industry Averages") cellrange(A11) clear
keep A C
rename (A C) (industry market_beta)
replace industry = strtrim(industry)
drop if industry == "" | strpos(industry, "Total Market") == 1
isid industry
save `betas'
import excel "data/pedata.xls", sheet("Industry Averages") cellrange(A9) clear
keep A I
rename (A I) (industry eps_growth)
replace industry = strtrim(industry)
drop if industry == "" | strpos(industry, "Total Market") == 1
isid industry
merge 1:1 industry using `dividends', assert(match) nogen
merge 1:1 industry using `debt', assert(match) nogen
merge 1:1 industry using `betas', assert(match) nogen
foreach v in dividend_yield debt_capital market_beta eps_growth {
 capture confirm string variable `v'
 if !_rc destring `v', replace ignore("NA")
}
* Convert decimal ratios to percentage points; beta remains unitless.
foreach v in dividend_yield debt_capital eps_growth {
 replace `v' = 100 * `v'
}
label variable dividend_yield "Dividend yield (%)"
label variable debt_capital "Market debt/capital, lease-adjusted (%)"
label variable market_beta "Levered market beta"
label variable eps_growth "Expected annual EPS growth, next 5 years (%)"
misstable summarize dividend_yield debt_capital market_beta eps_growth
count
count if missing(dividend_yield, debt_capital, market_beta, eps_growth)
drop if missing(dividend_yield, debt_capital, market_beta, eps_growth)
assert inrange(debt_capital, 0, 100)
sort industry
save "output/industry_data.dta", replace
export delimited using "output/industry_data.csv", replace
summarize dividend_yield debt_capital market_beta eps_growth

* 2. Linear, quadratic and cubic OLS; common industry sample.
generate double debt_sq = debt_capital^2
generate double debt_cube = debt_capital^3
tempname coef stats
postfile `coef' str12 model str20 term double coefficient se t p using "output/coefficients.dta", replace
postfile `stats' str12 model double n r2 adj_r2 using "output/model_statistics.dta", replace
foreach model in linear quadratic cubic multiple {
 local rhs debt_capital
 if "`model'" == "quadratic" local rhs debt_capital debt_sq
 if "`model'" == "cubic" local rhs debt_capital debt_sq debt_cube
 if "`model'" == "multiple" local rhs debt_capital market_beta eps_growth
 regress dividend_yield `rhs'
 estimates store `model'
 post `stats' ("`model'") (e(N)) (e(r2)) (e(r2_a))
 foreach term in `rhs' _cons {
  post `coef' ("`model'") ("`term'") (_b[`term']) (_se[`term']) ///
   (_b[`term']/_se[`term']) (2*ttail(e(df_r),abs(_b[`term']/_se[`term'])))
 }
 if "`model'" != "multiple" predict double fit_`model', xb
 if "`model'" == "quadratic" test debt_sq
 if "`model'" == "cubic" {
  test debt_cube
  test debt_sq debt_cube
 }
}
postclose `coef'
postclose `stats'
twoway (scatter dividend_yield debt_capital, mcolor(gs9) msize(small)) ///
 (line fit_linear debt_capital, sort lcolor(navy)) ///
 (line fit_quadratic debt_capital, sort lcolor(maroon) lpattern(dash)) ///
 (line fit_cubic debt_capital, sort lcolor(forest_green) lpattern(dot)), ///
 title("Dividend yield and debt-to-capital") ///
 subtitle("U.S. industries | January 2026") ///
 xtitle("Market debt-to-capital, lease-adjusted (%)") ytitle("Dividend yield (%)") ///
 legend(order(1 "Industries" 2 "Linear" 3 "Quadratic" 4 "Cubic") rows(1) position(6)) ///
 xlabel(0(20)80, format(%3.0f)) ylabel(0(2)8, format(%3.0f)) ///
 graphregion(color(white)) name(assignment3_plot, replace)
graph export "output/dividend_debt_fits.png", width(1800) replace
graph save "output/dividend_debt_fits.gph", replace

* 3. Multiple linear regression: conventional OLS standard errors.
estimates restore multiple
estimates table multiple, b(%10.6f) se(%10.6f) t(%10.4f) stats(N r2)
preserve
use "output/coefficients.dta", clear
export delimited using "output/coefficients.csv", replace
restore
preserve
use "output/model_statistics.dta", clear
export delimited using "output/model_statistics.csv", replace
restore
save "output/industry_analysis.dta", replace
log close
