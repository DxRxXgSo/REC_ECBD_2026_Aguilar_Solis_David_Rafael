import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "sql"


class DataMartScriptTests(unittest.TestCase):
    def test_schema_has_primary_key_dimension_and_fact_relationship(self):
        ddl = (SQL / "01_create_datamart.sql").read_text(encoding="utf-8")
        self.assertIn("DM.DimObesityLevel", ddl)
        self.assertIn("DM.FactObesityObservation", ddl)
        self.assertIn("PRIMARY KEY", ddl)
        self.assertIn("FOREIGN KEY", ddl)
        self.assertIn("DM.StgObesityObservation", ddl)

    def test_load_is_validated_transactional_and_non_destructive_to_schema(self):
        load = (SQL / "02_load_datamart.sql").read_text(encoding="utf-8")
        self.assertIn("BULK INSERT", load)
        self.assertIn("FIRSTROW = 2", load)
        self.assertIn("TRY_CONVERT", load)
        self.assertIn("BEGIN TRANSACTION", load)
        self.assertIn("ROLLBACK TRANSACTION", load)
        self.assertNotIn("DROP TABLE", load.upper())

    def test_read_only_validation_and_dashboard_queries_exist(self):
        validation = (SQL / "03_validate_datamart.sql").read_text(encoding="utf-8")
        dashboard = (SQL / "04_dashboard_queries.sql").read_text(encoding="utf-8")
        self.assertIn("COUNT_BIG", validation)
        self.assertIn("GROUP BY", dashboard)
        self.assertNotIn("INSERT ", validation.upper())
        self.assertNotIn("DELETE ", dashboard.upper())

    def test_dictionary_covers_all_source_fields_and_documents_source(self):
        expected = [
            "Gender", "Age", "Height", "Weight", "family_history_with_overweight",
            "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF",
            "TUE", "CALC", "MTRANS", "NObeyesdad",
        ]
        dictionary = (ROOT / "docs/unidad_ii/diccionario_datos.md").read_text(encoding="utf-8")
        for variable in expected:
            self.assertIn(f"`{variable}`", dictionary)
        self.assertIn("10.24432/C5H31Z", dictionary)
        self.assertIn("sintétic", dictionary.lower())


if __name__ == "__main__":
    unittest.main()
