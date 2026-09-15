# Research Methods in Finance

Olin Business School, Washington University in St. Louis · Fall 2026

Shared coursework repository for the class. Each week has its own code, data, documentation and deliverables.

## Coursework

| Week | Topic | Report | Code |
| --- | --- | --- | --- |
| [Week 2](week-02/README.md) | Stata Group Assignment 1: operating-profitability deciles | [PDF](week-02/output/pdf/assignment1_report.pdf) | [Stata do-file](week-02/assignment1.do) |

Add later work in `week-03/`, `week-04/`, and so on. Week numbers describe the class schedule; assignment numbers retain the instructor's numbering.

## Get started

1. Clone this repository or download it as a ZIP and extract it.
2. Open Stata (the analysis was run with StataNow/BE 19.5; code declares version 19.0).
3. Set the working directory to your local copy of this repository, then run:

```stata
cd "/path/to/research-methods-in-finance"
do run-week-02.do
```

The runner returns to the repository root when it finishes. Week 2 uses the included data snapshot and requires no additional Stata packages or live downloads. Running it replaces the generated Week 2 data, table and graph; it leaves raw data unchanged.

## Organization

```text
research-methods-in-finance/
├── README.md
├── CONTRIBUTING.md
├── run-week-02.do
└── week-02/
    ├── README.md
    ├── assignment1.do
    ├── data/raw/           # Frozen source CSVs, ZIPs and checksums
    ├── output/             # Analysis data, summary statistics and chart
    │   └── pdf/            # Completed report with code appendix
    ├── report/             # Editable LaTeX report and generated figure/table data
    └── scripts/            # PDF rebuild and numerical validation
```

## Team workflow

Keep changes within the relevant week. Use a branch and pull request for review, and include what changed and how you checked it. See [CONTRIBUTING.md](CONTRIBUTING.md).

This repository is public: anyone with the link can view or clone it. Teammates can propose changes through pull requests; repository owners can grant direct write access under **Settings → Collaborators**.
