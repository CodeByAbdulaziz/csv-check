# CSV Check

[![Tests](https://github.com/CodeByAbdulaziz/csv-check/actions/workflows/tests.yml/badge.svg)](https://github.com/CodeByAbdulaziz/csv-check/actions/workflows/tests.yml)

A small Python tool to find common problems in CSV files before analysis.

## What it checks

- Empty and whitespace-only cells
- Repeated rows
- Missing or repeated column names
- Rows with too many or too few columns
- Empty files and CSV parsing errors

## Run

You need Python 3.10 or newer. There are no packages to install.

```bash
git clone https://github.com/CodeByAbdulaziz/csv-check.git
cd csv-check
python csv_check.py examples/saudi_sales.csv
```

The sample has two empty cells and one repeated row:

```text
CSV Check
File: examples/saudi_sales.csv
Rows: 5 | Columns: 3
Missing cells: 2
Repeated rows: 1
Rows with wrong column count: 0
Header issues: 0

Missing by column:
  Column 2 ('city'): 1
  Column 3 ('sales_sar'): 1

Repeated row numbers: 4

Result: Issues found.
```

Try a file without these problems:

```bash
python csv_check.py examples/clean_sales.csv
```

Both CSV files contain made-up sales data for Saudi cities. Amounts are in Saudi riyals (SAR).

## JSON report

```bash
python csv_check.py examples/saudi_sales.csv --json
```

The report includes missing values per column and row numbers for repeats and wrong column counts. Errors go to stderr, so JSON output stays valid.

## How the checks work

Empty cells include spaces and missing fields in short rows. Extra fields are reported as row width problems. Duplicate rows must have exactly the same cell values. Column names are checked after removing outer spaces; letter case is kept.

Row numbers count CSV records, including the header as row 1. A quoted value with a newline still counts as one record. Blank records are checked too. Repeated row counts include repeats after the first copy.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | No issues found in these basic checks |
| 1 | Data or header issues found |
| 2 | File, encoding, or parsing error |

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests also run on GitHub when code is pushed or a pull request is opened.

## Limits

This tool reads comma-separated UTF-8 files, including files with a UTF-8 BOM. It reports problems and leaves the file unchanged. It does not check data types, dates, business rules, or whether numbers are correct. Duplicate detection keeps row values in memory, so it is best for small and medium files.
