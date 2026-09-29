# Week 4: Stata Group Assignment 3

U.S. industry dividend yields, debt-to-capital, market beta, and expected EPS growth. The report answers Questions 1-4 in order and follows the Week 2 layout, with consistent 12 pt question/answer text, 11 pt tables, and 10 pt captions/code.

- [Completed report](output/pdf/assignment3_report.pdf)
- [Stata analysis](assignment3.do)
- [Fitted-regression scatterplot](output/dividend_debt_fits.png)
- [Regression coefficients](output/coefficients.csv)
- [Model statistics](output/model_statistics.csv)

## Data and sample

Source: [Aswath Damodaran current data](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datacurrent.html). Original U.S. workbooks are dated January 5, 2026 and were downloaded September 29, 2026. Source URLs and SHA256 checksums are in `data/SOURCE.txt`. Frozen raw worksheet CSV exports are also included for independent verification.

Dividend yield uses `divfund.xls`; lease-adjusted market debt-to-capital uses `dbtfund.xls`; levered market beta uses `betas.xls`; expected annual EPS growth over the next five years uses `pedata.xls`. Yield, debt-to-capital, and growth are in percentage points; beta is unitless.

The 94 industry names match one-to-one across the four files. Aggregate market rows are excluded. Chemical (Diversified), Real Estate (General/Diversified), and Reinsurance lack EPS forecasts, leaving a common sample of 91 industries for all models. Industries receive equal weight; no outliers are removed. Standard errors are conventional OLS.

## Run

From the repository root in Stata 19 or later:

```stata
do run-week-04.do
```

Alternatively, change to `week-04` and run `do assignment3.do`. The runner returns to the repository root. Running replaces generated data, tables, and figures; original XLS snapshots remain unchanged. Logs are generated locally and ignored by Git.

To rebuild and numerically verify the PDF using Python:

```sh
python3 -m pip install -r week-04/scripts/requirements.txt
python3 week-04/scripts/build_report.py
```

The builder independently checks all coefficients, standard errors, t statistics, p values, R-squared values, and all 364 joined inputs against the frozen exports. It also renders local previews under `week-04/tmp/`, which are ignored by Git.
