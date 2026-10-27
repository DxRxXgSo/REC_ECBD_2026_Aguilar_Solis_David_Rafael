"""Unit III input contract, duplicate groups, and reproducible partitions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold


EXPECTED_COLUMNS = [
    "Gender", "Age", "Height", "Weight", "family_history_with_overweight",
    "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF",
    "TUE", "CALC", "MTRANS", "NObeyesdad",
]
LABELS = [
    "Insufficient_Weight", "Normal_Weight", "Overweight_Level_I",
    "Overweight_Level_II", "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
]
RANDOM_STATE = 42
EXPECTED_RAW_SHA256 = "28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b"
EXPECTED_PROCESSED_SHA256 = "64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d"


class DataContractError(ValueError):
    """Raised when Unit II input or its provenance does not meet the contract."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_input(root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
    processed = root / "data/processed/obesity_unit_ii.csv"
    manifest_path = root / "data/processed/unit_ii_manifest.json"
    unit_ii_evidence_path = root / "docs/unidad_ii/evidencias/verificacion_unidad_ii.json"
    for path in (raw, processed, manifest_path, unit_ii_evidence_path):
        if not path.is_file():
            raise DataContractError(f"Falta el artefacto requerido: {path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evidence = json.loads(unit_ii_evidence_path.read_text(encoding="utf-8"))
    if sha256(raw) != EXPECTED_RAW_SHA256 or sha256(processed) != EXPECTED_PROCESSED_SHA256:
        raise DataContractError("La huella de raw o del derivado no coincide con la versión validada de Unidad II")
    if manifest.get("input_sha256_bytes") != EXPECTED_RAW_SHA256:
        raise DataContractError("El manifiesto U2 no respalda la huella de la fuente")
    if manifest.get("output_sha256_bytes") != EXPECTED_PROCESSED_SHA256 or not manifest.get("source_values_equal"):
        raise DataContractError("El manifiesto U2 no confirma correspondencia exacta fuente-derivado")
    if evidence.get("run", {}).get("exit_code") != 0:
        raise DataContractError("La verificación registrada de Unidad II no terminó con código 0")
    criteria = {item["id"]: item["status"] for item in evidence.get("acceptance_criteria", [])}
    required = [f"AC-II{n:02}" for n in range(1, 11)] + ["AC-II12", "AC-II13", "AC-II14"]
    failed = [key for key in required if criteria.get(key) != "PASS"]
    if failed:
        raise DataContractError(f"Criterios técnicos requeridos de Unidad II no aprobados: {failed}")
    frame = pd.read_csv(processed, encoding="utf-8", on_bad_lines="error")
    source_frame = pd.read_csv(raw, encoding="utf-8", on_bad_lines="error")
    if frame.shape != (2111, 17) or list(frame.columns) != EXPECTED_COLUMNS:
        raise DataContractError(f"Dimensiones/esquema inesperado: {frame.shape}, {list(frame.columns)}")
    if not frame.equals(source_frame):
        raise DataContractError("Los valores procesados ya no coinciden con la fuente UCI")
    if frame.isna().any().any() or int(frame.duplicated().sum()) != 24:
        raise DataContractError("Faltantes/duplicados no coinciden con el contrato U2")
    if not pd.api.types.is_numeric_dtype(frame["Weight"]):
        raise DataContractError("Weight debe ser numérico para regresión")
    if sorted(frame["NObeyesdad"].unique().tolist()) != sorted(LABELS):
        raise DataContractError("NObeyesdad no contiene las siete clases previstas")
    if not manifest.get("exact_duplicate_rows_preserved") == 24:
        raise DataContractError("El manifiesto no confirma la conservación de los 24 duplicados")
    return frame, manifest


def duplicate_group_ids(frame: pd.DataFrame) -> np.ndarray:
    """Return one stable, shared group ID for each exactly identical row."""
    rows = [tuple(row) for row in frame.itertuples(index=False, name=None)]
    codes, _ = pd.factorize(pd.Series(rows, dtype=object), sort=False)
    return codes.astype(np.int64)


def split_indices(frame: pd.DataFrame, random_state: int = RANDOM_STATE) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    groups = duplicate_group_ids(frame)
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=random_state)
    train_index, test_index = next(splitter.split(frame, frame["NObeyesdad"], groups))
    if set(groups[train_index]).intersection(groups[test_index]):
        raise DataContractError("Hay grupos de filas idénticas compartidos entre train y test")
    return train_index, test_index, groups


def regression_cv(groups: np.ndarray, n_splits: int = 5) -> GroupKFold:
    return GroupKFold(n_splits=n_splits)


def classification_cv(random_state: int = RANDOM_STATE, n_splits: int = 5) -> StratifiedGroupKFold:
    return StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)


def split_summary(frame: pd.DataFrame, train_index: np.ndarray, test_index: np.ndarray, groups: np.ndarray) -> dict[str, Any]:
    return {
        "random_state": RANDOM_STATE,
        "splitter": "StratifiedGroupKFold(n_splits=5, shuffle=True); first fold reserved as final test",
        "train_indices": train_index.tolist(),
        "test_indices": test_index.tolist(),
        "train_rows": len(train_index),
        "test_rows": len(test_index),
        "train_unique_groups": int(np.unique(groups[train_index]).size),
        "test_unique_groups": int(np.unique(groups[test_index]).size),
        "group_intersection_count": int(len(set(groups[train_index]).intersection(groups[test_index]))),
        "train_class_counts": frame.iloc[train_index]["NObeyesdad"].value_counts().reindex(LABELS, fill_value=0).to_dict(),
        "test_class_counts": frame.iloc[test_index]["NObeyesdad"].value_counts().reindex(LABELS, fill_value=0).to_dict(),
        "duplicate_row_count": int(frame.duplicated().sum()),
        "duplicate_group_ids": sorted(np.unique(groups[frame.duplicated(keep=False)]).astype(int).tolist()),
    }
