from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from lightgbm import LGBMClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, StackingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.models.preprocessor import ChurnPreprocessor
from app.utils.feature_helpers import clean_training_frame


def evaluate_model(name: str, model, X_test, y_test) -> dict:
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.35).astype(int)
    return {
        "model": name,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "precision": round(float(precision_score(y_test, predictions)), 4),
        "recall": round(float(recall_score(y_test, predictions)), 4),
    }


def main() -> None:
    warnings.filterwarnings("ignore", message="X does not have valid feature names")
    data_path = PROJECT_ROOT / "data" / "churn.csv"
    artifacts_dir = BACKEND_DIR / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)
    df = clean_training_frame(df)

    preprocessor = ChurnPreprocessor()
    prepared = preprocessor.fit_transform(df)
    X = prepared.drop(columns=["Churn"])
    y = prepared["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    smote = SMOTE(random_state=42)
    scaler = StandardScaler()
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    X_train_scaled = scaler.fit_transform(X_train_resampled)
    X_test_scaled = scaler.transform(X_test)

    logistic_model = LogisticRegression(max_iter=500, random_state=42)
    logistic_model.fit(X_train_scaled, y_train_resampled)

    random_forest_model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=1,
    )
    random_forest_model.fit(X_train_resampled, y_train_resampled)

    xgb_model = xgb.XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
        n_jobs=1,
    )
    lgb_model = LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=40,
        random_state=42,
        n_jobs=1,
        verbose=-1,
    )
    gb_model = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        random_state=42,
    )
    rf_model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=1,
    )
    stack = StackingClassifier(
        estimators=[
            ("xgb", xgb_model),
            ("lgb", lgb_model),
            ("gb", gb_model),
            ("rf", rf_model),
        ],
        final_estimator=LogisticRegression(max_iter=500),
        cv=5,
        stack_method="predict_proba",
        n_jobs=1,
    )
    stack.fit(X_train_scaled, y_train_resampled)

    metrics = {
        "stacking_ensemble": evaluate_model("Stacking Ensemble", stack, X_test_scaled, y_test),
        "logistic_regression": evaluate_model("Logistic Regression", logistic_model, X_test_scaled, y_test),
        "random_forest": evaluate_model("Random Forest", random_forest_model, X_test, y_test),
    }

    importance = permutation_importance(
        stack,
        X_test_scaled,
        y_test,
        n_repeats=3,
        random_state=42,
        n_jobs=1,
        scoring="roc_auc",
    )
    ranked_features = sorted(
        zip(X.columns, importance.importances_mean),
        key=lambda item: item[1],
        reverse=True,
    )[:12]
    feature_importance = [
        {"feature": feature, "importance": round(float(score), 5)}
        for feature, score in ranked_features
    ]

    metadata = {
        "feature_medians": {column: float(X[column].median()) for column in X.columns},
        "feature_importance": feature_importance,
        "metrics": metrics,
        "classification_threshold": 0.35,
        "training_rows": int(len(df)),
    }

    joblib.dump(stack, artifacts_dir / "model.pkl")
    joblib.dump(scaler, artifacts_dir / "scaler.pkl")
    joblib.dump(preprocessor, artifacts_dir / "preprocessor.pkl")
    joblib.dump(list(X.columns), artifacts_dir / "feature_columns.pkl")
    joblib.dump(logistic_model, artifacts_dir / "logistic_regression.pkl")
    joblib.dump(random_forest_model, artifacts_dir / "random_forest.pkl")
    with (artifacts_dir / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    print("Artifacts saved to", artifacts_dir)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
