import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib, os
path = "../../data/churn.csv"
BINARY_COLS = ["gender","Partner","Dependents","PhoneService","PaperlessBilling"]

CAT_COLS = [
    "MultipleLines","InternetService","OnlineSecurity","OnlineBackup",
    "DeviceProtection","TechSupport","StreamingTV","StreamingMovies",
    "Contract","PaymentMethod"
]

SERVICE_COLS = [
    "PhoneService","MultipleLines","InternetService","OnlineSecurity",
    "OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"
]

CONTRACT_RISK_MAP = {
    "Month-to-month": 2,
    "One year": 1,
    "Two year": 0
}

def _basic_clean(df):
    df = df.copy()
    if "customerID" in df.columns:
        df.drop("customerID", axis=1, inplace=True)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)
    if "Churn" in df.columns and df["Churn"].dtype == object:
        df["Churn"] = (df["Churn"] == "Yes").astype(int)

    return df

def _feature_engineer(df):
    df = df.copy()

    df["ChargesPerMonth"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["MonthlyToTotal"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)

    df["TenureBucket"] = pd.cut(
        df["tenure"],
        bins=[-1, 12, 36, 72],
        labels=[0, 1, 2]
    ).astype(int)

    no_vals = {"No", "No internet service", "No phone service"}

    df["ServiceCount"] = df[SERVICE_COLS].apply(
        lambda r: sum(v not in no_vals for v in r),
        axis=1
    )

    df["HighValue"] = (df["MonthlyCharges"] > df["MonthlyCharges"].median()).astype(int)
    df["ContractRisk"] = df["Contract"].map(CONTRACT_RISK_MAP)

    return df

class ChurnPreprocessor:
    def __init__(self):
        self.encoders = {}
        self.feature_columns = []

    def fit_transform(self, df):
        df = _basic_clean(df)
        df = _feature_engineer(df)

        for col in BINARY_COLS:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.encoders[col] = le

        cols_to_encode = [c for c in CAT_COLS if c in df.columns]
        df = pd.get_dummies(df, columns=cols_to_encode, drop_first=True)

        df = df.replace({True: 1, False: 0})

        y = df["Churn"]
        X = df.drop("Churn", axis=1)

        self.feature_columns = X.columns.tolist()

        print(f"Preprocessing complete. Features: {len(self.feature_columns)}")

        return X, y

    def transform(self, df):
        df = _basic_clean(df)
        df = _feature_engineer(df)

        for col in BINARY_COLS:
            if col in df.columns and col in self.encoders:
                df[col] = self.encoders[col].transform(df[col])

        cols_to_encode = [c for c in CAT_COLS if c in df.columns]
        df = pd.get_dummies(df, columns=cols_to_encode, drop_first=True)

        df = df.replace({True: 1, False: 0})

        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0

        return df[self.feature_columns]

    def save(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        joblib.dump(self, path)
        print(f"Preprocessor saved to {path}")

    @classmethod
    def load(cls, path):
        obj = joblib.load(path)
        print(f"Preprocessor loaded from {path}")
        return obj