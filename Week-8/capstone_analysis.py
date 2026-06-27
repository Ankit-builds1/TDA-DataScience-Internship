from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import stats
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parent


def main():
    raw = ROOT / "data" / "raw" / "customer_churn.csv"
    df = pd.read_csv(raw)
    df = df.dropna().drop_duplicates(subset=["CustomerID"])
    df["CustomerValue"] = df["MonthlyCharges"] * np.maximum(df["Tenure"], 1)
    df["TenureSegment"] = pd.cut(df["Tenure"], bins=[-1, 12, 36, 72], labels=["New", "Developing", "Loyal"])
    df.to_csv(ROOT / "data" / "cleaned_data.csv", index=False)

    churn_rate = df["Churn"].mean()
    churned = df[df["Churn"] == 1]
    retained = df[df["Churn"] == 0]
    tenure_test = stats.ttest_ind(churned["Tenure"], retained["Tenure"], equal_var=False)
    charges_test = stats.ttest_ind(churned["MonthlyCharges"], retained["MonthlyCharges"], equal_var=False)
    chi = stats.chi2_contingency(pd.crosstab(df["Contract"], df["Churn"]))

    encoded = pd.get_dummies(df[["Tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen", "Contract", "PaymentMethod", "PaperlessBilling"]], drop_first=True).astype(float)
    model = sm.Logit(df["Churn"], sm.add_constant(encoded)).fit(disp=False, maxiter=200)
    df["PredictedChurnRisk"] = model.predict(sm.add_constant(encoded))

    print("CAPSTONE BUSINESS ANALYSIS")
    print(f"Rows: {len(df)}")
    print(f"Churn rate: {churn_rate:.2%}")
    print(f"Tenure t-test p-value: {tenure_test.pvalue:.4f}")
    print(f"Monthly charge t-test p-value: {charges_test.pvalue:.4f}")
    print(f"Contract chi-square p-value: {chi.pvalue:.4f}")
    print("Cleaned data regenerated: data/cleaned_data.csv")


if __name__ == "__main__":
    main()
