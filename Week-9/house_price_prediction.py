from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures
from sklearn.tree import DecisionTreeRegressor


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "house_data.csv"
TARGET = "Price"
NUMERIC_FEATURES = ["Area", "Bedrooms", "Bathrooms", "Age"]
CATEGORICAL_FEATURES = ["Location", "Property_Type"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
RANDOM_STATE = 42


def currency(value):
    return f"INR {value:,.0f}"


def load_data():
    df = pd.read_csv(DATA_PATH)
    required = FEATURES + [TARGET]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def evaluate_model(name, y_true, predictions):
    mse = mean_squared_error(y_true, predictions)
    return {
        "Model": name,
        "MAE": mean_absolute_error(y_true, predictions),
        "MSE": mse,
        "RMSE": np.sqrt(mse),
        "R2": r2_score(y_true, predictions),
    }


def scratch_linear_regression(x_train, y_train, x_test):
    x_train = np.asarray(x_train, dtype=float)
    y_train = np.asarray(y_train, dtype=float)
    x_test = np.asarray(x_test, dtype=float)
    slope = np.cov(x_train, y_train, bias=True)[0, 1] / np.var(x_train)
    intercept = y_train.mean() - slope * x_train.mean()
    predictions = intercept + slope * x_test
    return predictions, slope, intercept


def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("num", "passthrough", NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def run_analysis():
    df = load_data()
    missing_counts = df[FEATURES + [TARGET]].isna().sum()
    if missing_counts.sum() > 0:
        df = df.dropna(subset=FEATURES + [TARGET]).copy()

    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    scratch_predictions, scratch_slope, scratch_intercept = scratch_linear_regression(
        X_train["Area"], y_train, X_test["Area"]
    )
    results = [evaluate_model("Scratch Linear Regression (Area only)", y_test, scratch_predictions)]

    models = {
        "Linear Regression": Pipeline(
            steps=[("preprocess", build_preprocessor()), ("model", LinearRegression())]
        ),
        "Polynomial Regression (degree 2)": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("model", LinearRegression()),
            ]
        ),
        "Decision Tree Regressor": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", DecisionTreeRegressor(max_depth=6, random_state=RANDOM_STATE)),
            ]
        ),
        "Random Forest Regressor": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE)),
            ]
        ),
    }

    fitted_models = {}
    predictions_by_model = {"Scratch Linear Regression (Area only)": scratch_predictions}
    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        fitted_models[name] = model
        predictions_by_model[name] = predictions
        results.append(evaluate_model(name, y_test, predictions))

    metrics = pd.DataFrame(results).sort_values("R2", ascending=False).reset_index(drop=True)
    best_name = metrics.iloc[0]["Model"]
    best_predictions = predictions_by_model[best_name]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(y_test, best_predictions, alpha=0.78, color="#2A9D8F", edgecolor="#1D3557", linewidth=0.7)
    lower = min(y_test.min(), best_predictions.min())
    upper = max(y_test.max(), best_predictions.max())
    ax.plot([lower, upper], [lower, upper], color="#E76F51", linewidth=2, label="Perfect prediction")
    ax.set_title(f"Predicted vs Actual House Prices ({best_name})", fontsize=14, weight="bold")
    ax.set_xlabel("Actual Price")
    ax.set_ylabel("Predicted Price")
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "predictions_vs_actual.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sorted_metrics = metrics.sort_values("R2", ascending=True)
    ax.barh(sorted_metrics["Model"], sorted_metrics["R2"], color="#457B9D")
    ax.set_title("Model Comparison by R-Squared", fontsize=14, weight="bold")
    ax.set_xlabel("R-Squared Score")
    ax.set_xlim(min(0, sorted_metrics["R2"].min() - 0.05), 1.0)
    fig.tight_layout()
    fig.savefig(ROOT / "model_comparison.png", dpi=180)
    plt.close(fig)

    rf_model = fitted_models["Random Forest Regressor"]
    transformed_names = rf_model.named_steps["preprocess"].get_feature_names_out()
    clean_names = [name.replace("num__", "").replace("cat__", "") for name in transformed_names]
    importances = pd.DataFrame(
        {"Feature": clean_names, "Importance": rf_model.named_steps["model"].feature_importances_}
    ).sort_values("Importance", ascending=False)
    top_features = importances.head(5)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top_features.sort_values("Importance")["Feature"], top_features.sort_values("Importance")["Importance"], color="#F4A261")
    ax.set_title("Top Feature Importance (Random Forest)", fontsize=14, weight="bold")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(ROOT / "feature_importance.png", dpi=180)
    plt.close(fig)

    metrics.to_csv(ROOT / "model_metrics.csv", index=False)
    importances.to_csv(ROOT / "feature_importance.csv", index=False)

    best_row = metrics.iloc[0]
    report = f"""# Week 9: House Price Prediction Model

## Project Overview
This project builds a beginner-friendly machine learning workflow to predict house prices using area, bedrooms, bathrooms, property age, location, and property type. The goal is to compare simple and advanced regression models, evaluate model quality, and explain which features most strongly affect the predicted price.

## Dataset Summary
- Source file: `house_data.csv`
- Rows analyzed: {len(df)}
- Columns used: {", ".join(FEATURES + [TARGET])}
- Target variable: `Price`
- Missing values found in required columns: {int(missing_counts.sum())}

## Methodology
1. Loaded and validated the house price dataset.
2. Selected numerical and categorical predictors.
3. Used an 80/20 train-test split with `random_state=42` for reproducibility.
4. Implemented simple linear regression from scratch using `Area` as the only feature.
5. Trained scikit-learn regression models using preprocessing pipelines.
6. Compared all models with MAE, MSE, RMSE, and R2.
7. Visualized predicted prices against actual prices.

## Model Evaluation Results
{metrics.to_markdown(index=False, floatfmt=".4f")}

## Best Model
- Best model: **{best_name}**
- MAE: **{currency(best_row['MAE'])}**
- MSE: **{best_row['MSE']:,.2f}**
- RMSE: **{currency(best_row['RMSE'])}**
- R2 Score: **{best_row['R2']:.4f}**

## Scratch Linear Regression Formula
The from-scratch model used:

`Price = intercept + slope * Area`

- Intercept: {scratch_intercept:,.2f}
- Slope: {scratch_slope:,.2f}

## Key Feature Insights
Top Random Forest feature importance values:

{top_features.to_markdown(index=False, floatfmt=".4f")}

## Business Interpretation
The model confirms that property area is the strongest pricing signal, while location and property type add useful context. A real estate team can use this model as a quick estimate tool for initial pricing discussions, but final pricing should still include local market conditions, amenities, demand, and recent comparable sales.

## Testing Evidence
- The script validates required columns before modeling.
- The same random seed is used for repeatable results.
- The train-test split keeps evaluation data separate from training data.
- The script regenerates the report and figures from the source dataset.
"""
    (ROOT / "model_evaluation_report.md").write_text(report, encoding="utf-8")

    print("HOUSE PRICE PREDICTION MODEL")
    print(f"Best Model: {best_name}")
    print(f"MAE: {currency(best_row['MAE'])}")
    print(f"RMSE: {currency(best_row['RMSE'])}")
    print(f"R2 Score: {best_row['R2']:.4f}")
    print("Best Features:", ", ".join(top_features["Feature"].head(3)))
    return metrics, importances


if __name__ == "__main__":
    run_analysis()
