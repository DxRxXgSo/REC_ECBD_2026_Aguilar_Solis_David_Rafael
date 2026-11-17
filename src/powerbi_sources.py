"""Read-only Power BI source loader and contract checks for the ECBD dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


EXPECTED_CLASSES = {
    "Insufficient_Weight",
    "Normal_Weight",
    "Overweight_Level_I",
    "Overweight_Level_II",
    "Obesity_Type_I",
    "Obesity_Type_II",
    "Obesity_Type_III",
}
EXPECTED_RAW_COLUMNS = [
    "Gender", "Age", "Height", "Weight", "family_history_with_overweight",
    "FAVC", "FCVC", "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF",
    "TUE", "CALC", "MTRANS", "NObeyesdad",
]


def load_dashboard_sources(project_root: Path) -> dict[str, pd.DataFrame]:
    """Load existing source files without writing or changing any input."""
    root = Path(project_root)
    fact = pd.read_csv(root / "data/processed/obesity_unit_ii.csv")
    assignments = pd.read_csv(root / "data/processed/unidad_iv_cluster_assignments.csv")
    metrics = pd.read_csv(root / "docs/unidad_iii/resultados/optimizacion_metricas_test.csv")
    profile = pd.read_csv(root / "docs/unidad_iv/resultados/perfil_numerico_clusters.csv")
    variance = pd.read_csv(root / "docs/unidad_iv/resultados/varianza_pca.csv")

    fact.insert(0, "row_index", range(len(fact)))
    if assignments["row_index"].duplicated().any():
        raise ValueError("Cluster assignments contain duplicate row_index values")
    if set(fact["row_index"]) != set(assignments["row_index"]):
        raise ValueError("Cluster assignment keys do not match source row positions")
    fact = fact.merge(assignments, on="row_index", how="left", validate="one_to_one")
    if fact["cluster"].isna().any():
        raise ValueError("Some source observations have no cluster assignment")
    return {
        "fact": fact,
        "metrics": metrics,
        "cluster_profile": profile,
        "pca_variance": variance,
        "assignments": assignments,
    }


def validate_dashboard_sources(project_root: Path) -> dict[str, object]:
    """Validate row preservation and contracts used by Power BI visuals."""
    root = Path(project_root)
    sources = load_dashboard_sources(root)
    fact = sources["fact"]
    metrics = sources["metrics"]
    profile = sources["cluster_profile"]
    variance = sources["pca_variance"]
    raw = pd.read_csv(root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv")

    if len(raw) != 2111 or len(fact) != 2111 or raw.shape[1] != 17 or fact.shape[1] != 21:
        raise ValueError("Unexpected row or column count in raw/dashboard facts")
    if list(raw.columns) != EXPECTED_RAW_COLUMNS or not set(EXPECTED_RAW_COLUMNS).issubset(fact.columns):
        raise ValueError("Dashboard fact does not preserve the expected 17 source columns")
    if not raw.equals(fact.loc[:, raw.columns]):
        raise ValueError("Dashboard import layer changed source values or row ordering")
    if fact["row_index"].nunique() != 2111:
        raise ValueError("Dashboard row_index is not unique")
    if int(raw.duplicated().sum()) != 24 or int(fact.duplicated(subset=list(raw.columns)).sum()) != 24:
        raise ValueError("Exact duplicate observations were not preserved")
    if set(fact["NObeyesdad"].unique()) != EXPECTED_CLASSES:
        raise ValueError("The seven expected obesity categories do not match")
    if fact["cluster"].nunique() != 9 or set(profile["cluster"]) != set(range(9)):
        raise ValueError("Cluster assignment/profile contract is not k=9")
    if len(metrics) != 5 or set(metrics["task"]) != {"regression", "classification"}:
        raise ValueError("Expected one regression and four classification metric rows")
    if set(variance["component"]) != {"PC1", "PC2"}:
        raise ValueError("PCA variance table must contain PC1 and PC2")

    return {
        "raw_rows": len(raw),
        "raw_columns": len(raw.columns),
        "dashboard_fact_rows": len(fact),
        "exact_duplicate_rows": 24,
        "obesity_classes": sorted(fact["NObeyesdad"].unique().tolist()),
        "cluster_count": int(fact["cluster"].nunique()),
        "metric_rows": len(metrics),
        "pca_components": variance["component"].tolist(),
    }
