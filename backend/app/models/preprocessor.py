from __future__ import annotations

import pandas as pd


class ChurnPreprocessor:
    def __init__(self) -> None:
        self.binary_cols = ["gender", "Partner", "Dependents", "PhoneService", "PaperlessBilling"]
        self.cat_cols = [
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaymentMethod",
        ]
        self.contract_map = {"Month-to-month": 2, "One year": 1, "Two year": 0}
        self.feature_columns: list[str] | None = None
        self.monthly_charges_median: float | None = None

    def _feature_engineering_base(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["ChargesPerMonth"] = df["TotalCharges"] / (df["tenure"] + 1)
        df["MonthlyToTotal"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1)
        df["TenureBucket"] = pd.cut(df["tenure"], bins=[-1, 12, 36, 72], labels=[0, 1, 2]).astype(int)

        service_cols = [
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
        ]
        df["ServiceCount"] = df[service_cols].apply(
            lambda row: sum(value not in ["No", "No internet service", "No phone service"] for value in row),
            axis=1,
        )
        df["ContractRisk"] = df["Contract"].map(self.contract_map)
        return df

    def _apply_high_value(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        median_m = self.monthly_charges_median
        if median_m is None:
            median_m = float(out["MonthlyCharges"].median())
        out["HighValue"] = (out["MonthlyCharges"] > median_m).astype(int)
        return out

    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        base = self._feature_engineering_base(df)
        return self._apply_high_value(base)

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._feature_engineering_base(df)
        self.monthly_charges_median = float(df["MonthlyCharges"].median())
        df = self._apply_high_value(df)
        for col in self.binary_cols:
            if col == "gender":
                df[col] = df[col].map({"Male": 0, "Female": 1})
            else:
                df[col] = df[col].map({"No": 0, "Yes": 1})
        df = pd.get_dummies(df, columns=self.cat_cols, drop_first=True)
        df = df.replace({True: 1, False: 0})
        self.feature_columns = df.drop("Churn", axis=1).columns.tolist()
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.feature_columns is None:
            raise ValueError("Preprocessor has not been fitted.")
        df = self._feature_engineering_base(df)
        df = self._apply_high_value(df)
        for col in self.binary_cols:
            if col == "gender":
                df[col] = df[col].map({"Male": 0, "Female": 1})
            else:
                df[col] = df[col].map({"No": 0, "Yes": 1})
        df = pd.get_dummies(df, columns=self.cat_cols, drop_first=True)
        df = df.replace({True: 1, False: 0})
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        return df[self.feature_columns]
