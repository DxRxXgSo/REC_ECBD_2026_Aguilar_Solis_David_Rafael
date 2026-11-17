"""Reproducible Unit IV K-Means and PCA analysis on the validated U2 dataset."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
PROCESSED = ROOT / "data/processed/obesity_unit_ii.csv"
EXPECTED_RAW_SHA256 = "28b6991062855d3d15642e38b1aa9d1b32fb7abbb5abf5b096f1868cd706154b"
EXPECTED_PROCESSED_SHA256 = "64418dcf666d49d832d07fe53dbfd9415662f2537502fde60e8dbe55b8f5218d"
FEATURES = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]
RANDOM_STATE = 42
K_VALUES = tuple(range(2, 10))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_validated_data(root: Path = ROOT) -> tuple[pd.DataFrame, dict[str, str]]:
    raw = root / "data/raw/ObesityDataSet_raw_and_data_sinthetic.csv"
    processed = root / "data/processed/obesity_unit_ii.csv"
    if not raw.is_file() or not processed.is_file():
        raise FileNotFoundError("Falta el CSV original o el conjunto procesado de Unidad II.")
    raw_hash, processed_hash = sha256(raw), sha256(processed)
    if raw_hash != EXPECTED_RAW_SHA256 or processed_hash != EXPECTED_PROCESSED_SHA256:
        raise ValueError("Las huellas de entrada no coinciden con el contrato validado de Unidad II.")
    frame = pd.read_csv(processed, encoding="utf-8", on_bad_lines="error")
    source = pd.read_csv(raw, encoding="utf-8", on_bad_lines="error")
    if frame.shape != (2111, 17) or not frame.equals(source):
        raise ValueError("El conjunto procesado no coincide con las 2,111 filas originales.")
    if frame.isna().any().any() or int(frame.duplicated().sum()) != 24:
        raise ValueError("La calidad del conjunto difiere del contrato de Unidad II.")
    if "NObeyesdad" in FEATURES or not set(FEATURES).issubset(frame.columns):
        raise ValueError("Predictores incorrectos: NObeyesdad no puede formar los clusters.")
    if not all(pd.api.types.is_numeric_dtype(frame[name]) for name in FEATURES):
        raise ValueError("Todas las variables seleccionadas deben ser numéricas.")
    return frame, {"raw_sha256": raw_hash, "processed_sha256": processed_hash}


def score_k(values: np.ndarray, k_values: tuple[int, ...] = K_VALUES) -> tuple[pd.DataFrame, dict[int, KMeans]]:
    rows: list[dict[str, float | int]] = []
    models: dict[int, KMeans] = {}
    for k in k_values:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20, max_iter=300)
        labels = model.fit_predict(values)
        score = float(silhouette_score(values, labels))
        rows.append({"k": k, "inertia": float(model.inertia_), "silhouette": score})
        models[k] = model
    return pd.DataFrame(rows), models


def analyze(root: Path = ROOT) -> dict[str, object]:
    frame, hashes = load_validated_data(root)
    x = frame.loc[:, FEATURES].astype(float)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    scores, models = score_k(x_scaled)
    best_k = int(scores.sort_values(["silhouette", "k"], ascending=[False, True]).iloc[0]["k"])
    kmeans = models[best_k]
    labels = kmeans.labels_.astype(int)

    pca = PCA(n_components=2, svd_solver="full")
    coordinates = pca.fit_transform(x_scaled)
    explained = pca.explained_variance_ratio_
    assignment = pd.DataFrame({
        "row_index": np.arange(len(frame), dtype=int),
        "cluster": labels,
        "PC1": coordinates[:, 0],
        "PC2": coordinates[:, 1],
    })
    numeric_profile = frame.assign(cluster=labels).groupby("cluster")[FEATURES].mean().round(4)
    categorical_columns = ["Gender", "family_history_with_overweight", "FAVC", "CAEC", "CALC", "MTRANS"]
    category_profile = {
        column: frame.assign(cluster=labels).groupby("cluster")[column]
        .agg(lambda values: values.value_counts(normalize=True).head(2).round(3).to_dict())
        .to_dict()
        for column in categorical_columns
    }
    label_profile = pd.crosstab(
        pd.Series(labels, name="cluster"),
        frame["NObeyesdad"],
        normalize="index",
    ).round(4)

    results_dir = root / "docs/unidad_iv/resultados"
    figure_dir = root / "docs/unidad_iv/figuras"
    model_dir = root / "modelos/unidad_iv"
    assignment_path = root / "data/processed/unidad_iv_cluster_assignments.csv"
    for directory in (results_dir, figure_dir, model_dir, assignment_path.parent):
        directory.mkdir(parents=True, exist_ok=True)

    assignment.to_csv(assignment_path, index=False, encoding="utf-8", lineterminator="\n")
    scores.to_csv(results_dir / "seleccion_k.csv", index=False, encoding="utf-8", lineterminator="\n")
    numeric_profile.to_csv(results_dir / "perfil_numerico_clusters.csv", encoding="utf-8", lineterminator="\n")
    label_profile.to_csv(results_dir / "distribucion_etiqueta_posthoc.csv", encoding="utf-8", lineterminator="\n")
    pd.DataFrame({
        "component": ["PC1", "PC2"],
        "explained_variance_ratio": explained,
        "cumulative_variance_ratio": np.cumsum(explained),
    }).to_csv(results_dir / "varianza_pca.csv", index=False, encoding="utf-8", lineterminator="\n")
    joblib.dump({"scaler": scaler, "kmeans": kmeans, "features": FEATURES, "random_state": RANDOM_STATE}, model_dir / "kmeans_pipeline.joblib")
    joblib.dump({"pca": pca, "scaler": scaler, "features": FEATURES}, model_dir / "pca_transform.joblib")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(scores["k"], scores["inertia"], marker="o", color="#147D86")
    axes[0].set(title="Método del codo", xlabel="Número de clusters (k)", ylabel="Inercia")
    axes[1].plot(scores["k"], scores["silhouette"], marker="o", color="#B15B36")
    axes[1].axvline(best_k, linestyle="--", color="#536B80", label=f"Máximo: k={best_k}")
    axes[1].set(title="Coeficiente Silhouette", xlabel="Número de clusters (k)", ylabel="Silhouette", ylim=(-0.05, 1))
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "seleccion_k.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    palette = plt.get_cmap("tab10")
    for cluster_id in sorted(np.unique(labels)):
        subset = coordinates[labels == cluster_id]
        ax.scatter(subset[:, 0], subset[:, 1], s=13, alpha=0.58, color=palette(cluster_id), label=f"Cluster {cluster_id}")
    ax.set(title="PCA de las variables estandarizadas, coloreada por cluster", xlabel=f"PC1 ({explained[0]*100:.1f}% varianza)", ylabel=f"PC2 ({explained[1]*100:.1f}% varianza)")
    ax.legend(markerscale=1.5)
    fig.tight_layout()
    fig.savefig(figure_dir / "pca_clusters.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    scaled_profile = pd.DataFrame(x_scaled, columns=FEATURES).assign(cluster=labels).groupby("cluster").mean()
    fig, ax = plt.subplots(figsize=(9, max(3.5, 0.55 * best_k)))
    image = ax.imshow(scaled_profile.to_numpy(), cmap="RdYlBu_r", aspect="auto", vmin=-2, vmax=2)
    ax.set_xticks(range(len(FEATURES)), FEATURES, rotation=35, ha="right")
    ax.set_yticks(range(best_k), [f"Cluster {i}" for i in scaled_profile.index])
    ax.set_title("Promedios por cluster en unidades estandarizadas")
    fig.colorbar(image, ax=ax, label="Desviaciones estándar respecto de la media global")
    fig.tight_layout()
    fig.savefig(figure_dir / "perfil_clusters.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    output_hashes = {
        str(path.relative_to(root)): sha256(path)
        for path in [assignment_path, results_dir / "seleccion_k.csv", results_dir / "perfil_numerico_clusters.csv",
                     results_dir / "distribucion_etiqueta_posthoc.csv", results_dir / "varianza_pca.csv"]
    }
    evidence = {
        "task": "Unidad IV — K-Means y PCA",
        "timestamp_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "command": ".venv-unit2\\Scripts\\python.exe -m unittest discover -s tests/unit_iv -v and notebook execution",
        "environment": {"python": __import__("platform").python_version(), "pandas": pd.__version__, "numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "input": {"path": "data/processed/obesity_unit_ii.csv", **hashes, "rows": len(frame), "columns": frame.shape[1], "duplicates_preserved": int(frame.duplicated().sum())},
        "design": {"features": FEATURES, "excluded_target": "NObeyesdad", "random_state": RANDOM_STATE, "k_values": list(K_VALUES), "scaler": "StandardScaler fit over all records for unsupervised descriptive analysis", "silhouette": "full-data silhouette score for each k", "posthoc_label_use": "NObeyesdad is cross-tabulated only after fitting and is not used in scaling, PCA or K-Means"},
        "k_selection": {"chosen_k": best_k, "selection_rule": "largest full-data silhouette score; inertia curve used as secondary elbow diagnostic", "scores": scores.to_dict(orient="records"), "cluster_sizes": {str(k): int(v) for k, v in pd.Series(labels).value_counts().sort_index().items()}},
        "pca": {"explained_variance_ratio": [float(v) for v in explained], "cumulative_two_components": float(explained.sum())},
        "outputs_sha256": output_hashes,
        "interpretation_limits": ["The 24 exact duplicate rows remain in the clustering input and contribute repeated weight.", "The dataset includes synthetic records; external population generalization is not established.", "Clusters describe associations and are not causal, clinical or validated subtypes.", "Height and Weight are included as continuous features; clusters may primarily reflect anthropometric scale."],
    }
    evidence_path = root / "docs/unidad_iv/evidencias/verificacion_unidad_iv.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "frame": frame,
        "features": FEATURES,
        "scores": scores,
        "best_k": best_k,
        "cluster_sizes": evidence["k_selection"]["cluster_sizes"],
        "numeric_profile": numeric_profile,
        "category_profile": category_profile,
        "label_profile": label_profile,
        "pca_variance": pd.DataFrame(evidence["pca"]["explained_variance_ratio"], index=["PC1", "PC2"], columns=["explained_variance_ratio"]),
        "assignment_path": assignment_path,
        "evidence_path": evidence_path,
    }
