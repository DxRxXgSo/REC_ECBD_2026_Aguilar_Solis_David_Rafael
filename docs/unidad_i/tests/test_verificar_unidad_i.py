"""Controlled regression tests for the Unit I verifier; all fixtures are temporary."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
VERIFIER = REPO / "docs/unidad_i/verificar_unidad_i.py"
SOURCE_FILES = (
    "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv",
    "notebooks/00_revision_inicial_dataset.ipynb",
    "docs/sdd/00_reglas_globales.md",
    "docs/unidad_i/planeacion_unidad_i.docx",
    "docs/unidad_i/evidencias/verificacion_unidad_i.json",
)
REFERENCE_TEXT = " ".join((
    "https://doi.org/10.24432/C5H31Z",
    "https://doi.org/10.1016/j.dib.2019.104344",
    "https://doi.org/10.6028/NIST.SP.1500-1r1",
    "https://kddlab.com/files/CRISPWP-0800.pdf",
))


class VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="sdd_u1_verifier_test_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        for rel in SOURCE_FILES:
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / rel, target)
        (self.root / "README.md").write_text(
            "Proyecto de análisis. Periodo: 23 de septiembre al 20 de noviembre de 2026. "
            "Entrega Unidad I: 2 de octubre de 2026. Véase `docs/unidad_i/planeacion_unidad_i.md`.\n",
            encoding="utf-8",
        )
        (self.root / "docs/unidad_i/planeacion_unidad_i.md").write_text(
            "Planeación. Entrega Unidad I: 2 de octubre de 2026. Unidad V y cierre: 20 de noviembre de 2026. "
            "Actividad 0: 25 y 28 de septiembre de 2026. " + REFERENCE_TEXT + "\n",
            encoding="utf-8",
        )

    def run_verifier(self) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        evidence = Path(self.temp.name) / "evidence.json"
        result = subprocess.run(
            [sys.executable, str(VERIFIER), "--project-root", str(self.root), "--evidence", str(evidence)],
            text=True, encoding="utf-8", capture_output=True, check=False,
        )
        report = json.loads(evidence.read_text(encoding="utf-8"))
        return result, report

    def assert_controlled_failure(self, check_name: str) -> None:
        result, report = self.run_verifier()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        statuses = {item["check"]: item["status"] for item in report["checks"]}
        self.assertEqual(statuses[check_name], "FAIL")
        self.assertIn("exit_code", report["run"])

    def test_positive_fixture(self) -> None:
        result, report = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report["summary"]["fail"], 0)
        self.assertEqual(report["run"]["exit_code"], 0)
        self.assertTrue(report["run"]["verifier_sha256"])
        self.assertTrue(report["run"]["command"])
        self.assertTrue(report["run"]["timestamp_local"])
        self.assertTrue(any(item["status"] == "NO VERIFICADO" for item in report["acceptance_criteria"]))
        csv_hash = next(item for item in report["checks"] if item["check"] == "csv_content_hash")
        self.assertEqual(csv_hash["status"], "PASS")
        self.assertNotEqual(csv_hash["details"]["sha256_local_bytes"], csv_hash["details"]["sha256_after_crlf_to_lf"])

    def test_lf_variant_preserves_canonical_hash(self) -> None:
        path = self.root / SOURCE_FILES[0]
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        result, report = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        csv_hash = next(item for item in report["checks"] if item["check"] == "csv_content_hash")
        self.assertEqual(csv_hash["status"], "PASS")
        self.assertEqual(csv_hash["details"]["sha256_after_crlf_to_lf"], csv_hash["details"]["expected_canonical_sha256"])

    def test_csv_missing_is_controlled(self) -> None:
        (self.root / SOURCE_FILES[0]).unlink()
        self.assert_controlled_failure("csv_readable")

    def test_incorrect_columns_fail(self) -> None:
        path = self.root / SOURCE_FILES[0]
        data = path.read_bytes()
        first_line, rest = data.split(b"\n", 1)
        path.write_bytes(first_line.rsplit(b",", 1)[0] + b"\n" + rest)
        self.assert_controlled_failure("csv_header")

    def test_malformed_csv_syntax_fails(self) -> None:
        path = self.root / SOURCE_FILES[0]
        with path.open("ab") as stream:
            stream.write(b'\ninvalid,"unterminated\n')
        self.assert_controlled_failure("csv_parse")

    def test_malformed_row_width_fails(self) -> None:
        path = self.root / SOURCE_FILES[0]
        with path.open("a", encoding="utf-8", newline="") as stream:
            stream.write("\nshort,row\n")
        self.assert_controlled_failure("csv_row_width")

    def test_outdated_readme_fails(self) -> None:
        (self.root / "README.md").write_text(
            "Entrega Unidad I: 3 de octubre de 2026. Fecha final del proyecto: 21 de noviembre de 2026.\n",
            encoding="utf-8",
        )
        self.assert_controlled_failure("readme_calendar_coherence")

    def test_unverifiable_calendar_claim_fails(self) -> None:
        path = self.root / "README.md"
        path.write_text(path.read_text(encoding="utf-8") + "Cronograma oficial pendiente de confirmar.\n", encoding="utf-8")
        self.assert_controlled_failure("readme_calendar_coherence")

    def test_invalid_notebook_fails_without_exception(self) -> None:
        (self.root / SOURCE_FILES[1]).write_text('{"cells": [}', encoding="utf-8")
        self.assert_controlled_failure("notebook_structure")

    def test_readme_missing_is_controlled(self) -> None:
        (self.root / "README.md").unlink()
        self.assert_controlled_failure("readme_readable")

    def test_corrupt_docx_is_controlled(self) -> None:
        (self.root / "docs/unidad_i/planeacion_unidad_i.docx").write_bytes(b"not a docx archive")
        self.assert_controlled_failure("docx_container_readable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
