from __future__ import annotations

import json
from functools import lru_cache

import joblib
import pandas as pd

from app.config import settings


@lru_cache(maxsize=1)
def get_model():
    return joblib.load(settings.artifacts_dir / "model.pkl")


@lru_cache(maxsize=1)
def get_scaler():
    return joblib.load(settings.artifacts_dir / "scaler.pkl")


@lru_cache(maxsize=1)
def get_preprocessor():
    preprocessor = joblib.load(settings.artifacts_dir / "preprocessor.pkl")
    if getattr(preprocessor, "monthly_charges_median", None) is None:
        median = get_metadata().get("feature_medians", {}).get("MonthlyCharges")
        if median is not None:
            preprocessor.monthly_charges_median = float(median)
    return preprocessor


@lru_cache(maxsize=1)
def get_feature_columns() -> list[str]:
    return joblib.load(settings.artifacts_dir / "feature_columns.pkl")


@lru_cache(maxsize=1)
def get_metadata() -> dict:
    path = settings.artifacts_dir / "metadata.json"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def get_dataset() -> pd.DataFrame:
    return pd.read_csv(settings.data_path)
