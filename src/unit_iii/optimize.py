"""Training-only hyperparameter search and final reserved-test evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score,
                             recall_score)
from sklearn.model_selection import GridSearchCV

from .data import (LABELS, RANDOM_STATE, classification_cv, regression_cv,
                   sha256, split_indices, split_summary, validate_input)
from .pipelines import (REGRESSION_FEATURES, feature_columns, make_pipeline)


def _grid_search(estimator: Any, grid: dict[str, list[Any]], X: pd.DataFrame,
                 y: pd.Series, groups: np.ndarray, cv: Any, scoring: str) -> GridSearchCV:
    search = GridSearchCV(estimator, grid, scoring=scoring, cv=cv, n_jobs=1,
                          refit=True, error_score="raise", return_train_score=True)
    search.fit(X, y, groups=groups)
    return search


def run_optimization(root: Path) -> dict[str, Any]:
    frame, u2_manifest = validate_input(root)
    train_index, test_index, groups = split_indices(frame)
    y = frame["NObeyesdad"]
    groups_train = groups[train_index]
    model_dir = root / "modelos/unidad_iii"
    result_dir = root / "docs/unidad_iii/resultados"
    for path in (model_dir, result_dir):
        path.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Any] = {}
    prediction_rows: dict[str, np.ndarray] = {}
    # Regression search uses only training rows and grouped CV. Test is first read
    # for scoring after GridSearchCV has selected/refit on the full training set.
    Xr = frame.iloc[train_index][REGRESSION_FEATURES]
    yr = frame.iloc[train_index]["Weight"]
    regression_search = _grid_search(
        make_pipeline(Xr, RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1), scale_numeric=False),
        {"model__n_estimators": [100, 150], "model__max_depth": [None, 14],
         "model__min_samples_leaf": [1, 3]},
        Xr, yr, groups_train, regression_cv(groups_train), "neg_root_mean_squared_error",
    )
    Xr_test = frame.iloc[test_index][REGRESSION_FEATURES]
    yr_test = frame.iloc[test_index]["Weight"]
    pred = regression_search.best_estimator_.predict(Xr_test)
    prediction_rows["regression_randomforest_tuned"] = pred
    rows.append({
        "task": "regression", "scenario": "all_allowed_features", "model": "RandomForestRegressor",
        "best_params": json.dumps(regression_search.best_params_, sort_keys=True),
        "cv_best_score": float(-regression_search.best_score_),
        "test_mae": float(mean_absolute_error(yr_test, pred)),
        "test_rmse": float(np.sqrt(mean_squared_error(yr_test, pred))),
        "test_r2": float(r2_score(yr_test, pred)),
    })
    fitted_models["regression_randomforest_tuned"] = regression_search.best_estimator_

    for scenario in ("A", "B"):
        columns = feature_columns("classification", scenario)
        X_train = frame.iloc[train_index][columns]
        y_train = y.iloc[train_index]
        X_test = frame.iloc[test_index][columns]
        y_test = y.iloc[test_index]
        models = [
            ("LogisticRegression", make_pipeline(
                X_train, LogisticRegression(max_iter=2000, random_state=RANDOM_STATE), scale_numeric=True),
             {"model__C": [0.1, 1.0, 10.0]}),
            ("RandomForestClassifier", make_pipeline(
                X_train, RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1), scale_numeric=False),
             {"model__n_estimators": [100, 150], "model__max_depth": [None, 14],
              "model__min_samples_leaf": [1, 3]}),
        ]
        for model_name, estimator, grid in models:
            search = _grid_search(estimator, grid, X_train, y_train, groups_train,
                                  classification_cv(), "f1_macro")
            test_pred = search.best_estimator_.predict(X_test)
            key = f"classification_{scenario}_{model_name.lower()}_tuned"
            prediction_rows[key] = test_pred
            rows.append({
                "task": "classification", "scenario": scenario, "model": model_name,
                "best_params": json.dumps(search.best_params_, sort_keys=True),
                "cv_best_score": float(search.best_score_),
                "test_accuracy": float(accuracy_score(y_test, test_pred)),
                "test_precision_macro": float(precision_score(y_test, test_pred, average="macro", zero_division=0)),
                "test_recall_macro": float(recall_score(y_test, test_pred, average="macro", zero_division=0)),
                "test_f1_macro": float(f1_score(y_test, test_pred, average="macro", zero_division=0)),
                "classes": "|".join(LABELS),
            })
            fitted_models[key] = search.best_estimator_

    metrics = pd.DataFrame(rows)
    metrics_path = result_dir / "optimizacion_metricas_test.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8")
    predictions_path = result_dir / "optimizacion_predicciones_test.csv"
    prediction_table: dict[str, Any] = {
        "row_index": test_index,
        "weight_true": yr_test.to_numpy(),
        "class_true": y.iloc[test_index].to_numpy(),
    }
    prediction_table.update(prediction_rows)
    pd.DataFrame(prediction_table).to_csv(predictions_path, index=False, encoding="utf-8")
    model_hashes: dict[str, str] = {}
    for name, model in fitted_models.items():
        path = model_dir / f"{name}.joblib"
        joblib.dump(model, path, compress=3)
        restored = joblib.load(path)
        if not np.array_equal(restored.predict(
            Xr_test if name == "regression_randomforest_tuned" else
            frame.iloc[test_index][feature_columns("classification", name.split("_")[1])]
        ), prediction_rows[name]):
            raise RuntimeError(f"Predicciones distintas tras recargar {path.name}")
        model_hashes[path.name] = sha256(path)
    summary_path = result_dir / "optimizacion_manifest.json"
    summary = {
        "task": "hyperparameter_optimization", "input_sha256": u2_manifest["output_sha256_bytes"],
        "raw_sha256": u2_manifest["input_sha256_bytes"], "random_state": RANDOM_STATE,
        "split": split_summary(frame, train_index, test_index, groups),
        "search_scope": "All GridSearchCV selection, refitting, and CV restricted to train. Reserved test evaluated once after each best model is fixed.",
        "regression_cv": "GroupKFold(5), selection metric negative RMSE",
        "classification_cv": "StratifiedGroupKFold(5), selection metric macro F1",
        "metrics_sha256": sha256(metrics_path),
        "predictions_sha256": sha256(predictions_path),
        "serialized_prediction_roundtrip": "PASS for all five tuned pipelines",
        "models": model_hashes,
        "versions": {"python": __import__("platform").python_version(),
                     "pandas": pd.__version__, "numpy": np.__version__},
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"metrics": metrics, "manifest": summary, "metrics_path": metrics_path,
            "manifest_path": summary_path}
