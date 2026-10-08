"""Check common CSV problems using only the Python standard library."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys


def check_csv(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, strict=True)
        headers = next(reader, None)
        if headers is None:
            raise ValueError("The file is empty.")

        names = [name.strip() for name in headers]
        header_issues = []
        if not names:
            header_issues.append("The header row is empty.")
        for index, name in enumerate(names, start=1):
            if not name:
                header_issues.append(f"Column {index} has no name.")
        for name, count in Counter(names).items():
            if name and count > 1:
                header_issues.append(f"Header {name!r} is repeated.")

        missing = [0] * len(headers)
        seen = set()
        duplicate_rows = []
        row_width_issues = []
        row_count = 0

        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            if len(row) != len(headers):
                row_width_issues.append({
                    "row": row_number,
                    "expected": len(headers),
                    "actual": len(row),
                })
            for index in range(len(headers)):
                if index >= len(row) or not row[index].strip():
                    missing[index] += 1

            values = tuple(row)
            if values in seen:
                duplicate_rows.append(row_number)
            else:
                seen.add(values)

    return {
        "file": str(path),
        "rows": row_count,
        "columns": len(headers),
        "header_issues": header_issues,
        "missing_cells": sum(missing),
        "missing_by_column": [
            {"column": index + 1, "name": names[index], "missing": count}
            for index, count in enumerate(missing)
        ],
        "duplicate_rows": duplicate_rows,
        "row_width_issues": row_width_issues,
        "has_issues": bool(header_issues or sum(missing) or duplicate_rows or row_width_issues),
    }


def print_report(report: dict) -> None:
    print("CSV Check")
    print(f"File: {report['file']}")
    print(f"Rows: {report['rows']} | Columns: {report['columns']}")
    print(f"Missing cells: {report['missing_cells']}")
    print(f"Repeated rows: {len(report['duplicate_rows'])}")
    print(f"Rows with wrong column count: {len(report['row_width_issues'])}")
    print(f"Header issues: {len(report['header_issues'])}")

    if report["header_issues"]:
        print("\nHeader problems:")
        for issue in report["header_issues"]:
            print(f"  {issue}")
    if report["missing_cells"]:
        print("\nMissing by column:")
        for column in report["missing_by_column"]:
            if column["missing"]:
                print(f"  Column {column['column']} ({column['name']!r}): {column['missing']}")
    if report["duplicate_rows"]:
        numbers = ", ".join(str(row) for row in report["duplicate_rows"])
        print(f"\nRepeated row numbers: {numbers}")
    if report["row_width_issues"]:
        print("\nRow width problems:")
        for issue in report["row_width_issues"]:
            print(f"  Row {issue['row']}: expected {issue['expected']}, found {issue['actual']}")

    result = "Issues found." if report["has_issues"] else "No issues found in these basic checks."
    print(f"\nResult: {result}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check a CSV file for common data problems.")
    parser.add_argument("file", type=Path, help="Path to a comma-separated UTF-8 CSV file")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    args = parser.parse_args(argv)

    try:
        report = check_csv(args.file)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)
    return 1 if report["has_issues"] else 0


if __name__ == "__main__":
    sys.exit(main())
