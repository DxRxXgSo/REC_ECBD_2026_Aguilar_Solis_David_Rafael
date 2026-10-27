"""Train-only preprocessing and model pipelines for Unit III."""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


REGRESSION_FEATURES = [
    "Gender", "Age", "Height", "family_history_with_overweight", "FAVC", "FCVC",
    "NCP", "CAEC", "SMOKE", "CH2O", "SCC", "FAF", "TUE", "CALC", "MTRANS",
]
CLASSIFICATION_A_FEATURES = REGRESSION_FEATURES + ["Weight"]
CLASSIFICATION_B_FEATURES = [
    "Gender", "Age", "family_history_with_overweight", "FAVC", "FCVC", "NCP",
    "CAEC", "SMOKE", "CH2O", "SCC", "FAF", "TUE", "CALC", "MTRANS",
]
NUMERIC = ["Age", "Height", "Weight", "FCVC", "NCP", "CH2O", "FAF", "TUE"]


def feature_columns(task: str, scenario: str | None = None) -> list[str]:
    if task == "regression":
        return REGRESSION_FEATURES.copy()
    if task == "classification" and scenario == "A":
        return CLASSIFICATION_A_FEATURES.copy()
    if task == "classification" and scenario == "B":
        return CLASSIFICATION_B_FEATURES.copy()
    raise ValueError(f"Tarea/escenario no válido: task={task}, scenario={scenario}")


def make_preprocessor(frame: pd.DataFrame, scale_numeric: bool = True) -> ColumnTransformer:
    numeric_columns = [column for column in frame.columns if column in NUMERIC]
    categorical_columns = [column for column in frame.columns if column not in numeric_columns]
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler() if scale_numeric else "passthrough"),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric, numeric_columns),
        ("categorical", categorical, categorical_columns),
    ], remainder="drop")


def make_pipeline(frame: pd.DataFrame, estimator: Any, scale_numeric: bool = True) -> Pipeline:
    return Pipeline([
        ("preprocess", make_preprocessor(frame, scale_numeric=scale_numeric)),
        ("model", estimator),
    ])
