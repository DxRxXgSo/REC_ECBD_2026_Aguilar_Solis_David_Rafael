import unittest

import numpy as np

from src.unit_iv import FEATURES, RANDOM_STATE, load_validated_data, score_k


class UnitIVAnalysisTests(unittest.TestCase):
    def test_contract_uses_processed_source_and_excludes_target(self):
        frame, hashes = load_validated_data()
        self.assertEqual(frame.shape, (2111, 17))
        self.assertEqual(frame.duplicated().sum(), 24)
        self.assertNotIn("NObeyesdad", FEATURES)
        self.assertEqual(len(hashes["raw_sha256"]), 64)

    def test_kmeans_selection_scores_are_reproducible(self):
        values = np.array([[0.0, 0.0], [0.1, 0.0], [5.0, 5.0], [5.1, 5.0], [9.0, 0.0], [9.1, 0.1]])
        scores_a, models_a = score_k(values, (2, 3))
        scores_b, models_b = score_k(values, (2, 3))
        self.assertEqual(scores_a["k"].tolist(), [2, 3])
        self.assertTrue(np.allclose(scores_a["silhouette"], scores_b["silhouette"]))
        self.assertTrue(np.array_equal(models_a[2].labels_, models_b[2].labels_))
        self.assertEqual(RANDOM_STATE, 42)


if __name__ == "__main__":
    unittest.main()
