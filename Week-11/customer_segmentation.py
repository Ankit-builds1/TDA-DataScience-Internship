from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, silhouette_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "segmentation_data.csv"
RANDOM_STATE = 42
TARGET = "Churn"


def load_data():
    df = pd.read_csv(DATA_PATH)
    required = ["CustomerID", "Tenure", "MonthlyCharges", "TotalCharges", "Contract", "PaymentMethod", "PaperlessBilling", "SeniorCitizen", "Churn"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def engineer_features(df):
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


def encoded_matrix(df, include_target=False):
    numeric = [
        "Tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen",
        "LifetimeValueProxy", "AvgChargePerTenure", "MonthlyToTotalRatio",
        "ContractRiskScore", "PaperlessBillingFlag", "AutoPaymentFlag",
        "HighMonthlyChargeFlag", "ShortTenureFlag",
    ]
    categorical = ["Contract", "PaymentMethod", "PaperlessBilling"]
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoded = encoder.fit_transform(df[categorical])
    encoded_cols = encoder.get_feature_names_out(categorical)
    X = pd.concat(
        [
            df[numeric].reset_index(drop=True),
            pd.DataFrame(encoded, columns=encoded_cols),
        ],
        axis=1,
    )
    if include_target:
        X[TARGET] = df[TARGET].values
    return X


def assign_segment_names(profile):
    names = {}
    for segment, row in profile.iterrows():
        if row["MonthlyCharges_mean"] >= profile["MonthlyCharges_mean"].median() and row["Tenure_mean"] >= profile["Tenure_mean"].median():
            names[segment] = "Premium Loyalists"
        elif row["ContractRiskScore_mean"] >= profile["ContractRiskScore_mean"].median() and row["Tenure_mean"] < profile["Tenure_mean"].median():
            names[segment] = "At-Risk New Customers"
        elif row["MonthlyCharges_mean"] < profile["MonthlyCharges_mean"].median():
            names[segment] = "Budget Conscious"
        else:
            names[segment] = "Growth Accounts"
    used = {}
    final = {}
    for seg, name in names.items():
        used[name] = used.get(name, 0) + 1
        final[seg] = name if used[name] == 1 else f"{name} {used[name]}"
    return final


def safe_auc(y_true, proba):
    if len(np.unique(y_true)) < 2:
        return np.nan
    return roc_auc_score(y_true, proba)


def train_segment_models(df, features):
    rows = []
    importances = []
    for segment in sorted(df["Segment"].unique()):
        subset = df[df["Segment"] == segment].copy()
        y = subset[TARGET]
        X = features.loc[subset.index]
        if len(subset) < 30 or y.nunique() < 2:
            rows.append({
                "Segment": segment,
                "SegmentName": subset["SegmentName"].iloc[0],
                "Rows": len(subset),
                "Accuracy": np.nan,
                "Precision": np.nan,
                "Recall": np.nan,
                "F1": np.nan,
                "ROC_AUC": np.nan,
                "BestParams": "Not enough class variety for model training",
            })
            continue

        test_size = 0.25 if len(subset) >= 60 else 0.35
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
        )
        param_grid = {
            "n_estimators": [100, 200],
            "max_depth": [3, 5, None],
            "min_samples_leaf": [1, 3],
        }
        cv_splits = max(2, min(3, int(y_train.value_counts().min())))
        model = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE)
        search = GridSearchCV(
            model,
            param_grid,
            scoring="f1",
            cv=StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=RANDOM_STATE),
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        best = search.best_estimator_
        pred = best.predict(X_test)
        proba = best.predict_proba(X_test)[:, 1]
        rows.append({
            "Segment": segment,
            "SegmentName": subset["SegmentName"].iloc[0],
            "Rows": len(subset),
            "Accuracy": accuracy_score(y_test, pred),
            "Precision": precision_score(y_test, pred, zero_division=0),
            "Recall": recall_score(y_test, pred, zero_division=0),
            "F1": f1_score(y_test, pred, zero_division=0),
            "ROC_AUC": safe_auc(y_test, proba),
            "BestParams": str(search.best_params_),
        })
        imp = pd.DataFrame({"Feature": X.columns, "Importance": best.feature_importances_})
        imp["Segment"] = segment
        imp["SegmentName"] = subset["SegmentName"].iloc[0]
        importances.append(imp.sort_values("Importance", ascending=False).head(8))
    return pd.DataFrame(rows), pd.concat(importances, ignore_index=True) if importances else pd.DataFrame()


def create_pdf_recommendations(profile, metrics):
    pdf_path = ROOT / "business_recommendations.pdf"
    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.94, "Week 11 Business Recommendations", fontsize=20, weight="bold")
        fig.text(0.08, 0.90, "Customer Segmentation & Prediction", fontsize=12)
        y = 0.84
        for _, row in profile.iterrows():
            name = row["SegmentName"]
            share = row["CustomerShare"] * 100
            churn = row["Churn_mean"] * 100
            monthly = row["MonthlyCharges_mean"]
            recommendation = (
                "Offer loyalty rewards and premium retention outreach."
                if "Premium" in name else
                "Prioritize onboarding, contract education, and early-life support."
                if "At-Risk" in name else
                "Promote value plans and low-friction payment options."
                if "Budget" in name else
                "Use targeted upsell and account expansion campaigns."
            )
            fig.text(0.08, y, f"{name} ({share:.1f}% of customers)", fontsize=13, weight="bold")
            fig.text(0.10, y - 0.03, f"Churn rate: {churn:.1f}% | Avg monthly charge: {monthly:.0f}", fontsize=10)
            fig.text(0.10, y - 0.06, f"Recommendation: {recommendation}", fontsize=10)
            y -= 0.14
        fig.text(0.08, 0.16, "Modeling Summary", fontsize=13, weight="bold")
        fig.text(0.10, 0.13, f"Segment models trained: {metrics['F1'].notna().sum()} | Best segment F1: {metrics['F1'].max():.3f}", fontsize=10)
        fig.text(0.10, 0.10, "Use these models as decision-support tools. Revalidate with newer customer data before operational rollout.", fontsize=10)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
    return pdf_path


def run_analysis():
    raw = load_data()
    df = engineer_features(raw)
    cluster_features = df[[
        "MonthlyCharges",
        "TotalCharges",
        "SeniorCitizen",
        "ContractRiskScore",
        "PaperlessBillingFlag",
        "AutoPaymentFlag",
        "HighMonthlyChargeFlag",
    ]].copy()
    scaled = StandardScaler().fit_transform(cluster_features)

    inertias = []
    silhouette_rows = []
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        labels = km.fit_predict(scaled)
        inertias.append({"Clusters": k, "Inertia": km.inertia_})
        silhouette_rows.append({"Algorithm": "KMeans", "Clusters": k, "Silhouette": silhouette_score(scaled, labels)})

    kmeans = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=20)
    df["Segment"] = kmeans.fit_predict(scaled)
    agglomerative = AgglomerativeClustering(n_clusters=4)
    agg_labels = agglomerative.fit_predict(scaled)
    dbscan_labels = DBSCAN(eps=2.8, min_samples=8).fit_predict(scaled)

    silhouette_rows.append({"Algorithm": "Agglomerative", "Clusters": len(set(agg_labels)), "Silhouette": silhouette_score(scaled, agg_labels)})
    if len(set(dbscan_labels)) > 1 and -1 not in set(dbscan_labels):
        db_sil = silhouette_score(scaled, dbscan_labels)
    elif len(set(dbscan_labels)) > 2:
        db_sil = silhouette_score(scaled[dbscan_labels != -1], dbscan_labels[dbscan_labels != -1])
    else:
        db_sil = np.nan
    silhouette_rows.append({"Algorithm": "DBSCAN", "Clusters": len(set(dbscan_labels)), "Silhouette": db_sil})

    profile = df.groupby("Segment").agg(
        Customers=("CustomerID", "count"),
        Tenure_mean=("Tenure", "mean"),
        MonthlyCharges_mean=("MonthlyCharges", "mean"),
        TotalCharges_mean=("TotalCharges", "mean"),
        Churn_mean=("Churn", "mean"),
        ContractRiskScore_mean=("ContractRiskScore", "mean"),
        SeniorCitizen_mean=("SeniorCitizen", "mean"),
    )
    profile["CustomerShare"] = profile["Customers"] / len(df)
    names = assign_segment_names(profile)
    profile["SegmentName"] = [names[idx] for idx in profile.index]
    df["SegmentName"] = df["Segment"].map(names)
    profile = profile.reset_index()[["Segment", "SegmentName", "Customers", "CustomerShare", "Tenure_mean", "MonthlyCharges_mean", "TotalCharges_mean", "Churn_mean", "ContractRiskScore_mean", "SeniorCitizen_mean"]]

    model_features = encoded_matrix(df).drop(columns=[TARGET], errors="ignore")
    model_metrics, feature_importance = train_segment_models(df, model_features)

    pd.DataFrame(inertias).to_csv(ROOT / "elbow_results.csv", index=False)
    pd.DataFrame(silhouette_rows).to_csv(ROOT / "clustering_comparison.csv", index=False)
    profile.to_csv(ROOT / "segment_profiles.csv", index=False)
    model_metrics.to_csv(ROOT / "model_evaluation_results.csv", index=False)
    feature_importance.to_csv(ROOT / "segment_feature_importance.csv", index=False)
    df.to_csv(ROOT / "segmentation_with_predictions_ready_features.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(7, 5))
    elbow = pd.DataFrame(inertias)
    ax.plot(elbow["Clusters"], elbow["Inertia"], marker="o", color="#2A9D8F")
    ax.set_title("Elbow Method for K-Means", fontsize=14, weight="bold")
    ax.set_xlabel("Number of Clusters")
    ax.set_ylabel("Inertia")
    fig.tight_layout()
    fig.savefig(ROOT / "elbow_method.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(df["Tenure"], df["MonthlyCharges"], c=df["Segment"], cmap="viridis", alpha=0.78)
    ax.set_title("Customer Segments by Tenure and Monthly Charges", fontsize=14, weight="bold")
    ax.set_xlabel("Tenure")
    ax.set_ylabel("Monthly Charges")
    fig.colorbar(scatter, ax=ax, label="Segment")
    fig.tight_layout()
    fig.savefig(ROOT / "customer_segments.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    plot_profile = profile.sort_values("Churn_mean")
    ax.barh(plot_profile["SegmentName"], plot_profile["Churn_mean"], color="#E76F51")
    ax.set_title("Churn Rate by Customer Segment", fontsize=14, weight="bold")
    ax.set_xlabel("Churn Rate")
    fig.tight_layout()
    fig.savefig(ROOT / "segment_churn_rates.png", dpi=180)
    plt.close(fig)

    create_pdf_recommendations(profile, model_metrics)

    segment_lines = []
    for _, row in profile.iterrows():
        segment_lines.append(
            f"## {row['SegmentName']}\n"
            f"- Segment ID: {int(row['Segment'])}\n"
            f"- Customers: {int(row['Customers'])} ({row['CustomerShare']:.1%})\n"
            f"- Average tenure: {row['Tenure_mean']:.1f} months\n"
            f"- Average monthly charges: {row['MonthlyCharges_mean']:.2f}\n"
            f"- Churn rate: {row['Churn_mean']:.1%}\n"
            f"- Business action: {'Retention outreach and loyalty rewards' if 'Premium' in row['SegmentName'] else 'Early onboarding and contract support' if 'At-Risk' in row['SegmentName'] else 'Value-plan messaging and payment convenience' if 'Budget' in row['SegmentName'] else 'Upsell and engagement campaigns'}\n"
        )
    (ROOT / "segment_profiles.md").write_text(
        "# Segment Profiles\n\n" +
        "K-Means with 4 clusters was selected after reviewing elbow and silhouette results. Agglomerative clustering and DBSCAN were used as comparison algorithms.\n\n" +
        "\n".join(segment_lines),
        encoding="utf-8",
    )

    print("CUSTOMER SEGMENTATION & PREDICTION")
    print(f"Rows: {len(df)}")
    print(f"Segments created: {df['Segment'].nunique()}")
    print(f"Clustering algorithms compared: KMeans, Agglomerative, DBSCAN")
    print(f"Segment models trained: {model_metrics['F1'].notna().sum()}")
    print(f"Best segment F1: {model_metrics['F1'].max():.4f}")
    print("Segment names:", ", ".join(profile["SegmentName"].tolist()))
    return profile, model_metrics


if __name__ == "__main__":
    run_analysis()
