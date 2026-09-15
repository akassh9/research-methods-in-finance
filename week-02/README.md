# Week 2 · Stata Group Assignment 1

## Task

Use ten characteristic-sorted portfolios from Kenneth French's Data Library, calculate monthly excess returns, report means, sample standard deviations and two-sided tests of zero mean, discuss the results, plot one portfolio and include a Stata code appendix.

## Deliverables

- [Completed report](output/pdf/assignment1_report.pdf)
- [Stata code](assignment1.do)
- [Results table (CSV)](output/summary_statistics.csv)
- [Decile 10 chart](output/op_decile10.png) and [editable Stata graph](output/op_decile10.gph)
- [Analysis dataset (Stata)](output/op_excess_returns.dta) and [CSV](output/op_excess_returns.csv)

## Data and methods

**Selection:** Value-weighted operating-profitability deciles, from lowest (1) to highest (10).

**Sample:** July 1963–July 2026; 757 complete monthly observations per decile.

**Units:** Percent per month. Excess return = portfolio return − monthly RF. The tests use `ttest`, with 756 degrees of freedom and two-sided p-values. They do not adjust for serial correlation or multiple testing.

**Sources:** [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html), [OP definitions](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_port_form_op.html).

Downloaded September 15, 2026, using the July 2026 CRSP vintage:

- [Operating-profitability ZIP](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Portfolios_Formed_on_OP_CSV.zip)
- [Fama/French factors ZIP (RF column)](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip)
- [Preserved snapshots and SHA-256 checksums](data/raw/SOURCE.txt)

The do-file's row ranges select monthly blocks in these frozen files. Replacing them with a new vintage requires updating the ranges and sample checks.

## Run

From the repository root in Stata:

```stata
do run-week-02.do
```

Alternatively, from `week-02` itself:

```stata
do assignment1.do
```

Stata regenerates the data, table, PNG/GPH graph and local `output/assignment1.log`. Logs are ignored by Git. All 40 reported statistics were independently checked against the raw CSV data.

## Rebuild the report (optional)

The report is typeset in LaTeX. Its editable source is [report/report.tex](report/report.tex). Install Python 3 and a full TeX distribution (MacTeX or TeX Live) with `latexmk`, `newtx`, `pgfplots`, and `listings`. No third-party Python packages are required.

From the repository root:

```sh
python3 week-02/scripts/build_report.py
```

Run Stata first if analysis code changed. The builder independently verifies all 40 statistics, refreshes the LaTeX table and vector-chart data, then compiles the report. Intermediate TeX files go under ignored `week-02/tmp/latex/`. The final PDF remains in `output/pdf/assignment1_report.pdf`.

Review the PDF after edits. The discussion is specific to this sample and must be revised if data or methods change. The appendix includes the current `assignment1.do` directly, avoiding a separately maintained copy.

## Main result

Nine deciles reject the zero-mean null at 5%; decile 1 does not (p = 0.0672). The pattern in mean excess returns is not monotonic. Individual portfolio tests do not test a high-minus-low spread or risk-adjusted abnormal performance.
