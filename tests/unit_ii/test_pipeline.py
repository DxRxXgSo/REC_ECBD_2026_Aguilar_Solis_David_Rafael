import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.unit_ii import DataValidationError, EXPECTED_COLUMNS, process, read_source, sha256


def sample_frame():
    return pd.DataFrame([{
        "Gender": "Female", "Age": 21.0, "Height": 1.6, "Weight": 60.0,
        "family_history_with_overweight": "yes", "FAVC": "no", "FCVC": 2.0,
        "NCP": 3.0, "CAEC": "Sometimes", "SMOKE": "no", "CH2O": 2.0,
        "SCC": "no", "FAF": 1.0, "TUE": 1.0, "CALC": "no",
        "MTRANS": "Walking", "NObeyesdad": "Normal_Weight",
    }])


class UnitIIPipelineTests(unittest.TestCase):
    def test_valid_input_preserves_rows_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.csv"
            output = root / "processed.csv"
            manifest = root / "manifest.json"
            sample_frame().to_csv(source, index=False)
            first = process(source, output, manifest, expected_rows=None)
            first_bytes = output.read_bytes()
            second = process(source, output, manifest, expected_rows=None)
            self.assertEqual(first_bytes, output.read_bytes())
            self.assertEqual(first["output_sha256_bytes"], second["output_sha256_bytes"])
            self.assertEqual(second["rows_preserved"], 1)

    def test_missing_input_fails_controlled(self):
        with self.assertRaises(FileNotFoundError):
            read_source(Path("missing.csv"), expected_rows=None)

    def test_wrong_columns_fail(self):
        frame = sample_frame().drop(columns=["Weight"])
        with self.assertRaises(DataValidationError):
            from src.unit_ii import validate_frame
            validate_frame(frame, expected_rows=None)

    def test_malformed_row_fails_controlled(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.csv"
            source.write_text(",".join(EXPECTED_COLUMNS) + "\n" + ",".join(["x"] * 5), encoding="utf-8")
            with self.assertRaises(DataValidationError):
                read_source(source, expected_rows=None)

    def test_corrupt_category_fails(self):
        frame = sample_frame()
        frame.loc[0, "NObeyesdad"] = "Invented_Class"
        with self.assertRaises(DataValidationError):
            from src.unit_ii import validate_frame
            validate_frame(frame, expected_rows=None)

    def test_full_source_schema_types_and_duplicate_count(self):
        root = Path(__file__).resolve().parents[2]
        source = root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
        original_hash = sha256(source)
        frame = read_source(source)
        self.assertEqual(sha256(source), original_hash)
        self.assertEqual(frame.shape, (2111, 17))
        self.assertEqual(frame.columns.tolist(), EXPECTED_COLUMNS)
        self.assertEqual(int(frame.duplicated().sum()), 24)
        self.assertEqual(frame["NObeyesdad"].nunique(), 7)

    def test_processed_values_match_source_exactly(self):
        root = Path(__file__).resolve().parents[2]
        source = pd.read_csv(root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv")
        processed = pd.read_csv(root / "data/processed/obesity_unit_ii.csv")
        pd.testing.assert_frame_equal(source, processed, check_exact=True)


if __name__ == "__main__":
    unittest.main()
