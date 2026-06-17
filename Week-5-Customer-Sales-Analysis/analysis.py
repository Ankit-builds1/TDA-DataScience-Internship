from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_SALES_COLUMNS = [
    "Date", "Product", "Quantity", "Price", "Customer_ID", "Region", "Total_Sales"
]
REQUIRED_CHURN_COLUMNS = [
    "CustomerID", "Tenure", "MonthlyCharges", "TotalCharges", "Contract",
    "PaymentMethod", "PaperlessBilling", "SeniorCitizen", "Churn"
]


@dataclass(frozen=True)
class DatasetQuality:
    rows: int
    columns: int
    missing_values: dict[str, int]
    duplicate_rows: int


def load_sales_data(path: str | Path = "sales_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_SALES_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required sales columns: {missing}")
    return df


def load_churn_data(path: str | Path = "customer_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_CHURN_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required churn columns: {missing}")
    return df


def assess_quality(df: pd.DataFrame) -> DatasetQuality:
    return DatasetQuality(
        rows=int(len(df)),
        columns=int(len(df.columns)),
        missing_values={col: int(df[col].isna().sum()) for col in df.columns},
        duplicate_rows=int(df.duplicated().sum()),
    )


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean["Product"] = clean["Product"].astype(str).str.strip().str.title()
    clean["Region"] = clean["Region"].astype(str).str.strip().str.title()
    clean["Customer_ID"] = clean["Customer_ID"].astype(str).str.strip().str.upper()
    clean["Date"] = pd.to_datetime(clean["Date"], errors="coerce")
    for col in ["Quantity", "Price", "Total_Sales"]:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    clean = clean.dropna(subset=REQUIRED_SALES_COLUMNS)
    clean = clean[clean["Quantity"] > 0]
    clean = clean[clean["Price"] > 0]
    clean["Calculated_Total"] = clean["Quantity"] * clean["Price"]
    clean["Total_Mismatch"] = (clean["Calculated_Total"] - clean["Total_Sales"]).abs() > 0.01
    clean["Year"] = clean["Date"].dt.year
    clean["Month"] = clean["Date"].dt.month
    clean["Month_Name"] = clean["Date"].dt.strftime("%B")
    clean["Month_Period"] = clean["Date"].dt.to_period("M").astype(str)
    clean["Day"] = clean["Date"].dt.day
    clean["Order_Value_Band"] = pd.cut(
        clean["Total_Sales"],
        bins=[0, 50000, 150000, 300000, float("inf")],
        labels=["Low", "Medium", "High", "Premium"],
        include_lowest=True,
    )
    return clean


def clean_churn_data(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean["CustomerID"] = clean["CustomerID"].astype(str).str.strip().str.upper()
    for col in ["Tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen", "Churn"]:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    for col in ["Contract", "PaymentMethod", "PaperlessBilling"]:
        clean[col] = clean[col].astype(str).str.strip()
    clean = clean.dropna(subset=REQUIRED_CHURN_COLUMNS)
    clean["Estimated_Lifetime_Value"] = clean["Tenure"] * clean["MonthlyCharges"]
    clean["Churn_Label"] = clean["Churn"].map({0: "Retained", 1: "Churned"})
    clean["Tenure_Group"] = pd.cut(
        clean["Tenure"],
        bins=[0, 12, 36, 72],
        labels=["0-12 Months", "13-36 Months", "37-72 Months"],
        include_lowest=True,
    )
    return clean


def advanced_filters(sales: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "premium_north_or_south": sales[
            (sales["Total_Sales"] >= 150000) & (sales["Region"].isin(["North", "South"]))
        ],
        "phones_or_laptops": sales[
            (sales["Product"].isin(["Phone", "Laptop"])) | (sales["Quantity"] >= 8)
        ],
        "march_high_value": sales[
            (sales["Month_Period"] == "2024-03") & (sales["Total_Sales"] > sales["Total_Sales"].median())
        ],
    }


def create_customer_profile(sales: pd.DataFrame, churn: pd.DataFrame) -> pd.DataFrame:
    sales_profile = sales.groupby("Customer_ID", as_index=False).agg(
        Total_Revenue=("Total_Sales", "sum"),
        Orders=("Customer_ID", "size"),
        Units=("Quantity", "sum"),
        Average_Order_Value=("Total_Sales", "mean"),
        First_Order=("Date", "min"),
        Last_Order=("Date", "max"),
        Main_Region=("Region", lambda s: s.mode().iloc[0]),
        Main_Product=("Product", lambda s: s.mode().iloc[0]),
    )
    churn_profile = churn.rename(columns={"CustomerID": "Customer_ID"})
    merged = sales_profile.merge(churn_profile, on="Customer_ID", how="left", indicator=True)
    return merged


def compute_sales_summary(sales: pd.DataFrame, churn: pd.DataFrame) -> dict[str, object]:
    customer_profile = create_customer_profile(sales, churn)
    monthly = sales.groupby("Month_Period").agg(
        Monthly_Revenue=("Total_Sales", "sum"),
        Monthly_Units=("Quantity", "sum"),
        Monthly_Orders=("Customer_ID", "size"),
        Average_Order_Value=("Total_Sales", "mean"),
    )
    product = sales.groupby("Product").agg(
        Revenue=("Total_Sales", "sum"),
        Units=("Quantity", "sum"),
        Orders=("Product", "size"),
        Average_Price=("Price", "mean"),
    ).sort_values("Revenue", ascending=False)
    region = sales.groupby("Region").agg(
        Revenue=("Total_Sales", "sum"),
        Units=("Quantity", "sum"),
        Orders=("Region", "size"),
        Average_Order_Value=("Total_Sales", "mean"),
    ).sort_values("Revenue", ascending=False)
    pivot_product_region = pd.pivot_table(
        sales, values="Total_Sales", index="Product", columns="Region",
        aggfunc="sum", fill_value=0, margins=True
    )
    pivot_month_product = pd.pivot_table(
        sales, values="Total_Sales", index="Month_Period", columns="Product",
        aggfunc="sum", fill_value=0
    )
    churn_by_contract = churn.groupby("Contract").agg(
        Customers=("CustomerID", "size"),
        Churn_Rate=("Churn", "mean"),
        Avg_Tenure=("Tenure", "mean"),
        Avg_Monthly_Charges=("MonthlyCharges", "mean"),
    ).sort_values("Churn_Rate", ascending=False)
    repeated_customers = int((sales["Customer_ID"].value_counts() > 1).sum())
    id_overlap = len(set(sales["Customer_ID"]) & set(churn["CustomerID"]))
    top_customer_row = customer_profile.sort_values("Total_Revenue", ascending=False).iloc[0]
    return {
        "total_revenue": float(sales["Total_Sales"].sum()),
        "total_units": int(sales["Quantity"].sum()),
        "total_orders": int(len(sales)),
        "total_customers": int(sales["Customer_ID"].nunique()),
        "average_order_value": float(sales["Total_Sales"].mean()),
        "top_customer": str(top_customer_row["Customer_ID"]),
        "top_customer_revenue": float(top_customer_row["Total_Revenue"]),
        "top_product": str(product.index[0]),
        "top_product_revenue": float(product.iloc[0]["Revenue"]),
        "top_region": str(region.index[0]),
        "top_region_revenue": float(region.iloc[0]["Revenue"]),
        "best_month": str(monthly["Monthly_Revenue"].idxmax()),
        "best_month_revenue": float(monthly["Monthly_Revenue"].max()),
        "sales_quality": assess_quality(sales),
        "churn_quality": assess_quality(churn),
        "monthly": monthly,
        "product": product,
        "region": region,
        "customer_profile": customer_profile,
        "pivot_product_region": pivot_product_region,
        "pivot_month_product": pivot_month_product,
        "churn_by_contract": churn_by_contract,
        "overall_churn_rate": float(churn["Churn"].mean()),
        "repeat_customers": repeated_customers,
        "id_overlap": id_overlap,
        "merge_matched_rows": int((customer_profile["_merge"] == "both").sum()),
    }


def format_inr(value: float) -> str:
    return f"INR {value:,.0f}"
