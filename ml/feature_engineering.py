import pandas as pd

SERVICE_COLS = [
    "PhoneService","MultipleLines","InternetService","OnlineSecurity",
    "OnlineBackup","DeviceProtection","TechSupport","StreamingTV","StreamingMovies"
]

CONTRACT_RISK_MAP = {
    "Month-to-month": 2,
    "One year": 1,
    "Two year": 0
}


def feature_engineer(df):
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