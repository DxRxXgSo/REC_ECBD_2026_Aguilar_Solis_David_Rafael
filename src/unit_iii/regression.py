"""Grouped, leakage-safe regression experiment for predicting Weight."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .data import (
    RANDOM_STATE, duplicate_group_ids, regression_cv, sha256, split_indices, split_summary, validate_input,
)
from .pipelines import REGRESSION_FEATURES, make_pipeline


SCORING = {
    "mae": "neg_mean_absolute_error",
    "rmse": "neg_root_mean_squared_error",
    "r2": "r2",
}


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
    }


def run_regression(root: Path) -> dict[str, Any]:
    frame, u2_manifest = validate_input(root)
    train_index, test_index, groups = split_indices(frame)
    features = REGRESSION_FEATURES.copy()
    if "Weight" in features or "NObeyesdad" in features:
        raise ValueError("La lista de predictores incluye objetivo o etiqueta")
    X = frame[features]
    y = frame["Weight"]
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    groups_train = groups[train_index]
    cv = regression_cv(groups_train, n_splits=5)
    estimators = {
        "DummyRegressor_mean": DummyRegressor(strategy="mean"),
        "LinearRegression": make_pipeline(X_train, LinearRegression(), scale_numeric=True),
        "RandomForestRegressor": make_pipeline(
            X_train,
            RandomForestRegressor(n_estimators=150, random_state=RANDOM_STATE, n_jobs=1),
            scale_numeric=False,
        ),
    }
    result_rows: list[dict[str, Any]] = []
    prediction_rows: dict[str, np.ndarray] = {}
    model_dir = root / "modelos/unidad_iii"
    result_dir = root / "docs/unidad_iii/resultados"
    figure_dir = root / "docs/unidad_iii/figuras"
    model_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    for name, estimator in estimators.items():
        scores = cross_validate(
            estimator, X_train, y_train, cv=cv, groups=groups_train,
            scoring=SCORING, n_jobs=1, error_score="raise",
        )
        fitted = estimator.fit(X_train, y_train)
        train_pred = fitted.predict(X_train)
        test_pred = fitted.predict(X_test)
        train_metrics = _metrics(y_train.to_numpy(), train_pred)
        test_metrics = _metrics(y_test.to_numpy(), test_pred)
        row: dict[str, Any] = {"model": name}
        row.update({f"train_{key}": val for key, val in train_metrics.items()})
        row.update({f"test_{key}": val for key, val in test_metrics.items()})
        row.update({
            "cv_mae_mean": float(-scores["test_mae"].mean()),
            "cv_mae_std": float(scores["test_mae"].std(ddof=1)),
            "cv_rmse_mean": float(-scores["test_rmse"].mean()),
            "cv_rmse_std": float(scores["test_rmse"].std(ddof=1)),
            "cv_r2_mean": float(scores["test_r2"].mean()),
            "cv_r2_std": float(scores["test_r2"].std(ddof=1)),
            "train_test_rmse_gap": float(test_metrics["rmse"] - train_metrics["rmse"]),
        })
        result_rows.append(row)
        prediction_rows[name] = test_pred
        joblib.dump(fitted, model_dir / f"{name.lower()}_base.joblib", compress=3)

    metrics = pd.DataFrame(result_rows)
    metric_path = result_dir / "regresion_metricas_base.csv"
    metrics.to_csv(metric_path, index=False, encoding="utf-8")
    predictions = pd.DataFrame({"row_index": test_index, "weight_true": y_test.to_numpy()})
    for name, pred in prediction_rows.items():
        predictions[name] = pred
    prediction_path = result_dir / "regresion_predicciones_test_base.csv"
    predictions.to_csv(prediction_path, index=False, encoding="utf-8")

    fig, axes = plt.subplots(1, len(prediction_rows), figsize=(15, 4.5), sharex=True, sharey=True)
    low, high = float(y_test.min()), float(y_test.max())
    for ax, (name, pred) in zip(axes, prediction_rows.items()):
        ax.scatter(y_test, pred, s=14, alpha=0.55, color="#2F6690")
        ax.plot([low, high], [low, high], color="#9B2226", linestyle="--", linewidth=1)
        ax.set_title(name.replace("Regressor", ""))
        ax.set_xlabel("Peso real (kg)")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Peso predicho (kg)")
    fig.suptitle("Regresión base: predicción de Weight en test reservado")
    fig.tight_layout()
    figure_path = figure_dir / "regresion_predicciones_test_base.png"
    fig.savefig(figure_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    grouped_cv = [
        {"fold": fold + 1, "train_rows": len(train), "validation_rows": len(valid),
         "group_overlap": len(set(groups_train[train]).intersection(groups_train[valid]))}
        for fold, (train, valid) in enumerate(cv.split(X_train, y_train, groups_train))
    ]
    metadata = {
        "task": "regression",
        "target": "Weight",
        "excluded_predictors": ["Weight", "NObeyesdad"],
        "feature_columns": features,
        "input_sha256": u2_manifest["output_sha256_bytes"],
        "raw_sha256": u2_manifest["input_sha256_bytes"],
        "random_state": RANDOM_STATE,
        "split": split_summary(frame, train_index, test_index, groups),
        "cv": {"method": "GroupKFold", "folds": grouped_cv},
        "python": __import__("platform").python_version(),
        "pandas": pd.__version__, "numpy": np.__version__, "scikit_learn": sklearn.__version__,
        "metrics_csv_sha256": sha256(metric_path),
        "predictions_csv_sha256": sha256(prediction_path),
        "figure_sha256": sha256(figure_path),
        "models": {
            path.name: sha256(path) for path in sorted(model_dir.glob("*_base.joblib"))
        },
        "metric_note": "CV values are grouped out-of-fold scores computed only on training rows; test is held back from fit and CV.",
    }
    (result_dir / "regresion_manifest_base.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"metrics": metrics, "metadata": metadata, "metric_path": metric_path, "figure_path": figure_path}
