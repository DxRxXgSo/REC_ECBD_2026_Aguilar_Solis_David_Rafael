from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
import unittest
from sklearn.dummy import DummyClassifier

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from unit_iii.data import (DataContractError, EXPECTED_COLUMNS, classification_cv,
                           regression_cv, split_indices, validate_input)
from unit_iii.pipelines import (CLASSIFICATION_A_FEATURES, CLASSIFICATION_B_FEATURES,
                                REGRESSION_FEATURES, make_pipeline, make_preprocessor)


class ExperimentContractTests(unittest.TestCase):
    def test_validated_unit_ii_input_matches_contract(self):
        frame, manifest = validate_input(ROOT)
        self.assertEqual(frame.shape, (2111, 17))
        self.assertEqual(list(frame.columns), EXPECTED_COLUMNS)
        self.assertEqual(frame["NObeyesdad"].nunique(), 7)
        self.assertEqual(frame.duplicated().sum(), 24)
        self.assertTrue(manifest["source_values_equal"])

    def test_duplicate_groups_do_not_cross_reproducible_holdout(self):
        frame, _ = validate_input(ROOT)
        train, test, groups = split_indices(frame)
        train2, test2, _ = split_indices(frame)
        self.assertTrue(np.array_equal(train, train2) and np.array_equal(test, test2))
        self.assertFalse(set(groups[train]).intersection(groups[test]))

    def test_duplicate_groups_do_not_cross_any_training_cv_fold(self):
        frame, _ = validate_input(ROOT)
        train, _, groups = split_indices(frame)
        X, y, fold_groups = frame.iloc[train], frame.iloc[train]["NObeyesdad"], groups[train]
        for splitter in (regression_cv(fold_groups), classification_cv()):
            for fit, validation in splitter.split(X, y, fold_groups):
                self.assertFalse(set(fold_groups[fit]).intersection(fold_groups[validation]))

    def test_predictors_exclude_target_and_label_leakage(self):
        self.assertNotIn("Weight", REGRESSION_FEATURES)
        self.assertNotIn("NObeyesdad", REGRESSION_FEATURES)
        self.assertNotIn("NObeyesdad", CLASSIFICATION_A_FEATURES + CLASSIFICATION_B_FEATURES)
        self.assertTrue({"Height", "Weight"}.issubset(CLASSIFICATION_A_FEATURES))
        self.assertNotIn("Height", CLASSIFICATION_B_FEATURES)
        self.assertNotIn("Weight", CLASSIFICATION_B_FEATURES)

    def test_preprocessor_is_fitted_from_training_only(self):
        train = pd.DataFrame({"Age": [20.0, np.nan, 30.0], "Gender": ["Female", "Male", "Female"]})
        held_out = pd.DataFrame({"Age": [99999.0], "Gender": ["Unknown"]})
        preprocessor = make_preprocessor(train)
        preprocessor.fit(train)
        numeric = preprocessor.named_transformers_["numeric"]
        self.assertEqual(numeric.named_steps["imputer"].statistics_[0], 25.0)
        self.assertEqual(preprocessor.transform(held_out).shape[0], 1)

    def test_pipeline_model_serialization_preserves_predictions(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            X = pd.DataFrame({"Age": [20, 22, 41, 44], "Gender": ["F", "F", "M", "M"]})
            y = np.array(["a", "a", "b", "b"])
            model = make_pipeline(X, DummyClassifier(strategy="most_frequent")).fit(X, y)
            expected = model.predict(X)
            path = Path(directory) / "model.joblib"
            joblib.dump(model, path)
            restored = joblib.load(path)
            self.assertTrue(np.array_equal(restored.predict(X), expected))

    def test_generated_metrics_are_finite_for_each_task(self):
        result_dir = ROOT / "docs/unidad_iii/resultados"
        files = ["regresion_metricas_base.csv", "clasificacion_metricas_base.csv",
                 "optimizacion_metricas_test.csv"]
        for filename in files:
            with self.subTest(filename=filename):
                metrics = pd.read_csv(result_dir / filename).select_dtypes(include=["number"])
                values = metrics.to_numpy(dtype=float)
                self.assertTrue(np.isfinite(values[~np.isnan(values)]).all())

    def test_invalid_input_root_fails_as_controlled_contract_error(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(DataContractError, "Falta el artefacto requerido"):
                validate_input(Path(directory))
