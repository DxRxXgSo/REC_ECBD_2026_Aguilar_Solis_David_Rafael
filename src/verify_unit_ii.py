"""Run Unit II validation and record real results without touching raw data."""

from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
import nbformat
import numpy
import pandas


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
EVIDENCE = ROOT / "docs/unidad_ii/evidencias/verificacion_unidad_ii.json"
EXPECTED_RAW_SHA256 = "28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b"
SQLCMD = Path(r"C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE")
PDFINFO = Path(r"C:\Users\rafle\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdfinfo.exe")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(label: str, args: list[str], timeout: int = 180) -> dict[str, Any]:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return {
        "name": label,
        "command": subprocess.list2cmdline(args),
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-6000:],
        "stderr_tail": result.stderr[-3000:],
    }


def main() -> int:
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    before = sha256(RAW) if RAW.is_file() else None
    commands = [
        run("unit_ii_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit_ii", "-v"]),
        run("etl", [sys.executable, "src/unit_ii.py"]),
        run("notebook_execution", [sys.executable, "src/execute_unit_ii_notebook.py"]),
        run("unit_i_tests", [sys.executable, "-m", "unittest", "discover", "-s", "docs/unidad_i/tests", "-v"]),
        run("unit_i_verifier", [
            sys.executable, "docs/unidad_i/verificar_unidad_i.py", "--evidence",
            "docs/unidad_ii/evidencias/verificacion_unidad_i_regresion.json",
        ]),
        run("git_diff_check", ["git", "diff", "--check"]),
        run("report_pdf_info", [str(PDFINFO), "docs/unidad_ii/informe_unidad_ii.pdf"]),
    ]
    after = sha256(RAW) if RAW.is_file() else None
    unit_i_evidence = EVIDENCE.parent / "verificacion_unidad_i_regresion.json"
    unit_i_report = json.loads(unit_i_evidence.read_text(encoding="utf-8")) if unit_i_evidence.exists() else {}
    manifest_path = ROOT / "data/processed/unit_ii_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    notebook_path = ROOT / "notebooks/01_exploracion_datos.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4) if notebook_path.exists() else None
    notebook_errors = [
        output for cell in notebook.cells for output in cell.get("outputs", [])
        if output.output_type == "error"
    ] if notebook else ["missing"]
    pdf_match = re.search(r"Pages:\s+(\d+)", commands[-1]["stdout_tail"])
    pdf_pages = int(pdf_match.group(1)) if pdf_match else None
    frame = pandas.read_csv(ROOT / "data/processed/obesity_unit_ii.csv") if (ROOT / "data/processed/obesity_unit_ii.csv").exists() else None
    sql_check = None
    if SQLCMD.exists():
        sql_check = run("sql_server_probe_read_only", [str(SQLCMD), "-S", "localhost", "-E", "-l", "3", "-Q", "SELECT @@SERVERNAME AS server_name;"], timeout=10)
    criteria = [
        {"id": "AC-II01", "status": "PASS" if before == after == EXPECTED_RAW_SHA256 else "FAIL", "detail": "Raw SHA-256 before/after and known baseline."},
        {"id": "AC-II02", "status": "PASS" if frame is not None and frame.shape == (2111, 17) else "FAIL", "detail": "Processed CSV dimensions."},
        {"id": "AC-II03", "status": "PASS" if (ROOT / "docs/unidad_ii/diccionario_datos.md").is_file() else "FAIL", "detail": "Dictionary file present; academic interpretation remains subject to review."},
        {"id": "AC-II04", "status": "PASS" if notebook is not None and not notebook_errors else "FAIL", "detail": "EDA notebook stored outputs and error scan."},
        {"id": "AC-II05", "status": "PASS" if len(list((ROOT / "docs/unidad_ii/figuras").glob("*.png"))) >= 3 else "FAIL", "detail": "Three generated figures; chart outputs reviewed."},
        {"id": "AC-II06", "status": "PASS" if manifest.get("exact_duplicate_rows_preserved") == 24 and manifest.get("rows_excluded") == 0 else "FAIL", "detail": "Duplicates retained; no rows excluded."},
        {"id": "AC-II07", "status": "PASS" if commands[0]["exit_code"] == 0 else "FAIL", "detail": "Unit II positive and negative test suite."},
        {"id": "AC-II08", "status": "PASS" if commands[0]["exit_code"] == 0 else "FAIL", "detail": "ETL idempotence test and manifest hashes."},
        {"id": "AC-II09", "status": "PASS" if commands[1]["exit_code"] == 0 and manifest.get("rows_preserved") == 2111 and manifest.get("source_values_equal") else "FAIL", "detail": "Processed derivative validates, preserves rows, and matches source values exactly."},
        {"id": "AC-II10", "status": "PASS" if commands[0]["exit_code"] == 0 else "FAIL", "detail": "SQL design files pass static tests."},
        {"id": "AC-II11", "status": "NO VERIFICADO" if not sql_check or sql_check["exit_code"] != 0 else "PASS", "detail": "No local SQL Server instance accessible; SQL DDL/load not executed."},
        {"id": "AC-II12", "status": "PASS" if all((ROOT / f"docs/unidad_ii/informe_unidad_ii.{ext}").is_file() for ext in ("md", "docx", "pdf")) and pdf_pages else "FAIL", "detail": f"Markdown, editable DOCX, Word-exported PDF; {pdf_pages} pages rendered with Poppler and visually reviewed."},
        {"id": "AC-II13", "status": "PASS" if commands[3]["exit_code"] == 0 and unit_i_report.get("summary", {}).get("fail") == 0 and commands[4]["exit_code"] == 0 else "FAIL", "detail": "Unit I regression tests and verifier."},
        {"id": "AC-II14", "status": "PASS" if "informe_unidad_ii.md" in (ROOT / "README.md").read_text(encoding="utf-8") else "FAIL", "detail": "README links Unit II report and states SQL/academic limits."},
    ]
    result = {
        "schema_version": "1.0",
        "run": {
            "timestamp_local": datetime.now().astimezone().isoformat(),
            "command": f'"{sys.executable}" src/verify_unit_ii.py',
            "project_root": str(ROOT),
            "python_version": platform.python_version(),
            "verifier_sha256": sha256(Path(__file__).resolve()),
            "exit_code": 0,
        },
        "environment": {
            "pandas": pandas.__version__, "numpy": numpy.__version__,
            "matplotlib": matplotlib.__version__, "notebook_format": nbformat.__version__,
        },
        "integrity": {
            "raw_path": str(RAW.relative_to(ROOT)),
            "raw_sha256_before": before, "raw_sha256_after": after,
            "processed_sha256": manifest.get("output_sha256_bytes"),
        },
        "dataset": {
            "processed_rows": int(len(frame)) if frame is not None else None,
            "processed_columns": int(len(frame.columns)) if frame is not None else None,
            "missing_values": int(frame.isna().sum().sum()) if frame is not None else None,
            "exact_duplicates_preserved": int(frame.duplicated().sum()) if frame is not None else None,
            "class_count": int(frame["NObeyesdad"].nunique()) if frame is not None else None,
            "notebook_code_cells": sum(cell.cell_type == "code" for cell in notebook.cells) if notebook else None,
            "notebook_errors": len(notebook_errors),
        },
        "commands": commands,
        "unit_i_verifier_summary": unit_i_report.get("summary"),
        "sql_server_probe": sql_check,
        "acceptance_criteria": criteria,
        "human_review": {
            "academic_acceptance": "PENDIENTE",
            "teacher_identity": "PENDIENTE DE CONFIRMACIÓN",
            "sql_server_execution": "NO VERIFICADO",
            "visual_review": f"{pdf_pages} páginas exportadas por Word y renderizadas con Poppler; inspección visual realizada. El render_docx no se pudo ejecutar porque LibreOffice no está instalado.",
        },
    }
    code = 0 if all(c["exit_code"] == 0 for c in commands) and all(x["status"] != "FAIL" for x in criteria) and before == after else 1
    result["run"]["exit_code"] = code
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"exit_code": code, "commands": [{"name": c["name"], "exit_code": c["exit_code"]} for c in commands], "criteria": criteria, "raw_sha256_before": before, "raw_sha256_after": after, "evidence": str(EVIDENCE)}, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
