import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from csv_check import check_csv, main


class CsvCheckTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "data.csv"

    def write_csv(self, text):
        self.path.write_text(text, encoding="utf-8")

    def run_cli(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = main([str(self.path), *args])
        return code, output.getvalue(), errors.getvalue()

    def test_bom_quoted_commas_and_newlines(self):
        self.write_csv('\ufeffcity,note\nRiyadh,"one, two"\nJeddah,"two\nlines"\n')
        report = check_csv(self.path)
        self.assertEqual(report["rows"], 2)
        self.assertFalse(report["has_issues"])
        self.assertEqual(self.run_cli()[0], 0)

    def test_missing_cells_duplicate_headers_and_rows(self):
        self.write_csv(" city,city, \nRiyadh, ,\nRiyadh, ,\n")
        report = check_csv(self.path)
        self.assertEqual(report["missing_cells"], 4)
        self.assertEqual(report["duplicate_rows"], [3])
        self.assertEqual(report["header_issues"], ["Column 3 has no name.", "Header 'city' is repeated."])
        self.assertEqual([column["missing"] for column in report["missing_by_column"]], [0, 2, 2])
        self.assertEqual(self.run_cli()[0], 1)

    def test_short_and_long_rows(self):
        self.write_csv("city,sales_sar\nRiyadh\nJeddah,900,extra\n")
        report = check_csv(self.path)
        self.assertEqual(report["row_width_issues"], [
            {"row": 2, "expected": 2, "actual": 1},
            {"row": 3, "expected": 2, "actual": 3},
        ])
        self.assertEqual(report["missing_cells"], 1)

    def test_json_output_is_valid_and_has_no_text(self):
        self.write_csv("city,sales_sar\nRiyadh,1200\n")
        code, output, errors = self.run_cli("--json")
        self.assertEqual(code, 0)
        self.assertEqual(errors, "")
        self.assertEqual(json.loads(output)["rows"], 1)

    def test_empty_file_and_empty_header(self):
        self.write_csv("")
        code, output, errors = self.run_cli()
        self.assertEqual((code, output), (2, ""))
        self.assertIn("The file is empty.", errors)
        self.write_csv("\n")
        self.assertEqual(check_csv(self.path)["header_issues"], ["The header row is empty."])
        self.assertEqual(self.run_cli()[0], 1)

    def test_missing_file_and_bad_quotes(self):
        code, output, errors = self.run_cli("--json")
        self.assertEqual((code, output), (2, ""))
        self.assertTrue(errors.startswith("Error:"))
        self.write_csv('city,note\nRiyadh,"not closed\n')
        code, output, errors = self.run_cli()
        self.assertEqual((code, output), (2, ""))
        self.assertIn("unexpected end of data", errors)

    def test_row_numbers_count_records_including_header(self):
        self.write_csv('city,note\nRiyadh,"two\nlines"\nRiyadh,"two\nlines"\n')
        self.assertEqual(check_csv(self.path)["duplicate_rows"], [3])

    def test_duplicates_use_exact_cell_values(self):
        self.write_csv("city\nRiyadh\n Riyadh\nRiyadh\n")
        self.assertEqual(check_csv(self.path)["duplicate_rows"], [4])


if __name__ == "__main__":
    unittest.main()
