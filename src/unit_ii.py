"""Conservative and reproducible ETL for Unit II."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_COLUMNS = [
    "Gender", "Age", "Height", "Weight", "family_history_with_overweight",
    "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF",
    "TUE", "CALC", "MTRANS", "NObeyesdad",
]
NUMERIC_COLUMNS = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]
CATEGORIES = {
    "Gender": {"Female", "Male"},
    "family_history_with_overweight": {"yes", "no"},
    "FAVC": {"yes", "no"},
    "CAEC": {"no", "Sometimes", "Frequently", "Always"},
    "SMOKE": {"yes", "no"},
    "SCC": {"yes", "no"},
    "CALC": {"no", "Sometimes", "Frequently", "Always"},
    "MTRANS": {"Automobile", "Motorbike", "Bike", "Public_Transportation", "Walking"},
    "NObeyesdad": {
        "Insufficient_Weight", "Normal_Weight", "Overweight_Level_I",
        "Overweight_Level_II", "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
    },
}


class DataValidationError(ValueError):
    """Raised when source data does not satisfy the documented schema."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_frame(frame: pd.DataFrame, expected_rows: int | None = None) -> pd.DataFrame:
    if list(frame.columns) != EXPECTED_COLUMNS:
        raise DataValidationError(
            f"Encabezados/orden inválidos: esperados {EXPECTED_COLUMNS}; recibidos {list(frame.columns)}"
        )
    if frame.empty:
        raise DataValidationError("El CSV no contiene filas")
    if expected_rows is not None and len(frame) != expected_rows:
        raise DataValidationError(f"Filas inválidas: esperadas {expected_rows}, recibidas {len(frame)}")
    if frame.isna().any().any():
        missing = frame.columns[frame.isna().any()].tolist()
        raise DataValidationError(f"Valores faltantes en {missing}")
    for column in NUMERIC_COLUMNS:
        try:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
        except (TypeError, ValueError) as error:
            raise DataValidationError(f"Columna numérica inválida {column}: {error}") from error
        if not np.isfinite(frame[column].to_numpy(dtype=float)).all():
            raise DataValidationError(f"Valores no finitos en {column}")
    for column, allowed in CATEGORIES.items():
        observed = set(frame[column].astype(str).unique())
        invalid = sorted(observed - allowed)
        if invalid:
            raise DataValidationError(f"Categorías fuera de dominio en {column}: {invalid}")
    return frame


def read_source(source: Path, expected_rows: int | None = 2111) -> pd.DataFrame:
    if not source.is_file():
        raise FileNotFoundError(f"No existe el archivo de entrada: {source}")
    try:
        frame = pd.read_csv(source, encoding="utf-8", on_bad_lines="error")
    except (UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError, OSError) as error:
        raise DataValidationError(f"No se pudo leer el CSV {source}: {error}") from error
    return validate_frame(frame, expected_rows=expected_rows)


def process(source: Path, output: Path, manifest_path: Path, expected_rows: int | None = 2111) -> dict[str, Any]:
    frame = read_source(source, expected_rows=expected_rows)
    original_hash = sha256(source)
    duplicates = int(frame.duplicated().sum())
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve all rows/values. CSV line endings and quoting are normalized only in the derivative.
    frame.to_csv(output, index=False, encoding="utf-8", lineterminator="\n", float_format="%.15g")
    processed = read_source(output, expected_rows=expected_rows)
    output_hash = sha256(output)
    manifest: dict[str, Any] = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/unit_ii.py",
        "input_path": str(source),
        "input_sha256_bytes": original_hash,
        "output_path": str(output),
        "output_sha256_bytes": output_hash,
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "rows_read": len(frame),
        "rows_preserved": len(processed),
        "rows_excluded": 0,
        "columns": list(processed.columns),
        "column_count": len(processed.columns),
        "missing_values": int(processed.isna().sum().sum()),
        "exact_duplicate_rows_preserved": duplicates,
        "transformations": ["CSV serialization normalized to UTF-8/LF; no row filtering or feature recoding"],
        "decision": "Preserve all 24 exact duplicates and all observed values; do not fit learned preprocessing in Unit II.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv")
    parser.add_argument("--output", type=Path, default=root / "data/processed/obesity_unit_ii.csv")
    parser.add_argument("--manifest", type=Path, default=root / "data/processed/unit_ii_manifest.json")
    args = parser.parse_args()
    try:
        manifest = process(args.input, args.output, args.manifest)
    except (OSError, DataValidationError) as error:
        parser.exit(2, f"ERROR: {error}\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
