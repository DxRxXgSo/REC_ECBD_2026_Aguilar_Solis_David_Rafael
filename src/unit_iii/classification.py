"""Grouped, leakage-safe classification experiments for NObeyesdad."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import cross_validate

from .data import (LABELS, RANDOM_STATE, classification_cv, sha256,
                   split_indices, split_summary, validate_input)
from .pipelines import feature_columns, make_pipeline

SCORING = {
    "accuracy": "accuracy",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
    "f1_macro": "f1_macro",
}


def run_classification(root: Path) -> dict[str, Any]:
    frame, u2_manifest = validate_input(root)
    train_index, test_index, groups = split_indices(frame)
    y = frame["NObeyesdad"]
    groups_train = groups[train_index]
    cv = classification_cv()
    results: list[dict[str, Any]] = []
    predictions: dict[str, np.ndarray] = {}
    reports: dict[str, Any] = {}
    model_dir = root / "modelos/unidad_iii"
    result_dir = root / "docs/unidad_iii/resultados"
    figure_dir = root / "docs/unidad_iii/figuras"
    for path in (model_dir, result_dir, figure_dir):
        path.mkdir(parents=True, exist_ok=True)

    for scenario in ("A", "B"):
        columns = feature_columns("classification", scenario)
        X_train = frame.iloc[train_index][columns]
        X_test = frame.iloc[test_index][columns]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        models = {
            "DummyClassifier_prior": DummyClassifier(strategy="prior"),
            "LogisticRegression": make_pipeline(
                X_train, LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
                scale_numeric=True,
            ),
            "RandomForestClassifier": make_pipeline(
                X_train, RandomForestClassifier(n_estimators=150, random_state=RANDOM_STATE,
                                                n_jobs=1), scale_numeric=False,
            ),
        }
        for model_name, estimator in models.items():
            scores = cross_validate(
                estimator, X_train, y_train, cv=cv, groups=groups_train,
                scoring=SCORING, n_jobs=1, error_score="raise",
            )
            fitted = estimator.fit(X_train, y_train)
            train_pred = fitted.predict(X_train)
            test_pred = fitted.predict(X_test)
            key = f"{scenario}_{model_name}"
            results.append({
                "scenario": scenario,
                "scenario_note": ("Incluye Height y Weight; puede aproximar la regla antropométrica de la etiqueta"
                                  if scenario == "A" else "Hábitos/condición; excluye Height y Weight"),
                "model": model_name,
                "feature_columns": "|".join(columns),
                "train_accuracy": float(accuracy_score(y_train, train_pred)),
                "test_accuracy": float(accuracy_score(y_test, test_pred)),
                "test_precision_macro": float(precision_score(y_test, test_pred, average="macro", zero_division=0)),
                "test_recall_macro": float(recall_score(y_test, test_pred, average="macro", zero_division=0)),
                "test_f1_macro": float(f1_score(y_test, test_pred, average="macro", zero_division=0)),
                **{f"cv_{metric}_mean": float(scores[f"test_{metric}"].mean()) for metric in SCORING},
                **{f"cv_{metric}_std": float(scores[f"test_{metric}"].std(ddof=1)) for metric in SCORING},
            })
            predictions[key] = test_pred
            reports[key] = classification_report(y_test, test_pred, labels=LABELS,
                                                  output_dict=True, zero_division=0)
            joblib.dump(fitted, model_dir / f"{key.lower()}_base.joblib", compress=3)

    metrics = pd.DataFrame(results)
    metrics_path = result_dir / "clasificacion_metricas_base.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8")
    report_path = result_dir / "clasificacion_reporte_por_clase_base.json"
    report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    prediction_data: dict[str, Any] = {"row_index": test_index, "y_true": y.iloc[test_index].to_numpy()}
    prediction_data.update(predictions)
    predictions_path = result_dir / "clasificacion_predicciones_test_base.csv"
    pd.DataFrame(prediction_data).to_csv(predictions_path, index=False, encoding="utf-8")

    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    for row_idx, scenario in enumerate(("A", "B")):
        for col_idx, model_name in enumerate(("DummyClassifier_prior", "LogisticRegression", "RandomForestClassifier")):
            key = f"{scenario}_{model_name}"
            cm = confusion_matrix(y.iloc[test_index], predictions[key], labels=LABELS)
            ax = axes[row_idx, col_idx]
            im = ax.imshow(cm, cmap="Blues")
            ax.set_title(f"Escenario {scenario}: {model_name}")
            ax.set_xticks(range(len(LABELS)), [x.replace("_", "\n") for x in LABELS], rotation=45, ha="right", fontsize=7)
            ax.set_yticks(range(len(LABELS)), [x.replace("_", "\n") for x in LABELS], fontsize=7)
            ax.set_xlabel("Predicción")
            ax.set_ylabel("Real")
            for i in range(len(LABELS)):
                for j in range(len(LABELS)):
                    ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=7,
                            color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.suptitle("Clasificación base de NObeyesdad: test reservado (A antropométrico / B hábitos)")
    fig.tight_layout()
    figure_path = figure_dir / "clasificacion_matrices_confusion_base.png"
    fig.savefig(figure_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    cv_folds = []
    for fold, (tr, va) in enumerate(cv.split(frame.iloc[train_index], y.iloc[train_index], groups_train)):
        cv_folds.append({"fold": fold + 1, "train_rows": len(tr), "validation_rows": len(va),
                         "group_overlap": len(set(groups_train[tr]).intersection(groups_train[va]))})
    metadata = {
        "task": "classification", "target": "NObeyesdad", "classes": LABELS,
        "scenarios": {"A": "includes Height and Weight; anthropometric circularity caution",
                      "B": "habits/condition features; excludes Height and Weight"},
        "random_state": RANDOM_STATE, "input_sha256": u2_manifest["output_sha256_bytes"],
        "raw_sha256": u2_manifest["input_sha256_bytes"],
        "split": split_summary(frame, train_index, test_index, groups),
        "cv": {"method": "StratifiedGroupKFold", "folds": cv_folds},
        "python": __import__("platform").python_version(), "pandas": pd.__version__,
        "numpy": np.__version__, "scikit_learn": sklearn.__version__,
        "metrics_csv_sha256": sha256(metrics_path), "predictions_csv_sha256": sha256(predictions_path),
        "per_class_report_sha256": sha256(report_path), "figure_sha256": sha256(figure_path),
        "models": {path.name: sha256(path) for path in sorted(model_dir.glob("*_base.joblib"))},
        "metric_note": "CV uses only training groups. Final test is evaluated after fit and is not used for tuning.",
    }
    manifest_path = result_dir / "clasificacion_manifest_base.json"
    manifest_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"metrics": metrics, "metadata": metadata, "metric_path": metrics_path,
            "figure_path": figure_path, "manifest_path": manifest_path}
