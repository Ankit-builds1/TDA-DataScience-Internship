from pathlib import Path
import json
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
DEPLOYMENT = ROOT / "deployment"
FIGURES = REPORTS / "figures"
MODELS = ROOT / "models"
RANDOM_STATE = 42


def ensure_dirs():
    for path in [REPORTS, FIGURES, MODELS, DEPLOYMENT]:
        path.mkdir(parents=True, exist_ok=True)


def load_data():
    return {
        "sales": pd.read_csv(DATA / "sales_data.csv"),
        "houses": pd.read_csv(DATA / "house_prices.csv"),
        "churn": pd.read_csv(DATA / "customer_churn.csv"),
    }


def engineer_churn(df):
    out = df.copy()
    tenure_safe = out["Tenure"].replace(0, 1)
    out["LifetimeValueProxy"] = out["MonthlyCharges"] * out["Tenure"]
    out["AvgChargePerTenure"] = out["TotalCharges"] / tenure_safe
    out["MonthlyToTotalRatio"] = (out["MonthlyCharges"] / out["TotalCharges"].replace(0, np.nan)).fillna(0)
    out["ContractRiskScore"] = out["Contract"].map({"Month-to-month": 3, "One year": 2, "Two year": 1}).fillna(0)
    out["PaperlessBillingFlag"] = out["PaperlessBilling"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
    out["AutoPaymentFlag"] = out["PaymentMethod"].isin(["Credit Card", "Bank Transfer"]).astype(int)
    out["HighMonthlyChargeFlag"] = (out["MonthlyCharges"] >= out["MonthlyCharges"].quantile(0.75)).astype(int)
    out["ShortTenureFlag"] = (out["Tenure"] <= 12).astype(int)
    return out


def churn_pipeline():
    numeric = [
        "Tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen",
        "LifetimeValueProxy", "AvgChargePerTenure", "MonthlyToTotalRatio",
        "ContractRiskScore", "PaperlessBillingFlag", "AutoPaymentFlag",
        "HighMonthlyChargeFlag", "ShortTenureFlag",
    ]
    categorical = ["Contract", "PaymentMethod", "PaperlessBilling"]
    preprocess = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ])
    model = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE)
    return Pipeline([("preprocess", preprocess), ("model", model)]), numeric + categorical


def analyze_sales(sales):
    sales = sales.copy()
    sales["Date"] = pd.to_datetime(sales["Date"])
    summary = {
        "total_sales": float(sales["Total_Sales"].sum()),
        "avg_order_value": float(sales["Total_Sales"].mean()),
        "top_product": str(sales.groupby("Product")["Total_Sales"].sum().idxmax()),
        "top_region": str(sales.groupby("Region")["Total_Sales"].sum().idxmax()),
    }
    monthly = sales.set_index("Date").resample("ME")["Total_Sales"].sum().reset_index()
    monthly.to_csv(REPORTS / "monthly_sales_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(monthly["Date"], monthly["Total_Sales"], marker="o", color="#2A9D8F")
    ax.set_title("Monthly Sales Trend", fontsize=14, weight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(FIGURES / "sales_trend.png", dpi=180)
    plt.close(fig)
    return summary


def analyze_houses(houses):
    X = pd.get_dummies(houses[["Area", "Bedrooms", "Bathrooms", "Age", "Location", "Property_Type"]], drop_first=True)
    y = houses["Price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    model = RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    summary = {
        "house_mae": float(mean_absolute_error(y_test, pred)),
        "house_r2": float(r2_score(y_test, pred)),
        "avg_price": float(houses["Price"].mean()),
    }
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_test, pred, color="#457B9D", alpha=0.75)
    lower, upper = min(y_test.min(), pred.min()), max(y_test.max(), pred.max())
    ax.plot([lower, upper], [lower, upper], color="#E76F51", linewidth=2)
    ax.set_title("House Model: Actual vs Predicted", fontsize=13, weight="bold")
    ax.set_xlabel("Actual Price")
    ax.set_ylabel("Predicted Price")
    fig.tight_layout()
    fig.savefig(FIGURES / "house_predictions.png", dpi=180)
    plt.close(fig)
    return summary


def train_churn(churn):
    df = engineer_churn(churn)
    pipe, features = churn_pipeline()
    X = df[features]
    y = df["Churn"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
    param_grid = {
        "model__n_estimators": [100, 200],
        "model__max_depth": [4, 6, None],
        "model__min_samples_leaf": [1, 3],
    }
    search = GridSearchCV(pipe, param_grid, scoring="f1", cv=3, n_jobs=-1)
    search.fit(X_train, y_train)
    best = search.best_estimator_
    pred = best.predict(X_test)
    proba = best.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, pred)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "best_params": search.best_params_,
        "churn_rate": float(df["Churn"].mean()),
    }
    with open(MODELS / "churn_model.pkl", "wb") as f:
        pickle.dump(best, f)
    with open(MODELS / "feature_columns.json", "w", encoding="utf-8") as f:
        json.dump(features, f, indent=2)
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Stayed", "Churned"]
    counts = y.map({0: "Stayed", 1: "Churned"}).value_counts().reindex(labels)
    ax.bar(labels, counts, color=["#2A9D8F", "#E76F51"])
    ax.set_title("Customer Churn Distribution", fontsize=14, weight="bold")
    ax.set_ylabel("Customers")
    fig.tight_layout()
    fig.savefig(FIGURES / "churn_distribution.png", dpi=180)
    plt.close(fig)
    return metrics


def write_outputs(sales_summary, house_summary, churn_metrics):
    summary = {
        "business_problem": "Predict customer churn and summarize supporting sales/property portfolio analytics.",
        "success_metric": "F1 score and recall for churn risk identification.",
        "sales_summary": sales_summary,
        "house_summary": house_summary,
        "churn_model": churn_metrics,
    }
    (REPORTS / "capstone_metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md = f"""# Week 12 Final Capstone: Comprehensive Data Science Project

## Executive Summary
This project completes an end-to-end data science workflow across sales, housing, and customer churn datasets. The deployable model focuses on churn prediction because customer retention has direct business impact.

## Business Problem
The company needs a repeatable way to identify customers likely to leave, understand revenue patterns, and present model-backed recommendations in a portfolio-ready format.

## Success Metrics
- Primary metric: churn prediction F1 score
- Supporting metrics: recall, ROC-AUC, house price R2, and sales growth patterns

## Results
- Churn rate: {churn_metrics['churn_rate']:.2%}
- Churn model accuracy: {churn_metrics['accuracy']:.4f}
- Churn model recall: {churn_metrics['recall']:.4f}
- Churn model F1 score: {churn_metrics['f1']:.4f}
- Churn model ROC-AUC: {churn_metrics['roc_auc']:.4f}
- Total sales analyzed: {sales_summary['total_sales']:,.0f}
- Top product: {sales_summary['top_product']}
- Top region: {sales_summary['top_region']}
- House price model R2: {house_summary['house_r2']:.4f}

## Recommendations
1. Use the churn model to flag high-risk customers for retention outreach.
2. Prioritize high-value customers with short tenure and high monthly charges.
3. Use sales trend monitoring to align campaign timing with revenue peaks.
4. Keep the model retraining process repeatable through the included source modules and deployment files.

## Deployment Demo
The `deployment/app.py` file provides a Flask prediction API and simple web form. The saved model is stored in `models/churn_model.pkl`.
"""
    (REPORTS / "business_report.md").write_text(md, encoding="utf-8")


def main():
    ensure_dirs()
    data = load_data()
    sales_summary = analyze_sales(data["sales"])
    house_summary = analyze_houses(data["houses"])
    churn_metrics = train_churn(data["churn"])
    write_outputs(sales_summary, house_summary, churn_metrics)
    print("FINAL CAPSTONE PROJECT")
    print(f"Churn F1: {churn_metrics['f1']:.4f}")
    print(f"Churn Recall: {churn_metrics['recall']:.4f}")
    print(f"Churn ROC-AUC: {churn_metrics['roc_auc']:.4f}")
    print(f"Top Product: {sales_summary['top_product']}")
    print(f"House R2: {house_summary['house_r2']:.4f}")


if __name__ == "__main__":
    main()
