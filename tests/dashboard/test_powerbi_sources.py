import unittest
from pathlib import Path

from src.powerbi_sources import load_dashboard_sources, validate_dashboard_sources


ROOT = Path(__file__).resolve().parents[2]


class PowerBISourceContractTests(unittest.TestCase):
    def test_existing_sources_meet_dashboard_contract(self):
        result = validate_dashboard_sources(ROOT)
        self.assertEqual(result["raw_rows"], 2111)
        self.assertEqual(result["raw_columns"], 17)
        self.assertEqual(result["dashboard_fact_rows"], 2111)
        self.assertEqual(result["exact_duplicate_rows"], 24)
        self.assertEqual(result["cluster_count"], 9)
        self.assertEqual(result["metric_rows"], 5)
        self.assertEqual(
            result["obesity_classes"],
            [
                "Insufficient_Weight", "Normal_Weight", "Obesity_Type_I",
                "Obesity_Type_II", "Obesity_Type_III", "Overweight_Level_I",
                "Overweight_Level_II",
            ],
        )

    def test_row_level_cluster_merge_is_one_to_one(self):
        sources = load_dashboard_sources(ROOT)
        fact = sources["fact"]
        self.assertEqual(fact["row_index"].nunique(), 2111)
        self.assertEqual(fact["cluster"].isna().sum(), 0)
        self.assertEqual(len(fact), 2111)
        metrics = sources["metrics"]
        self.assertEqual(len(metrics[metrics["task"] == "regression"]), 1)
        self.assertEqual(
            set(metrics.loc[metrics["task"] == "classification", "scenario"]),
            {"A", "B"},
        )

    def test_power_query_files_reference_the_expected_sources(self):
        query_dir = ROOT / "dashboard/powerbi/queries"
        expected = {
            "FactDashboard.m": ["obesity_unit_ii.csv", "unidad_iv_cluster_assignments.csv", "ValidateNoMissing"],
            "DimObesityLevel.m": ["SqlDatabase", "DM.DimObesityLevel"],
            "ModelMetrics.m": ["optimizacion_metricas_test.csv"],
            "ClusterProfile.m": ["perfil_numerico_clusters.csv"],
            "PcaVariance.m": ["varianza_pca.csv"],
        }
        for name, fragments in expected.items():
            with self.subTest(query=name):
                text = (query_dir / name).read_text(encoding="utf-8")
                for fragment in fragments:
                    self.assertIn(fragment, text)
        parameters = (ROOT / "dashboard/ECBD_Integrador_2026/ECBD_Integrador_2026.SemanticModel/definition/expressions.tmdl").read_text(encoding="utf-8")
        for parameter in ["ProjectRoot", "SqlInstance", "SqlDatabase", "localhost\\SQLEXPRESS", "REC_ECBD_Obesidad_2026"]:
            self.assertIn(parameter, parameters)
        dax = (ROOT / "dashboard/powerbi/measures.dax").read_text(encoding="utf-8")
        for measure in ["Observaciones =", "Accuracy =", "Precision macro =", "Recall macro =", "F1 macro =", "MAE =", "RMSE =", "R cuadrada ="]:
            self.assertIn(measure, dax)


if __name__ == "__main__":
    unittest.main()
