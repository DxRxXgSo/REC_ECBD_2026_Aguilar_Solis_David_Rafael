"""Read-only Unit I checks; writes evidence only after a passing run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shlex
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree


EXPECTED_CANONICAL_CSV_SHA256 = "b62e1eb1c8c981379bee23e39e35683f5455683bd772dc722827158dde929a1f"
PREVIOUSLY_RECORDED_NOTEBOOK_SHA256 = "06ffa5be12ab00a41f1b445d66dc37ed817aec31d000e52a80adaef2be989a70"
EXPECTED_HEADER = [
    "Gender", "Age", "Height", "Weight", "family_history_with_overweight",
    "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF",
    "TUE", "CALC", "MTRANS", "NObeyesdad",
]
EXPECTED_RECORDS = 2111
MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}
DATE_PATTERNS = (
    re.compile(r"\b(?P<day>\d{1,2})\s+de\s+(?P<month>enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\s+de\s+(?P<year>20\d{2})\b", re.I),
    re.compile(r"\b(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>20\d{2})\b"),
    re.compile(r"\b(?P<year>20\d{2})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\b"),
)
REQUIRED_REFERENCE_URLS = (
    "https://doi.org/10.24432/C5H31Z",
    "https://doi.org/10.1016/j.dib.2019.104344",
    "https://doi.org/10.6028/NIST.SP.1500-1r1",
    "https://kddlab.com/files/CRISPWP-0800.pdf",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_dates(text: str) -> list[str]:
    found: list[str] = []
    for line in text.splitlines():
        for pattern in DATE_PATTERNS:
            for match in pattern.finditer(line):
                day = int(match.group("day"))
                month_token = match.group("month")
                month = MONTHS[month_token.lower()] if month_token and not month_token.isdigit() else int(month_token)
                year = int(match.group("year"))
                try:
                    normalized = datetime(year, month, day).date().isoformat()
                except ValueError:
                    normalized = "INVALID"
                found.append(f"{normalized}\t{line.strip()}")
    return found


def stale_calendar_claims(text: str) -> list[str]:
    patterns = (
        re.compile(r"\bno\s+(?:se\s+)?(?:localiz[oó]|encontr[oó]|verificable)\b[^\n.]{0,140}(?:gu[ií]a|cronograma|calendario|fecha oficial)", re.I),
        re.compile(r"\bno\s+(?:est[aá]n|est[aá])\s+disponibles\b[^\n.]{0,100}(?:gu[ií]a|cronograma|calendario|fecha oficial)", re.I),
        re.compile(r"\bpendiente\b[^\n.]{0,120}(?:gu[ií]a|cronograma|calendario|fecha oficial)", re.I),
        re.compile(r"\b(?:gu[ií]a|cronograma|calendario|fecha oficial)\b[^\n.]{0,100}\b(?:pendiente|por confirmar|no disponible|no verificable)", re.I),
    )
    return [match.group(0).strip() for pattern in patterns for match in pattern.finditer(text)]


def build_report(project_root: Path, verifier_path: Path, command: str) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def record(name: str, status: str, details: object, category: str = "technical") -> None:
        checks.append({"check": name, "category": category, "status": status, "details": details})

    paths = {
        "csv": project_root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv",
        "notebook": project_root / "notebooks/00_revision_inicial_dataset.ipynb",
        "readme": project_root / "README.md",
        "global_rules": project_root / "docs/sdd/00_reglas_globales.md",
        "plan_md": project_root / "docs/unidad_i/planeacion_unidad_i.md",
        "plan_docx": project_root / "docs/unidad_i/planeacion_unidad_i.docx",
        "previous_evidence": project_root / "docs/unidad_i/evidencias/verificacion_unidad_i.json",
    }

    raw_csv: bytes | None = None
    try:
        raw_csv = paths["csv"].read_bytes()
        record("csv_readable", "PASS", {"path": str(paths["csv"]), "bytes": len(raw_csv)})
    except OSError as exc:
        record("csv_readable", "FAIL", {"path": str(paths["csv"]), "error": f"{type(exc).__name__}: {exc}"})

    csv_rows: list[list[str]] | None = None
    if raw_csv is None:
        record("csv_content_hash", "NO VERIFICADO", "No se pudo leer el CSV.")
        record("csv_header", "NO VERIFICADO", "No se pudo leer el CSV.")
        record("csv_record_count", "NO VERIFICADO", "No se pudo leer el CSV.")
        record("csv_row_width", "NO VERIFICADO", "No se pudo leer el CSV.")
        record("csv_quality_counts", "NO VERIFICADO", "No se pudo leer el CSV.")
    else:
        normalized_csv = raw_csv.replace(b"\r\n", b"\n")
        local_hash = sha256_bytes(raw_csv)
        canonical_hash = sha256_bytes(normalized_csv)
        record("csv_content_hash", "PASS" if canonical_hash == EXPECTED_CANONICAL_CSV_SHA256 else "FAIL",
               {"sha256_local_bytes": local_hash, "sha256_after_crlf_to_lf": canonical_hash,
                "expected_canonical_sha256": EXPECTED_CANONICAL_CSV_SHA256,
                "byte_length": len(raw_csv), "crlf_count": raw_csv.count(b"\r\n"),
                "lf_only_count": raw_csv.count(b"\n") - raw_csv.count(b"\r\n"),
                "interpretation": "Se compara el hash canónico; el hash local conserva los finales de línea presentes."})
        try:
            decoded = raw_csv.decode("utf-8-sig", errors="strict")
            reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
            csv_rows = list(reader)
            record("csv_parse", "PASS", {"parsed_rows_including_header": len(csv_rows), "encoding": "UTF-8"})
        except (UnicodeDecodeError, csv.Error, OSError, ValueError) as exc:
            record("csv_parse", "FAIL", {"error": f"{type(exc).__name__}: {exc}"})
            csv_rows = None
        if csv_rows is None:
            for name in ("csv_header", "csv_record_count", "csv_row_width", "csv_quality_counts"):
                record(name, "NO VERIFICADO", "El CSV no se pudo parsear completamente.")
        else:
            header = csv_rows[0] if csv_rows else []
            data_rows = csv_rows[1:] if csv_rows else []
            record("csv_header", "PASS" if header == EXPECTED_HEADER else "FAIL",
                   {"column_count": len(header), "expected_column_count": len(EXPECTED_HEADER),
                    "missing": [column for column in EXPECTED_HEADER if column not in header],
                    "unexpected": [column for column in header if column not in EXPECTED_HEADER],
                    "order_matches": header == EXPECTED_HEADER})
            record("csv_record_count", "PASS" if len(data_rows) == EXPECTED_RECORDS else "FAIL",
                   {"records": len(data_rows), "expected": EXPECTED_RECORDS})
            widths = Counter(len(row) for row in data_rows)
            record("csv_row_width", "PASS" if all(len(row) == len(EXPECTED_HEADER) for row in data_rows) else "FAIL",
                   {"width_counts": {str(width): count for width, count in sorted(widths.items())},
                    "expected_width": len(EXPECTED_HEADER)})
            empty_cells = sum(value == "" for row in data_rows for value in row)
            duplicate_rows = sum(count - 1 for count in Counter(tuple(row) for row in data_rows).values())
            record("csv_quality_counts", "PASS" if empty_cells == 0 and duplicate_rows == 24 else "FAIL",
                   {"empty_cells": empty_cells, "exact_duplicate_rows": duplicate_rows,
                    "expected_empty_cells": 0, "expected_exact_duplicate_rows": 24})

    notebook_hash: str | None = None
    try:
        notebook_bytes = paths["notebook"].read_bytes()
        notebook_hash = sha256_bytes(notebook_bytes)
        notebook = json.loads(notebook_bytes.decode("utf-8"))
        valid_structure = (notebook.get("nbformat") == 4 and isinstance(notebook.get("cells"), list))
        code_cells = [cell for cell in notebook.get("cells", []) if isinstance(cell, dict) and cell.get("cell_type") == "code"]
        cell_errors = []
        for index, cell in enumerate(notebook.get("cells", [])):
            if not isinstance(cell, dict) or cell.get("cell_type") not in {"code", "markdown", "raw"}:
                cell_errors.append(f"invalid_cell_{index}")
                continue
            if not isinstance(cell.get("source"), (str, list)):
                cell_errors.append(f"invalid_source_{index}")
            if cell.get("cell_type") == "code":
                if not isinstance(cell.get("outputs"), list):
                    cell_errors.append(f"invalid_outputs_{index}")
                if cell.get("execution_count") is not None and not isinstance(cell.get("execution_count"), int):
                    cell_errors.append(f"invalid_execution_count_{index}")
        valid_structure = valid_structure and not cell_errors
        record("notebook_structure", "PASS" if valid_structure else "FAIL",
               {"nbformat": notebook.get("nbformat"), "cell_count": len(notebook.get("cells", [])),
                "code_cell_count": len(code_cells), "errors": cell_errors,
                "sha256_observed": notebook_hash})
        if valid_structure:
            saved_outputs = sum(bool(cell.get("outputs")) for cell in code_cells)
            executed_with_outputs = sum(cell.get("execution_count") is not None and bool(cell.get("outputs")) for cell in code_cells)
            record("notebook_saved_outputs", "PASS" if saved_outputs > 0 else "FAIL",
                   {"code_cells_with_stored_outputs": saved_outputs,
                    "stored_outputs_are_not_proof_of_authenticity": True,
                    "notebook_executed_by_this_verifier": False})
            baseline_matches = notebook_hash == PREVIOUSLY_RECORDED_NOTEBOOK_SHA256
            record("notebook_matches_prior_observed_hash", "PASS" if baseline_matches else "FAIL",
                   {"sha256_observed": notebook_hash, "previously_recorded_sha256": PREVIOUSLY_RECORDED_NOTEBOOK_SHA256,
                    "claim": "Hash continuity only; it does not authenticate when or how saved outputs were produced."})
        else:
            record("notebook_saved_outputs", "NO VERIFICADO", "La estructura del notebook es inválida.")
            record("notebook_matches_prior_observed_hash", "NO VERIFICADO", "La estructura del notebook es inválida.")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, AttributeError, TypeError) as exc:
        record("notebook_structure", "FAIL", {"error": f"{type(exc).__name__}: {exc}"})
        record("notebook_saved_outputs", "NO VERIFICADO", "No se pudo leer el notebook.")
        record("notebook_matches_prior_observed_hash", "NO VERIFICADO", "No se pudo leer el notebook.")

    global_text: str | None = None
    plan_text: str | None = None
    readme_text: str | None = None
    for key, check_name in (("global_rules", "global_rules_readable"), ("plan_md", "plan_markdown_readable"), ("readme", "readme_readable")):
        try:
            value = paths[key].read_text(encoding="utf-8-sig")
            if not value.strip():
                raise ValueError("empty file")
            record(check_name, "PASS", {"path": str(paths[key]), "characters": len(value)})
            if key == "global_rules": global_text = value
            elif key == "plan_md": plan_text = value
            else: readme_text = value
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            record(check_name, "FAIL", {"path": str(paths[key]), "error": f"{type(exc).__name__}: {exc}"})

    if global_text is None:
        record("confirmed_calendar_source", "NO VERIFICADO", "No se pudo leer la fuente SDD de calendario.")
    else:
        lines = global_text.splitlines()
        has_u1 = any("2 de octubre de 2026" in line and "Unidad I" in line and "20%" in line for line in lines)
        has_close = any("20 de noviembre de 2026" in line and "cierre" in line.lower() and "15%" in line for line in lines)
        has_activity0_discrepancy = any("25 o 28 de septiembre de 2026" in line and "Actividad 0" in line for line in lines)
        ok = has_u1 and has_close and has_activity0_discrepancy
        record("confirmed_calendar_source", "PASS" if ok else "FAIL",
               {"unit_i_2026_10_02": has_u1, "project_close_2026_11_20": has_close,
                "activity_0_25_or_28_september_preserved": has_activity0_discrepancy})

    if plan_text is None:
        record("plan_calendar_coherence", "NO VERIFICADO", "No se pudo leer la planeación.", "academic")
    else:
        plan_lines = plan_text.splitlines()
        dated_plan_lines = extract_dates(plan_text)
        u1_date = any(item.startswith("2026-10-02\t") and "unidad i" in item.split("\t", 1)[1].lower()
                      for item in dated_plan_lines)
        close_date = any(item.startswith("2026-11-20\t") and any(
            word in item.split("\t", 1)[1].lower() for word in ("cierre", "fecha final", "20 de noviembre", "periodo"))
            for item in dated_plan_lines)
        activity0_line = any("actividad 0" in line.lower() and re.search(r"\b25\s+(?:y|o|/)\s+28\b", line.lower())
                             and "septiembre de 2026" in line.lower() for line in plan_lines)
        activity0_dates = activity0_line
        plan_stale = stale_calendar_claims(plan_text)
        ok = u1_date and close_date and activity0_dates and not plan_stale
        record("plan_calendar_coherence", "PASS" if ok else "FAIL",
               {"unit_i_date_present": u1_date, "project_close_present": close_date,
                "activity_0_both_dates_present": activity0_dates, "stale_unknown_calendar_claims": plan_stale}, "academic")

    if readme_text is None:
        record("readme_calendar_coherence", "FAIL", "README ausente o ilegible.", "documentation")
    else:
        dated_lines = extract_dates(readme_text)
        dates_by_line: dict[str, set[str]] = {}
        for item in dated_lines:
            normalized_date, source_line = item.split("\t", 1)
            dates_by_line.setdefault(source_line, set()).add(normalized_date)
        wrong_u1 = [line for line, dates in dates_by_line.items()
                    if "unidad i" in line.lower() and "2026-10-02" not in dates]
        wrong_close = [line for line, dates in dates_by_line.items()
                       if any(word in line.lower() for word in ("cierre", "fecha final", "periodo", "periodo:"))
                       and "2026-11-20" not in dates]
        stale_claims = stale_calendar_claims(readme_text)
        has_close_claim = any("2026-11-20" in dates and any(
            word in line.lower() for word in ("cierre", "fecha final", "periodo", "periodo:"))
            for line, dates in dates_by_line.items())
        ok = not wrong_u1 and not wrong_close and not stale_claims and has_close_claim
        record("readme_calendar_coherence", "PASS" if ok else "FAIL",
               {"unit_i_conflicting_dates": wrong_u1, "close_conflicting_dates": wrong_close,
                "stale_unknown_calendar_claims": stale_claims, "confirmed_close_in_readme": has_close_claim,
                "unit_i_date_may_be_omitted_if_no_conflicting_claim": True}, "documentation")

    docx_ok = False
    try:
        with zipfile.ZipFile(paths["plan_docx"]) as archive:
            bad_member = archive.testzip()
            document_xml = archive.read("word/document.xml")
            ElementTree.fromstring(document_xml)
            docx_ok = bad_member is None
        record("docx_container_readable", "PASS" if docx_ok else "FAIL",
               {"zip_integrity": bad_member is None, "document_xml_parseable": True,
                "visual_layout_checked": False}, "technical")
    except (OSError, zipfile.BadZipFile, KeyError, ElementTree.ParseError) as exc:
        record("docx_container_readable", "FAIL", {"error": f"{type(exc).__name__}: {exc}"}, "technical")

    if plan_text is None:
        record("reference_urls_syntactically_present", "NO VERIFICADO", "No se pudo leer la planeación.")
    else:
        missing_urls = [url for url in REQUIRED_REFERENCE_URLS if url not in plan_text]
        malformed_urls = [url for url in REQUIRED_REFERENCE_URLS if url in plan_text and urlparse(url).scheme not in {"http", "https"}]
        record("reference_urls_syntactically_present", "PASS" if not missing_urls and not malformed_urls else "FAIL",
               {"missing_urls": missing_urls, "malformed_urls": malformed_urls,
                "network_reachability_or_academic_validity_checked": False})

    local_plan_reference = "docs/unidad_i/planeacion_unidad_i.md" in (readme_text or "")
    plan_exists = paths["plan_md"].is_file()
    docx_exists = paths["plan_docx"].is_file()
    record("required_document_paths", "PASS" if local_plan_reference and plan_exists and docx_exists else "FAIL",
           {"readme_references_plan": local_plan_reference, "markdown_exists": plan_exists, "docx_exists": docx_exists})

    by_name = {item["check"]: item["status"] for item in checks}
    criteria = []
    for criterion in ("AC-I01", "AC-I02", "AC-I03", "AC-I04", "AC-I05", "AC-I06", "AC-I07", "AC-I08", "AC-I10", "AC-I14"):
        criteria.append({"id": criterion, "status": "NO VERIFICADO", "reason": "Requiere revisión académica o visual."})
    criteria.append({"id": "AC-I09", "status": "PASS" if by_name.get("confirmed_calendar_source") == "PASS" and by_name.get("plan_calendar_coherence") == "PASS" else "FAIL",
                     "reason": "Calendario SDD y planeación deben coincidir; Actividad 0 conserva ambas fechas."})
    criteria.append({"id": "AC-I11", "status": "PASS" if by_name.get("readme_calendar_coherence") == "PASS" and by_name.get("required_document_paths") == "PASS" else "FAIL",
                     "reason": "Se valida coherencia de calendario y rutas; la revisión académica completa del README permanece manual."})
    csv_checks = ("csv_readable", "csv_content_hash", "csv_parse", "csv_header", "csv_record_count", "csv_row_width", "csv_quality_counts")
    criteria.append({"id": "AC-I12", "status": "PASS" if all(by_name.get(name) == "PASS" for name in csv_checks) else "FAIL",
                     "reason": "Hash, lectura, encabezado, dimensiones, ancho uniforme y conteos básicos."})
    notebook_checks = ("notebook_structure", "notebook_saved_outputs", "notebook_matches_prior_observed_hash")
    criteria.append({"id": "AC-I13", "status": "PASS" if all(by_name.get(name) == "PASS" for name in notebook_checks) else "FAIL",
                     "reason": "Estructura, salidas guardadas y continuidad de hash; no autentica el origen histórico."})

    failures = sum(item["status"] == "FAIL" for item in checks)
    exit_code = 1 if failures else 0
    try:
        verifier_bytes = verifier_path.read_bytes()
        verifier_hash = sha256_bytes(verifier_bytes)
    except OSError:
        verifier_hash = None
        exit_code = 1

    return {
        "schema_version": "2.0",
        "run": {"timestamp_local": datetime.now().astimezone().isoformat(timespec="seconds"),
                "command": command, "python_version": sys.version, "project_root": str(project_root),
                "verifier_sha256": verifier_hash, "exit_code": exit_code,
                "notebook_execution_performed": False},
        "summary": {"pass": sum(item["status"] == "PASS" for item in checks),
                    "fail": failures,
                    "no_verificado": sum(item["status"] == "NO VERIFICADO" for item in checks)},
        "checks": checks,
        "acceptance_criteria": criteria,
        "interpretation": {"technical_tests_do_not_replace_academic_or_visual_review": True,
                           "stored_notebook_outputs_are_not_claimed_as_authentic_historical_execution": True},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--evidence", type=Path, help="Evidence output path. Negative fixtures should use a temporary path.")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    evidence_path = args.evidence.resolve() if args.evidence else project_root / "docs/unidad_i/evidencias/verificacion_unidad_i.json"
    verifier_path = Path(__file__).resolve()
    command = shlex.join([sys.executable, str(verifier_path), *sys.argv[1:]])
    report = build_report(project_root, verifier_path, command)
    exit_code = int(report["run"]["exit_code"])

    is_git_project = (project_root / ".git").exists()
    evidence_is_inside_project = evidence_path == project_root or project_root in evidence_path.parents
    should_write = exit_code == 0 or not (is_git_project and evidence_is_inside_project)
    if should_write:
        try:
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print(json.dumps({"evidence_write_error": f"{type(exc).__name__}: {exc}", "report": report}, ensure_ascii=True))
            return 1
    print(json.dumps(report, ensure_ascii=True))
    if not should_write:
        print("Evidencia del proyecto no sobrescrita: las verificaciones tienen FAIL.", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
