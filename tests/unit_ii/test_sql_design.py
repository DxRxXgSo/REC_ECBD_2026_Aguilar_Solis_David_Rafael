import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "sql"


class DataMartScriptTests(unittest.TestCase):
    def test_schema_has_primary_key_dimension_and_fact_relationship(self):
        database = (SQL / "00_create_database.sql").read_text(encoding="utf-8")
        ddl = (SQL / "01_create_datamart.sql").read_text(encoding="utf-8")
        self.assertIn("DB_ID(N'REC_ECBD_Obesidad_2026') IS NULL", database)
        self.assertIn("CREATE DATABASE [REC_ECBD_Obesidad_2026]", database)
        self.assertIn("USE [REC_ECBD_Obesidad_2026]", database)
        self.assertIn("DM.DimObesityLevel", ddl)
        self.assertIn("DM.FactObesityObservation", ddl)
        self.assertIn("PRIMARY KEY", ddl)
        self.assertIn("FOREIGN KEY", ddl)
        self.assertIn("DM.StgObesityObservation", ddl)
        self.assertIn("Age float NOT NULL", ddl)

    def test_load_is_validated_transactional_and_non_destructive_to_schema(self):
        load = (SQL / "02_load_datamart.sql").read_text(encoding="utf-8")
        self.assertIn("BULK INSERT", load)
        self.assertIn("BULK INSERT #IncomingObesityObservation", load)
        self.assertIn("FIRSTROW = 2", load)
        self.assertIn("TRY_CONVERT", load)
        self.assertIn("TRY_CONVERT(float, s.TUE)", load)
        self.assertNotIn("TRY_CONVERT(decimal(12,6)", load)
        self.assertIn("BEGIN TRANSACTION", load)
        self.assertIn("ROLLBACK TRANSACTION", load)
        self.assertNotIn("DROP TABLE", load.upper())
        self.assertNotIn("TRUNCATE TABLE", load.upper())
        self.assertNotIn("DELETE FROM DM.FACTOBESITYOBSERVATION", load.upper())
        self.assertIn("Staging ya contiene datos distintos", load)

    def test_read_only_validation_and_dashboard_queries_exist(self):
        validation = (SQL / "03_validate_datamart.sql").read_text(encoding="utf-8")
        dashboard = (SQL / "04_dashboard_queries.sql").read_text(encoding="utf-8")
        assertions = (SQL / "05_assert_datamart.sql").read_text(encoding="utf-8")
        self.assertIn("COUNT_BIG", validation)
        self.assertIn("duplicate_source_rows_preserved", validation)
        self.assertIn("orphaned_fact_rows", validation)
        self.assertIn("invalid_numeric_rows", validation)
        self.assertIn("duplicate_rows_preserved", assertions)
        self.assertIn("@fact_count <> 2111", assertions)
        self.assertIn("@fact_class_count <> 7", assertions)
        self.assertIn("GROUP BY", dashboard)
        self.assertIn("AVG(f.Height)", dashboard)
        self.assertIn("AVG(f.NCP)", dashboard)
        self.assertIn("AVG(f.CH2O)", dashboard)
        self.assertIn("AVG(f.TUE)", dashboard)
        self.assertIn("habit_name", dashboard)
        for script in (SQL / "01_create_datamart.sql", SQL / "02_load_datamart.sql", SQL / "03_validate_datamart.sql", SQL / "04_dashboard_queries.sql"):
            self.assertIn("USE [REC_ECBD_Obesidad_2026]", script.read_text(encoding="utf-8"))
        self.assertNotIn("INSERT ", validation.upper())
        self.assertNotIn("DELETE ", dashboard.upper())

    def test_read_only_integrated_verifier_never_runs_load_or_ddl_scripts(self):
        verifier = (ROOT / "src/verify_unit_ii.py").read_text(encoding="utf-8")
        self.assertIn("SQL_READ_ONLY_SCRIPTS", verifier)
        readonly_block = verifier.split("SQL_READ_ONLY_SCRIPTS = (", 1)[1].split(")", 1)[0]
        for script in ("sql/03_validate_datamart.sql", "sql/04_dashboard_queries.sql", "sql/05_assert_datamart.sql"):
            self.assertIn(f'"{script}"', readonly_block)
        for forbidden in ("sql/00_create_database.sql", "sql/01_create_datamart.sql", "sql/02_load_datamart.sql"):
            self.assertNotIn(f'"{forbidden}"', readonly_block)

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
