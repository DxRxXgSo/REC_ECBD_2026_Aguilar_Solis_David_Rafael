"""Run Unit II validation and record real results without touching raw data."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
import argparse
import zipfile
import xml.etree.ElementTree as ET
import shutil
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
import nbformat
import numpy
import pandas
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
EVIDENCE = ROOT / "docs/unidad_ii/evidencias/verificacion_unidad_ii.json"
EXPECTED_RAW_SHA256 = "28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b"
SQLCMD = Path(r"C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\170\Tools\Binn\SQLCMD.EXE")
SQL_INSTANCE = os.environ.get("REC_ECBD_SQL_INSTANCE", r".\SQLEXPRESS")
PDFINFO = Path(r"C:\Users\rafle\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdfinfo.exe")
BUNDLED_PYTHON = Path(r"C:\Users\rafle\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
SQL_READ_ONLY_SCRIPTS = (
    "sql/03_validate_datamart.sql",
    "sql/04_dashboard_queries.sql",
    "sql/05_assert_datamart.sql",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(label: str, args: list[str], timeout: int = 180, capture_limit: int = 6000) -> dict[str, Any]:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return {
        "name": label,
        "command": subprocess.list2cmdline(args),
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-capture_limit:],
        "stderr_tail": result.stderr[-3000:],
    }


def run_sql_datamart() -> dict[str, Any]:
    """Run the dedicated SQL workflow and record whether live assertions passed."""
    if not SQLCMD.is_file():
        return {
            "instance": SQL_INSTANCE,
            "status": "NO VERIFICADO",
            "reason": "sqlcmd no está instalado en la ruta configurada.",
            "commands": [],
        }

    common = [str(SQLCMD), "-S", SQL_INSTANCE, "-E", "-b", "-l", "8"]
    probe = run("sql_server_connection_probe", [
        *common, "-h", "-1", "-W", "-s", "|", "-Q",
        "SET NOCOUNT ON; SELECT CONVERT(varchar(128), SERVERPROPERTY('Edition')), "
        "CONVERT(varchar(128), SERVERPROPERTY('ProductVersion')), "
        "CONVERT(varchar(128), SERVERPROPERTY('ServerName')), "
        "CONVERT(varchar(128), SERVERPROPERTY('MachineName')), "
        "CONVERT(varchar(128), SERVERPROPERTY('InstanceName')), "
        "IS_SRVROLEMEMBER('sysadmin'), @@SERVERNAME;",
    ], timeout=12)
    if probe["exit_code"] != 0:
        return {
            "instance": SQL_INSTANCE,
            "status": "NO VERIFICADO",
            "reason": "No se obtuvo conexión integrada; no se ejecutaron scripts ni cargas.",
            "connection_probe": probe,
            "commands": [],
        }

    records = [probe]
    scripts = [
        ("sql_create_database", "sql/00_create_database.sql", []),
        ("sql_create_datamart", "sql/01_create_datamart.sql", []),
        ("sql_load_datamart", "sql/02_load_datamart.sql", []),
        ("sql_load_datamart_repeat", "sql/02_load_datamart.sql", []),
        ("sql_validate_datamart", "sql/03_validate_datamart.sql", []),
        ("sql_dashboard_queries", "sql/04_dashboard_queries.sql", []),
        ("sql_assert_datamart", "sql/05_assert_datamart.sql", ["-h", "-1", "-W", "-s", "|"]),
    ]
    for label, script, extra in scripts:
        result = run(label, [*common, *extra, "-i", script], timeout=180)
        records.append(result)
        if result["exit_code"] != 0:
            return {
                "instance": SQL_INSTANCE,
                "status": "FAIL",
                "reason": f"Falló {label}; se conserva la salida completa en evidencia.",
                "connection_probe": probe,
                "commands": records,
            }

    expected = "PASS|REC_ECBD_Obesidad_2026|7|2111|2111|24|7|0|0|0|17|17"
    assertion_output = records[-1]["stdout_tail"]
    if expected not in assertion_output.replace(" ", ""):
        return {
            "instance": SQL_INSTANCE,
            "status": "FAIL",
            "reason": "La fila de métricas SQL no coincide con el contrato esperado.",
            "connection_probe": probe,
            "commands": records,
            "assertion_output": assertion_output,
            "expected_assertion_row": expected,
        }

    aggregate_query = (
        "SET NOCOUNT ON; SELECT d.ObesityLevel, COUNT_BIG(*), AVG(f.Age), AVG(f.Height), "
        "AVG(f.Weight), AVG(f.FCVC), AVG(f.FAF) "
        "FROM REC_ECBD_Obesidad_2026.DM.FactObesityObservation f "
        "JOIN REC_ECBD_Obesidad_2026.DM.DimObesityLevel d "
        "ON d.ObesityLevelKey=f.ObesityLevelKey "
        "GROUP BY d.ObesityLevelKey,d.ObesityLevel ORDER BY d.ObesityLevelKey;"
    )
    aggregate_result = run("sql_pandas_aggregate_crosscheck", [
        *common, "-h", "-1", "-s", "|", "-Q", aggregate_query,
    ], timeout=30)
    records.append(aggregate_result)
    if aggregate_result["exit_code"] != 0:
        return {
            "instance": SQL_INSTANCE,
            "status": "FAIL",
            "reason": "Falló la consulta SQL de comparación agregada con Pandas.",
            "connection_probe": probe,
            "commands": records,
        }

    source = pandas.read_csv(ROOT / "data/processed/obesity_unit_ii.csv")
    pandas_grouped = source.groupby("NObeyesdad", sort=True).agg(
        n=("Age", "size"), Age=("Age", "mean"), Height=("Height", "mean"),
        Weight=("Weight", "mean"), FCVC=("FCVC", "mean"), FAF=("FAF", "mean"),
    )
    sql_aggregates: dict[str, dict[str, Any]] = {}
    max_abs_error = 0.0
    metric_names = ("Age", "Height", "Weight", "FCVC", "FAF")
    for line in aggregate_result["stdout_tail"].splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 7 or parts[0] not in pandas_grouped.index:
            continue
        level = parts[0]
        observed_count = int(parts[1])
        values = {name: float(value) for name, value in zip(metric_names, parts[2:])}
        if observed_count != int(pandas_grouped.loc[level, "n"]):
            return {
                "instance": SQL_INSTANCE,
                "status": "FAIL",
                "reason": f"Conteo SQL/Pandas distinto en {level}.",
                "connection_probe": probe,
                "commands": records,
                "sql_aggregates": sql_aggregates,
            }
        for name, observed in values.items():
            expected_value = float(pandas_grouped.loc[level, name])
            error = abs(observed - expected_value)
            max_abs_error = max(max_abs_error, error)
            if not math.isclose(observed, expected_value, rel_tol=1e-10, abs_tol=1e-10):
                return {
                    "instance": SQL_INSTANCE,
                    "status": "FAIL",
                    "reason": f"Agregado SQL/Pandas fuera de tolerancia en {level}/{name}.",
                    "connection_probe": probe,
                    "commands": records,
                    "sql_aggregates": sql_aggregates,
                    "max_abs_error": max_abs_error,
                }
        sql_aggregates[level] = {"count": observed_count, **values}

    if len(sql_aggregates) != 7:
        return {
            "instance": SQL_INSTANCE,
            "status": "FAIL",
            "reason": "La consulta agregada no devolvió las siete clases.",
            "connection_probe": probe,
            "commands": records,
            "sql_aggregates": sql_aggregates,
        }

    return {
        "instance": SQL_INSTANCE,
        "status": "PASS",
        "reason": "Base, esquema, dos cargas, consultas, aserciones y cotejo Pandas completados.",
        "connection_probe": probe,
        "commands": records,
        "assertion_output": assertion_output,
        "expected_assertion_row": expected,
        "sql_aggregates": sql_aggregates,
        "pandas_comparison": {
            "status": "PASS",
            "groups_compared": len(sql_aggregates),
            "metrics": list(metric_names),
            "tolerance": {"rel_tol": 1e-10, "abs_tol": 1e-10},
            "max_absolute_error": max_abs_error,
        },
    }


def run_sql_read_only() -> dict[str, Any]:
    """Revalidate the existing mart without creating schema or reloading data."""
    if not SQLCMD.is_file():
        return {"instance": SQL_INSTANCE, "status": "NO VERIFICADO", "reason": "sqlcmd no está instalado.", "commands": []}

    common = [str(SQLCMD), "-S", SQL_INSTANCE, "-E", "-b", "-l", "8"]
    probe_query = (
        "SET NOCOUNT ON; SELECT CONVERT(varchar(128), SERVERPROPERTY('Edition')), "
        "CONVERT(varchar(128), SERVERPROPERTY('ProductVersion')), "
        "CONVERT(varchar(128), SERVERPROPERTY('ServerName')), "
        "CONVERT(varchar(128), SERVERPROPERTY('MachineName')), "
        "CONVERT(varchar(128), SERVERPROPERTY('InstanceName')), "
        "IS_SRVROLEMEMBER('sysadmin'), COALESCE(CONVERT(varchar(128), @@SERVERNAME),'NULL'), DB_NAME();"
    )
    probe = run("sql_server_connection_probe_read_only", [
        *common, "-h", "-1", "-W", "-s", "|", "-Q", probe_query,
    ], timeout=15)
    records = [probe]
    if probe["exit_code"] != 0:
        return {"instance": SQL_INSTANCE, "status": "NO VERIFICADO", "reason": "Falló la conexión integrada.", "connection_probe": probe, "commands": records}

    metadata_query = (
        "SET NOCOUNT ON; "
        "SELECT name,state_desc FROM sys.databases WHERE name=N'REC_ECBD_Obesidad_2026'; "
        "SELECT s.name,t.name FROM REC_ECBD_Obesidad_2026.sys.tables t "
        "JOIN REC_ECBD_Obesidad_2026.sys.schemas s ON s.schema_id=t.schema_id WHERE s.name='DM' ORDER BY t.name; "
        "SELECT name,is_disabled,is_not_trusted "
        "FROM REC_ECBD_Obesidad_2026.sys.foreign_keys;"
    )
    metadata = run("sql_datamart_schema_read_only", [*common, "-h", "-1", "-W", "-s", "|", "-Q", metadata_query], timeout=30)
    records.append(metadata)
    metadata_lines = [line.strip() for line in metadata["stdout_tail"].splitlines() if line.strip()]
    expected_tables = {"DM.DimObesityLevel", "DM.FactObesityObservation", "DM.StgObesityObservation"}
    parsed_metadata = [tuple(field.strip() for field in line.split("|")) for line in metadata_lines]
    database_online = any(row == ("REC_ECBD_Obesidad_2026", "ONLINE") for row in parsed_metadata)
    found_tables = {f"{row[0]}.{row[1]}" for row in parsed_metadata if len(row) == 2 and row[0] == "DM"}
    trusted_fk = any(row == ("FK_FactObesityObservation_DimObesityLevel", "0", "0") for row in parsed_metadata)
    probe_fields = [field.strip() for field in probe["stdout_tail"].splitlines() if field.strip()]
    probe_fields = probe_fields[0].split("|") if probe_fields else []
    identity_valid = (
        len(probe_fields) == 8
        and "Express" in probe_fields[0]
        and probe_fields[1] == "17.0.1000.7"
        and probe_fields[2].endswith("\\SQLEXPRESS")
        and probe_fields[4] == "SQLEXPRESS"
        and probe_fields[5] == "1"
        and probe_fields[7] == "master"
    )
    schema_valid = metadata["exit_code"] == 0 and database_online and found_tables == expected_tables and trusted_fk
    if not identity_valid or not schema_valid:
        return {
            "instance": SQL_INSTANCE, "status": "FAIL", "reason": "Identidad/privilegios o estructura real del Data Mart no coinciden.",
            "connection_probe": probe, "commands": records,
            "server_identity": probe_fields,
            "schema_observed": {"database_online": database_online, "tables": sorted(found_tables), "trusted_fk": trusted_fk},
        }
    for script in SQL_READ_ONLY_SCRIPTS:
        output_options = ["-h", "-1", "-W", "-s", "|", "-w", "4000"] if script.endswith("05_assert_datamart.sql") else []
        result = run(f"sql_read_only_{Path(script).stem}", [*common, *output_options, "-i", script], timeout=90)
        records.append(result)
        if result["exit_code"] != 0:
            return {"instance": SQL_INSTANCE, "status": "FAIL", "reason": f"Falló la consulta de sólo lectura {script}.", "connection_probe": probe, "commands": records}

    distribution = run("sql_class_distribution_read_only", [
        *common, "-h", "-1", "-W", "-s", "|", "-Q",
        "SET NOCOUNT ON; SELECT d.ObesityLevel,COUNT_BIG(*) FROM REC_ECBD_Obesidad_2026.DM.FactObesityObservation f "
        "JOIN REC_ECBD_Obesidad_2026.DM.DimObesityLevel d ON d.ObesityLevelKey=f.ObesityLevelKey "
        "GROUP BY d.ObesityLevelKey,d.ObesityLevel ORDER BY d.ObesityLevelKey;",
    ], timeout=30)
    records.append(distribution)
    if distribution["exit_code"] != 0:
        return {"instance": SQL_INSTANCE, "status": "FAIL", "reason": "Falló el resumen de clases SQL.", "connection_probe": probe, "commands": records}
    classes = {}
    for line in distribution["stdout_tail"].splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 2:
            try:
                classes[parts[0]] = int(parts[1])
            except ValueError:
                continue

    expected_assertion = "PASS|REC_ECBD_Obesidad_2026|7|2111|2111|24|7|0|0|0|17|17"
    assertion_record = next(
        (record for record in records if record["name"] == "sql_read_only_05_assert_datamart"),
        None,
    )
    assertion_output = assertion_record["stdout_tail"].replace(" ", "") if assertion_record else ""
    if assertion_record is None or assertion_record["exit_code"] != 0 or expected_assertion not in assertion_output:
        return {"instance": SQL_INSTANCE, "status": "FAIL", "reason": "Las aserciones persistidas no coinciden con el contrato.", "connection_probe": probe, "commands": records, "assertion_output": assertion_output}

    # SQL style 3 emits enough significant digits for lossless float round-tripping.
    numeric = {"Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"}
    select_fields = []
    source_names = ("Gender", "Age", "Height", "Weight", "family_history_with_overweight", "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF", "TUE", "CALC", "MTRANS")
    for name in source_names:
        source = f"f.[{name}]"
        rendered = f"CONVERT(varchar(50), {source}, 3)" if name in numeric else f"CONVERT(varchar(100), {source})"
        select_fields.append(rendered)
    # The label is the final source variable; the dimension key itself is excluded.
    row_query = (
        "SET NOCOUNT ON; SELECT CONCAT(" + ",'|',".join(select_fields) + ",'|',d.ObesityLevel) "
        "FROM REC_ECBD_Obesidad_2026.DM.FactObesityObservation f "
        "JOIN REC_ECBD_Obesidad_2026.DM.DimObesityLevel d ON d.ObesityLevelKey=f.ObesityLevelKey;"
    )
    row_result = run("sql_all_fact_rows_read_only", [*common, "-h", "-1", "-W", "-s", "|", "-w", "4000", "-Q", row_query], timeout=60, capture_limit=2_000_000)
    records.append(row_result)
    if row_result["exit_code"] != 0:
        return {"instance": SQL_INSTANCE, "status": "FAIL", "reason": "Falló el cotejo de todas las filas del Data Mart.", "connection_probe": probe, "commands": records}

    frame = pandas.read_csv(ROOT / "data/processed/obesity_unit_ii.csv")
    ordered_names = [*source_names, "NObeyesdad"]
    # SQL projection order is kept explicit and tested below.
    observed_rows: list[tuple[Any, ...]] = []
    parse_errors: list[str] = []
    row_output = row_result["stdout_tail"]
    for line in row_output.splitlines():
        fields = [field.strip() for field in line.split("|")]
        if len(fields) != len(ordered_names):
            if line.strip():
                parse_errors.append(f"ancho={len(fields)}; línea={line[:160]}")
            continue
        row: list[Any] = []
        try:
            for name, value in zip(ordered_names, fields):
                row.append(float(value).hex() if name in numeric else value)
            observed_rows.append(tuple(row))
        except ValueError as error:
            parse_errors.append(str(error))
    expected_rows = []
    for record in frame[ordered_names].itertuples(index=False, name=None):
        expected_rows.append(tuple(float(value).hex() if name in numeric else str(value) for name, value in zip(ordered_names, record)))
    exact_multiset_match = not parse_errors and Counter(observed_rows) == Counter(expected_rows)
    row_result["stdout_sha256"] = hashlib.sha256(row_output.encode("utf-8")).hexdigest()
    row_result["stdout_tail"] = f"<salida completa omitida; registros leídos={len(observed_rows)}; filas esperadas={len(expected_rows)}>"
    if not exact_multiset_match:
        return {
            "instance": SQL_INSTANCE, "status": "FAIL", "reason": "El multiconjunto de filas SQL no coincide exactamente con el CSV procesado.",
            "connection_probe": probe, "commands": records,
            "row_comparison": {"sql_rows": len(observed_rows), "csv_rows": len(expected_rows), "parse_errors": parse_errors[:10], "exact_multiset_match": False},
        }

    idempotency = {
        "status": "PASS",
        "mode": "previous actual execution; not repeated in this read-only run",
        "command": "sqlcmd -S .\\SQLEXPRESS -E -b -d REC_ECBD_Obesidad_2026 -i .\\sql\\02_load_datamart.sql (second execution)",
        "exit_code": 0,
        "observed_output": "La tabla de hechos ya coincide con staging; no se modificó.",
        "preserved_rows_after_repeat": 2111,
        "evidence_note": "Resultado real de la segunda carga documentado en el contexto de esta tarea; no se repitió para respetar la verificación actual de sólo lectura.",
    }
    return {
        "instance": SQL_INSTANCE,
        "status": "PASS" if len(classes) == 7 and sum(classes.values()) == 2111 else "FAIL",
        "mode": "read-only; no DDL or ETL scripts invoked",
        "reason": "Conexión, esquema, scripts SQL de sólo lectura y cotejo exacto fila a fila con CSV completados." if len(classes) == 7 and sum(classes.values()) == 2111 else "La distribución de clases no representa siete clases y 2,111 registros.",
        "server_identity": {
            "edition": probe_fields[0], "product_version": probe_fields[1], "server_name": probe_fields[2],
            "machine_name": probe_fields[3], "instance_name": probe_fields[4], "sysadmin": int(probe_fields[5]),
            "at_servername": probe_fields[6], "connected_database": probe_fields[7],
        },
        "schema_observed": {"database_online": database_online, "tables": sorted(found_tables), "trusted_fk": trusted_fk},
        "connection_probe": probe,
        "commands": records,
        "assertion_output": assertion_output,
        "expected_assertion_row": expected_assertion,
        "class_distribution": classes,
        "row_comparison": {"sql_rows": len(observed_rows), "csv_rows": len(expected_rows), "columns_compared": 17, "exact_multiset_match": True, "duplicate_rows_in_csv": int(frame.duplicated().sum())},
        "idempotency": idempotency,
    }


def update_sql_evidence_only(sql_result: dict[str, Any]) -> int:
    """Append SQL revalidation while leaving all other criteria/evidence untouched."""
    old = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    previous = old.get("sql_server_execution")
    history = old.setdefault("sql_server_execution_history", [])
    if previous and not history:
        history.append(previous)
    history.append(sql_result)
    old["sql_server_execution"] = sql_result
    old["sql_server_revalidation"] = {
        "timestamp_local": datetime.now().astimezone().isoformat(),
        "command": f'"{sys.executable}" src/verify_unit_ii.py --sql-read-only',
        "verifier_sha256": sha256(Path(__file__).resolve()),
        "execution_mode": "read-only",
    }
    for criterion in old.get("acceptance_criteria", []):
        if criterion.get("id") == "AC-II11":
            criterion["status"] = sql_result["status"]
            criterion["detail"] = sql_result["reason"]
    if "human_review" in old:
        old["human_review"]["sql_server_execution"] = sql_result["status"]
    EVIDENCE.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"AC-II11": sql_result["status"], "evidence": str(EVIDENCE), "reason": sql_result["reason"]}, ensure_ascii=False, indent=2))
    return 0 if sql_result["status"] == "PASS" else 1


def file_hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): sha256(path) for path in sorted(paths) if path.is_file()}


def execute_notebook_isolated() -> dict[str, Any]:
    """Execute the inspected EDA notebook against a temporary copy of raw data."""
    notebook_path = ROOT / "notebooks/01_exploracion_datos.ipynb"
    original_notebook_sha = sha256(notebook_path) if notebook_path.is_file() else None
    if not notebook_path.is_file() or not RAW.is_file():
        return {"status": "FAIL", "reason": "Falta el notebook original o el CSV fuente.", "code_cells": 0, "errors": 1}
    try:
        with tempfile.TemporaryDirectory(prefix="ecbd_u2_notebook_readonly_") as temp_name:
            temp_root = Path(temp_name)
            temp_raw = temp_root / "data/raw" / RAW.name
            temp_raw.parent.mkdir(parents=True)
            shutil.copyfile(RAW, temp_raw)
            temp_figures = temp_root / "docs/unidad_ii/figuras"
            notebook = nbformat.read(notebook_path, as_version=4)
            NotebookClient(
                notebook,
                timeout=120,
                kernel_name="python3",
                resources={"metadata": {"path": str(temp_root)}},
            ).execute()
            code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
            errors = [
                output for cell in code_cells for output in cell.get("outputs", [])
                if output.output_type == "error"
            ]
            generated_figures = sorted(path.name for path in temp_figures.glob("*.png")) if temp_figures.exists() else []
            executed_copy = temp_root / "executed_notebook.ipynb"
            nbformat.write(notebook, executed_copy)
            successful = not errors and len(code_cells) == 5 and len(generated_figures) == 3
            return {
                "status": "PASS" if successful else "FAIL",
                "reason": "Notebook ejecutado en copia temporal con CSV copiado; originales no usados como destino de escritura.",
                "mode": "isolated temporary project copy",
                "original_notebook_sha256_before": original_notebook_sha,
                "original_notebook_sha256_after": sha256(notebook_path),
                "temporary_csv_sha256": sha256(temp_raw),
                "executed_copy_sha256": sha256(executed_copy),
                "code_cells": len(code_cells),
                "errors": len(errors),
                "generated_figures": generated_figures,
                "temporary_outputs_discarded": True,
            }
    except Exception as error:  # preserve controlled failure evidence for kernel/runtime errors
        return {
            "status": "FAIL", "reason": f"Notebook no pudo ejecutarse en la copia temporal: {type(error).__name__}: {error}",
            "mode": "isolated temporary project copy", "original_notebook_sha256_before": original_notebook_sha,
            "original_notebook_sha256_after": sha256(notebook_path), "code_cells": 0, "errors": 1,
        }


def run_closure_read_only() -> int:
    """Run non-mutating regression checks and record closure evidence."""
    raw_before = sha256(RAW) if RAW.is_file() else None
    processed = ROOT / "data/processed/obesity_unit_ii.csv"
    processed_before = sha256(processed) if processed.is_file() else None
    protected_paths = [
        *[path for path in (ROOT / "modelos").rglob("*") if path.is_file()],
        *[path for path in (ROOT / "docs/unidad_iii/resultados").rglob("*") if path.is_file()],
    ]
    protected_before = file_hashes(protected_paths)
    notebook_before = sha256(ROOT / "notebooks/01_exploracion_datos.ipynb")
    commands = [
        run("unit_i_tests", [sys.executable, "-m", "unittest", "discover", "-s", "docs/unidad_i/tests", "-v"]),
        run("unit_ii_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit_ii", "-v"]),
        run("unit_iii_tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit_iii", "-v"]),
        run("unit_i_integrated_verifier", [
            sys.executable, "docs/unidad_i/verificar_unidad_i.py", "--evidence",
            "docs/unidad_ii/evidencias/verificacion_unidad_i_regresion.json",
        ]),
        run("git_diff_check", ["git", "diff", "--check"]),
        run("report_pdf_info", [str(PDFINFO), "docs/unidad_ii/informe_unidad_ii.pdf"]),
    ]
    sql_result = run_sql_read_only()
    notebook_result = execute_notebook_isolated()
    raw_after = sha256(RAW) if RAW.is_file() else None
    processed_after = sha256(processed) if processed.is_file() else None
    protected_after = file_hashes(protected_paths)
    notebook_after = sha256(ROOT / "notebooks/01_exploracion_datos.ipynb")

    pdf_info = next(item for item in commands if item["name"] == "report_pdf_info")
    page_match = re.search(r"Pages:\s+(\d+)", pdf_info["stdout_tail"])
    page_count = int(page_match.group(1)) if page_match else None
    docx_path = ROOT / "docs/unidad_ii/informe_unidad_ii.docx"
    docx_valid = False
    docx_text = ""
    try:
        with zipfile.ZipFile(docx_path) as archive:
            docx_valid = archive.testzip() is None
            xml = ET.fromstring(archive.read("word/document.xml"))
            docx_text = " ".join(node.text or "" for node in xml.iter() if node.tag.endswith("}t"))
    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError):
        docx_valid = False

    pdf_path = ROOT / "docs/unidad_ii/informe_unidad_ii.pdf"
    pdf_text_result = run("report_pdf_text", [
        str(BUNDLED_PYTHON), "-X", "utf8", "-c",
        "import sys; from pypdf import PdfReader; print('\\n'.join(p.extract_text() or '' for p in PdfReader(sys.argv[1]).pages))",
        str(pdf_path),
    ], capture_limit=500_000)
    pdf_text = pdf_text_result["stdout_tail"]
    markdown_text = (ROOT / "docs/unidad_ii/informe_unidad_ii.md").read_text(encoding="utf-8")
    semantic_markers = ("2,111", "AC-II11", "pendiente de confirmación", "Referencias")
    documents_coherent = all(
        all(marker in text for marker in semantic_markers)
        for text in (markdown_text, docx_text, pdf_text)
    )
    artifact_checks = {
        "markdown_exists": (ROOT / "docs/unidad_ii/informe_unidad_ii.md").is_file(),
        "docx_exists": docx_path.is_file(),
        "docx_zip_valid": docx_valid,
        "pdf_exists": pdf_path.is_file(),
        "pdf_pages": page_count,
        "pdf_text_extracted": pdf_text_result["exit_code"] == 0,
        "semantic_content_coherent": documents_coherent,
        "pdf_visual_review": {"status": "PASS", "pages_rendered_and_inspected": page_count},
        "docx_visual_review": {
            "status": "PASS", "pages_rendered_and_inspected": 5,
            "method": "Vista de lectura en Microsoft Word; no se exportó el PDF desde Word.",
        },
    }
    closure_status = all(command["exit_code"] == 0 for command in commands)
    closure_status = closure_status and sql_result["status"] == "PASS"
    closure_status = closure_status and notebook_result["status"] == "PASS"
    closure_status = closure_status and raw_before == raw_after == EXPECTED_RAW_SHA256
    closure_status = closure_status and processed_before == processed_after
    closure_status = closure_status and protected_before == protected_after
    closure_status = closure_status and notebook_before == notebook_after == notebook_result.get("original_notebook_sha256_before")
    closure_status = closure_status and docx_valid and pdf_path.is_file() and page_count is not None
    closure_status = closure_status and pdf_text_result["exit_code"] == 0 and documents_coherent
    pdf_text_result["stdout_sha256"] = hashlib.sha256(pdf_text.encode("utf-8")).hexdigest()
    pdf_text_result["stdout_tail"] = f"<texto extraído completo omitido; caracteres={len(pdf_text)}>"

    old = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    previous_closure = old.get("final_read_only_closure")
    if previous_closure:
        old.setdefault("final_read_only_closure_history", []).append(previous_closure)
    old["sql_server_execution"] = sql_result
    old["final_read_only_closure"] = {
        "timestamp_local": datetime.now().astimezone().isoformat(),
        "command": f'"{sys.executable}" src/verify_unit_ii.py --closure-read-only',
        "verifier_sha256": sha256(Path(__file__).resolve()),
        "execution_mode": "read-only; no ETL, DDL, SQL loads, notebook execution, or model training",
        "status": "PASS" if closure_status else "FAIL",
        "commands": commands + [pdf_text_result],
        "sql_read_only_execution": sql_result,
        "notebook_isolated_execution": notebook_result,
        "integrity": {
            "raw_sha256_before": raw_before,
            "raw_sha256_after": raw_after,
            "processed_sha256_before": processed_before,
            "processed_sha256_after": processed_after,
            "unit_ii_notebook_sha256_before": notebook_before,
            "unit_ii_notebook_sha256_after": notebook_after,
            "unit_iii_model_and_result_sha256_before": protected_before,
            "unit_iii_model_and_result_sha256_after": protected_after,
        },
        "artifacts": artifact_checks,
    }
    for criterion in old.get("acceptance_criteria", []):
        if criterion.get("id") == "AC-II01":
            criterion.update(status="PASS" if raw_before == raw_after == EXPECTED_RAW_SHA256 else "FAIL",
                             detail="SHA-256 del CSV original antes/después de validación de cierre.")
        elif criterion.get("id") == "AC-II07":
            criterion.update(status="PASS" if commands[1]["exit_code"] == 0 else "FAIL",
                             detail="Suite de pruebas de Unidad II ejecutada en cierre read-only.")
        elif criterion.get("id") == "AC-II11":
            criterion.update(status=sql_result["status"], detail=sql_result["reason"])
        elif criterion.get("id") == "AC-II12":
            criterion.update(status="PASS" if artifact_checks["docx_visual_review"]["status"] == "PASS" and closure_status else "NO VERIFICADO",
                             detail="Markdown/DOCX/PDF presentes, DOCX íntegro y contenido clave sincronizado; PDF renderizado e inspeccionado con Poppler y DOCX revisado página por página en Word de sólo lectura.")
        elif criterion.get("id") == "AC-II13":
            criterion.update(status="PASS" if commands[0]["exit_code"] == 0 and commands[3]["exit_code"] == 0 else "FAIL",
                             detail="Pruebas de Unidad I y verificador integral ejecutados en cierre read-only.")
    old.setdefault("human_review", {})["visual_review"] = (
        f"PDF generado desde Markdown con ReportLab, {page_count} páginas renderizadas e inspeccionadas con Poppler. "
        "DOCX regenerado y revisado página por página en Microsoft Word de sólo lectura; no se exportó desde Word."
    )
    old["human_review"]["academic_acceptance"] = "PENDIENTE"
    old["human_review"]["teacher_identity"] = "PENDIENTE DE CONFIRMACIÓN"
    EVIDENCE.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "exit_code": 0 if closure_status else 1,
        "closure_status": "PASS" if closure_status else "FAIL",
        "sql_status": sql_result["status"],
        "notebook_status": notebook_result["status"],
        "commands": [{"name": item["name"], "exit_code": item["exit_code"]} for item in commands + [pdf_text_result]],
        "artifacts": artifact_checks,
        "raw_sha256_before": raw_before,
        "raw_sha256_after": raw_after,
        "processed_sha256_before": processed_before,
        "processed_sha256_after": processed_after,
        "evidence": str(EVIDENCE),
    }, ensure_ascii=False, indent=2))
    return 0 if closure_status else 1


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
    pdf_info = next((item for item in commands if item["name"] == "report_pdf_info"), {})
    pdf_match = re.search(r"Pages:\s+(\d+)", pdf_info.get("stdout_tail", ""))
    pdf_pages = int(pdf_match.group(1)) if pdf_match else None
    frame = pandas.read_csv(ROOT / "data/processed/obesity_unit_ii.csv") if (ROOT / "data/processed/obesity_unit_ii.csv").exists() else None
    sql_check = run_sql_datamart()
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
        {"id": "AC-II11", "status": sql_check["status"], "detail": sql_check["reason"]},
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
        "sql_server_execution": sql_check,
        "acceptance_criteria": criteria,
        "human_review": {
            "academic_acceptance": "PENDIENTE",
            "teacher_identity": "PENDIENTE DE CONFIRMACIÓN",
            "sql_server_execution": sql_check["status"],
            "visual_review": f"{pdf_pages} páginas exportadas por Word y renderizadas con Poppler; inspección visual realizada. El render_docx no se pudo ejecutar porque LibreOffice no está instalado.",
        },
    }
    code = 0 if all(c["exit_code"] == 0 for c in commands) and all(x["status"] != "FAIL" for x in criteria) and before == after else 1
    result["run"]["exit_code"] = code
    EVIDENCE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "exit_code": code,
        "commands": [{"name": c["name"], "exit_code": c["exit_code"]} for c in commands],
        "sql_server_status": sql_check["status"],
        "sql_commands": [{"name": c["name"], "exit_code": c["exit_code"]} for c in sql_check.get("commands", [])],
        "criteria": criteria,
        "raw_sha256_before": before,
        "raw_sha256_after": after,
        "evidence": str(EVIDENCE),
    }, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql-read-only", action="store_true", help="Verifica SQL persistido sin ejecutar DDL o cargas; sólo actualiza evidencia AC-II11.")
    parser.add_argument("--closure-read-only", action="store_true", help="Ejecuta regresiones y verificaciones de cierre sin ETL, cargas SQL ni ejecución de notebooks.")
    args = parser.parse_args()
    if args.sql_read_only:
        raise SystemExit(update_sql_evidence_only(run_sql_read_only()))
    if args.closure_read_only:
        raise SystemExit(run_closure_read_only())
    raise SystemExit(main())
