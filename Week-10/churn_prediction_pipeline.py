from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "churn_data.csv"
TARGET = "Churn"
RANDOM_STATE = 42


def load_data():
    df = pd.read_csv(DATA_PATH)
    required = [
        "CustomerID",
        "Tenure",
        "MonthlyCharges",
        "TotalCharges",
        "Contract",
        "PaymentMethod",
        "PaperlessBilling",
        "SeniorCitizen",
        "Churn",
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def create_engineered_features(df):
    engineered = df.copy()
    tenure_safe = engineered["Tenure"].replace(0, 1)
    monthly_safe = engineered["MonthlyCharges"].replace(0, np.nan)

    engineered["AvgChargePerTenure"] = engineered["TotalCharges"] / tenure_safe
    engineered["LifetimeValueProxy"] = engineered["MonthlyCharges"] * engineered["Tenure"]
    engineered["ChargeGap"] = engineered["TotalCharges"] - engineered["LifetimeValueProxy"]
    engineered["TenureGroup"] = pd.cut(
        engineered["Tenure"],
        bins=[0, 12, 36, 72],
        labels=["New", "Established", "Loyal"],
        include_lowest=True,
    ).astype(str)
    engineered["MonthlyToTotalRatio"] = (engineered["MonthlyCharges"] / engineered["TotalCharges"].replace(0, np.nan)).fillna(0)
    engineered["HighMonthlyChargeFlag"] = (engineered["MonthlyCharges"] >= engineered["MonthlyCharges"].quantile(0.75)).astype(int)
    engineered["LongTenureFlag"] = (engineered["Tenure"] >= 36).astype(int)
    engineered["ContractRiskScore"] = engineered["Contract"].map({"Month-to-month": 3, "One year": 2, "Two year": 1}).fillna(0)
    engineered["PaperlessBillingFlag"] = engineered["PaperlessBilling"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
    engineered["AutoPaymentFlag"] = engineered["PaymentMethod"].isin(["Credit Card", "Bank Transfer"]).astype(int)
    engineered["MonthlyChargeIntensity"] = (engineered["MonthlyCharges"] / monthly_safe.mean()).fillna(0)
    return engineered


def detect_outliers(df):
    rows = []
    for col in ["Tenure", "MonthlyCharges", "TotalCharges", "AvgChargePerTenure", "LifetimeValueProxy"]:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        iqr_count = int(((df[col] < lower) | (df[col] > upper)).sum())
        z = (df[col] - df[col].mean()) / df[col].std(ddof=0)
        z_count = int((z.abs() > 3).sum())
        rows.append({
            "Feature": col,
            "IQR_Lower": lower,
            "IQR_Upper": upper,
            "IQR_Outliers": iqr_count,
            "ZScore_Outliers": z_count,
        })
    return pd.DataFrame(rows)


def cap_outliers_iqr(df, columns):
    capped = df.copy()
    caps = []
    for col in columns:
        q1 = capped[col].quantile(0.25)
        q3 = capped[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        capped[col] = capped[col].clip(lower, upper)
        caps.append({"Feature": col, "LowerCap": lower, "UpperCap": upper})
    return capped, pd.DataFrame(caps)


def build_preprocessing_pipeline(numeric_features, one_hot_features, ordinal_features, binary_features):
    contract_order = [["Month-to-month", "One year", "Two year"]]
    return ColumnTransformer(
        transformers=[
            ("standard_numeric", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), numeric_features),
            ("one_hot", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]), one_hot_features),
            ("ordinal", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OrdinalEncoder(categories=contract_order)),
            ]), ordinal_features),
            ("binary_label", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
            ]), binary_features),
        ],
        remainder="drop",
    )


def evaluate_classifier(model, X_test, y_test):
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    return {
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions, zero_division=0),
        "Recall": recall_score(y_test, predictions, zero_division=0),
        "F1": f1_score(y_test, predictions, zero_division=0),
        "ROC_AUC": roc_auc_score(y_test, probabilities),
    }, predictions, probabilities


def run_pipeline():
    raw = load_data()
    df = create_engineered_features(raw)
    outlier_report = detect_outliers(df)
    df_capped, cap_report = cap_outliers_iqr(
        df,
        ["MonthlyCharges", "TotalCharges", "AvgChargePerTenure", "LifetimeValueProxy", "ChargeGap"],
    )

    binary_maps = {
        "PaperlessBilling": {"No": 0, "Yes": 1},
        "SeniorCitizen": {0: 0, 1: 1},
        "HighMonthlyChargeFlag": {0: 0, 1: 1},
        "LongTenureFlag": {0: 0, 1: 1},
        "AutoPaymentFlag": {0: 0, 1: 1},
    }
    for col, mapping in binary_maps.items():
        df_capped[col] = df_capped[col].map(mapping).fillna(df_capped[col]).astype(int)

    numeric_features = [
        "Tenure",
        "MonthlyCharges",
        "TotalCharges",
        "AvgChargePerTenure",
        "LifetimeValueProxy",
        "ChargeGap",
        "MonthlyToTotalRatio",
        "MonthlyChargeIntensity",
        "ContractRiskScore",
    ]
    one_hot_features = ["PaymentMethod", "TenureGroup"]
    ordinal_features = ["Contract"]
    binary_features = ["PaperlessBilling", "SeniorCitizen", "HighMonthlyChargeFlag", "LongTenureFlag", "AutoPaymentFlag"]
    feature_columns = numeric_features + one_hot_features + ordinal_features + binary_features

    X = df_capped[feature_columns]
    y = df_capped[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    standard_pipeline = Pipeline(steps=[
        ("preprocess", build_preprocessing_pipeline(numeric_features, one_hot_features, ordinal_features, binary_features)),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    standard_pipeline.fit(X_train, y_train)
    metrics, predictions, probabilities = evaluate_classifier(standard_pipeline, X_test, y_test)

    minmax_preprocessor = ColumnTransformer(
        transformers=[
            ("minmax_numeric", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", MinMaxScaler()),
            ]), numeric_features),
            ("one_hot", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]), one_hot_features),
            ("ordinal", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OrdinalEncoder(categories=[["Month-to-month", "One year", "Two year"]])),
            ]), ordinal_features),
            ("binary_label", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
            ]), binary_features),
        ]
    )
    minmax_pipeline = Pipeline(steps=[
        ("preprocess", minmax_preprocessor),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    minmax_pipeline.fit(X_train, y_train)
    minmax_metrics, _, _ = evaluate_classifier(minmax_pipeline, X_test, y_test)

    rf_pipeline = Pipeline(steps=[
        ("preprocess", build_preprocessing_pipeline(numeric_features, one_hot_features, ordinal_features, binary_features)),
        ("model", RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    rf_pipeline.fit(X_train, y_train)
    rf_metrics, _, _ = evaluate_classifier(rf_pipeline, X_test, y_test)

    comparison = pd.DataFrame([
        {"Pipeline": "StandardScaler + Logistic Regression", **metrics},
        {"Pipeline": "MinMaxScaler + Logistic Regression", **minmax_metrics},
        {"Pipeline": "StandardScaler + Random Forest", **rf_metrics},
    ])

    feature_names = standard_pipeline.named_steps["preprocess"].get_feature_names_out()
    clean_feature_names = [name.replace("standard_numeric__", "").replace("one_hot__", "").replace("ordinal__", "").replace("binary_label__", "") for name in feature_names]
    coefficients = pd.DataFrame({
        "Feature": clean_feature_names,
        "Coefficient": standard_pipeline.named_steps["model"].coef_[0],
    })
    coefficients["AbsCoefficient"] = coefficients["Coefficient"].abs()
    coefficients = coefficients.sort_values("AbsCoefficient", ascending=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7, 5))
    raw[TARGET].map({0: "Stayed", 1: "Churned"}).value_counts().reindex(["Stayed", "Churned"]).plot(
        kind="bar", ax=ax, color=["#2A9D8F", "#E76F51"]
    )
    ax.set_title("Customer Churn Distribution", fontsize=14, weight="bold")
    ax.set_xlabel("Customer Status")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(ROOT / "churn_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    top_coef = coefficients.head(10).sort_values("AbsCoefficient")
    ax.barh(top_coef["Feature"], top_coef["AbsCoefficient"], color="#457B9D")
    ax.set_title("Top Selected Features by Logistic Regression Coefficient", fontsize=13, weight="bold")
    ax.set_xlabel("Absolute Coefficient")
    fig.tight_layout()
    fig.savefig(ROOT / "feature_selection.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    cm = confusion_matrix(y_test, predictions)
    ax.imshow(cm, cmap="Blues")
    ax.set_title("Confusion Matrix - Churn Prediction", fontsize=13, weight="bold")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_xticks([0, 1], labels=["Stay", "Churn"])
    ax.set_yticks([0, 1], labels=["Stay", "Churn"])
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="#111111", fontsize=12)
    fig.tight_layout()
    fig.savefig(ROOT / "confusion_matrix.png", dpi=180)
    plt.close(fig)

    outlier_report.to_csv(ROOT / "outlier_report.csv", index=False)
    cap_report.to_csv(ROOT / "outlier_caps.csv", index=False)
    comparison.to_csv(ROOT / "pipeline_model_metrics.csv", index=False)
    coefficients.to_csv(ROOT / "selected_features.csv", index=False)
    pd.DataFrame(classification_report(y_test, predictions, output_dict=True)).transpose().to_csv(ROOT / "classification_report.csv")

    preprocessing_report = f"""# Week 10: Customer Churn Preprocessing Report

## Project Overview
This project prepares customer churn data for machine learning by applying categorical encoding, feature scaling, outlier handling, feature engineering, feature selection, and an end-to-end preprocessing pipeline.

## Dataset Summary
- Source file: `churn_data.csv`
- Rows: {len(raw)}
- Columns: {len(raw.columns)}
- Target: `Churn`
- Churn rate: {raw[TARGET].mean():.2%}

## Preprocessing Steps
1. Validated required columns and checked data types.
2. Created engineered customer behavior and value features.
3. Detected outliers using IQR and Z-score methods.
4. Capped high-variance numeric features using IQR boundaries.
5. Applied three encoding methods: binary label mapping, ordinal encoding, and one-hot encoding.
6. Compared two scaling methods: StandardScaler and MinMaxScaler.
7. Built complete scikit-learn pipelines for repeatable preprocessing and modeling.

## Encoding Methods Implemented
- Binary label encoding: `PaperlessBilling`, `SeniorCitizen`, `HighMonthlyChargeFlag`, `LongTenureFlag`, `AutoPaymentFlag`
- Ordinal encoding: `Contract`, ordered from month-to-month to two-year
- One-hot encoding: `PaymentMethod`, `TenureGroup`

## Scaling Techniques Implemented
- StandardScaler for the primary logistic regression pipeline
- MinMaxScaler for comparison against the primary pipeline

## Model and Pipeline Results
{comparison.to_markdown(index=False, floatfmt=".4f")}

## Selected Important Features
{coefficients.head(10)[["Feature", "Coefficient", "AbsCoefficient"]].to_markdown(index=False, floatfmt=".4f")}

## Testing Evidence
- Required column validation is performed before feature creation.
- Train-test split uses stratification to preserve churn distribution.
- Pipeline handles missing numeric and categorical values.
- The script regenerates metrics, outlier reports, selected features, and charts from the source CSV.
"""
    (ROOT / "preprocessing_report.md").write_text(preprocessing_report, encoding="utf-8")

    feature_doc = f"""# Feature Engineering Documentation

## Engineered Features Created
1. `AvgChargePerTenure`: total charges divided by tenure to estimate average customer value over time.
2. `LifetimeValueProxy`: monthly charges multiplied by tenure.
3. `ChargeGap`: difference between recorded total charges and estimated lifetime value.
4. `TenureGroup`: customer tenure bucket: New, Established, or Loyal.
5. `MonthlyToTotalRatio`: monthly charge compared with total charge.
6. `HighMonthlyChargeFlag`: identifies customers in the top monthly charge quartile.
7. `LongTenureFlag`: identifies customers with tenure of at least 36 months.
8. `ContractRiskScore`: assigns higher churn risk to shorter contracts.
9. `PaperlessBillingFlag`: converts paperless billing to a binary feature.
10. `AutoPaymentFlag`: identifies lower-friction payment methods.
11. `MonthlyChargeIntensity`: compares monthly charge against the dataset average.

## Rationale
These features translate raw billing and account details into business signals. They help the model detect customer value, contract commitment, billing behavior, and tenure maturity.

## Outlier Handling
Outliers were detected with both IQR boundaries and Z-score thresholds. Numeric charge/value features were capped with IQR limits instead of removed so customer records remain available for training.

## Feature Selection
Feature selection was performed using logistic regression coefficient strength after preprocessing. The top features are exported to `selected_features.csv` and visualized in `feature_selection.png`.
"""
    (ROOT / "feature_engineering_documentation.md").write_text(feature_doc, encoding="utf-8")

    print("CUSTOMER CHURN PREPROCESSING PIPELINE")
    print(f"Rows: {len(raw)}")
    print(f"Churn Rate: {raw[TARGET].mean():.2%}")
    print(f"Accuracy: {metrics['Accuracy']:.4f}")
    print(f"Precision: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"F1 Score: {metrics['F1']:.4f}")
    print(f"ROC AUC: {metrics['ROC_AUC']:.4f}")
    print("Top Features:", ", ".join(coefficients["Feature"].head(5)))
    return comparison, coefficients, outlier_report


if __name__ == "__main__":
    run_pipeline()
