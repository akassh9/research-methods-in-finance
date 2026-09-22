# Week 3 · Stata Group Assignment 2

Simple CAPM analysis using ten value-weighted operating-profitability deciles.

## Deliverables

- [Completed report with Stata code appendix](output/pdf/assignment2_report.pdf)
- [Original questions](assignment2_questions.pdf)
- [Stata do-file](assignment2.do)
- [Regression results and beta tests (CSV)](output/capm_results.csv)
- [Newey–West regression and beta-test results (CSV)](output/capm_hac_results.csv) and [Stata dataset](output/capm_hac_results.dta)
- [Results dataset](output/capm_results.dta)
- [Monthly excess returns (CSV)](output/op_excess_returns.csv) and [Stata dataset](output/op_excess_returns.dta)
- [Editable report](report/report.tex)

## Data and method

The Kenneth French source files, downloaded September 15, 2026, are included in this folder. Sources and checksums are in [data/raw/SOURCE.txt](data/raw/SOURCE.txt). The sample is July 1963–July 2026: 757 monthly observations per portfolio. Decile 1 is lowest profitability; decile 10 is highest.

Portfolio excess return = portfolio return minus RF, in percent per month. Regress each excess return on an intercept and Mkt-RF (already a market excess return). Report conventional OLS as a baseline, then use Newey–West HAC standard errors with 12 monthly lags for final inference. Test beta = 1 with two-sided, unadjusted p-values at 5%, using 755 residual degrees of freedom. HAC inference accounts for heteroskedasticity and serial correlation; p-values are not adjusted for multiple comparisons.

## Run

From the repository root in Stata:

```stata
do run-week-03.do
```

Or run `do assignment2.do` from inside `week-03`. Requires Stata 19 or newer; no extra packages or downloads. The runner returns to the repository root. Running it replaces generated Week 3 datasets and results; source data remain unchanged.

To independently validate the results and rebuild the PDF:

```sh
python3 week-03/scripts/build_report.py
```

Requires Python 3 with NumPy and a TeX distribution with `latexmk`, `newtx`, `pgfplots`, and `listings`. Run Stata first after changing the analysis. The builder checks 220 statistics, 20 classifications, all 7,570 monthly excess returns and the matched market returns against the raw data, then generates the report tables and compiles the PDF. The appendix reads the do-file directly. The written discussion must be reviewed if the data or method changes.

## Main results

With Newey–West standard errors, deciles 1–2 are cyclical and deciles 6 and 9 are defensive at 5%. The other betas are not significantly different from one. Alphas remain significantly negative for deciles 1 and 3 and significantly positive for deciles 8 and 9. R-squared ranges from 0.777 to 0.904.

## Diagnostics and HAC inference

After each OLS regression, the code runs the default Breusch–Pagan/Cook–Weisberg test (`estat hettest`), which assumes normal errors and tests constant variance against variation with fitted values. At 5%, it rejects for deciles 2, 4 and 10.

The Breusch–Godfrey test (`estat bgodfrey, lags(12)`) jointly tests no residual serial correlation at lags 1–12, with chi-squared reference degrees of freedom 12. Stata's default zero-filling of unavailable initial residual lags retains all 757 observations. It rejects at 5% for deciles 1, 2, 7, 8, 9 and 10. This conventional diagnostic is not itself robust to heteroskedasticity.

The code then runs `newey excessN market, lag(12)` for each decile. Twelve monthly lags cover a year and are a stated modeling choice. Newey–West uses Bartlett weights and Stata's N/(N−2) finite-sample adjustment. Point estimates and R-squared are unchanged; standard errors, coefficient tests and beta-equals-one tests are recomputed. The report uses HAC results for the final conclusions, regardless of the diagnostic outcomes.

The builder independently checks the diagnostics via auxiliary regressions and the HAC covariance via the Newey–West formula, in addition to verifying the OLS estimates, p-values, classifications and monthly returns.
