from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["Date", "Product", "Quantity", "Price", "Customer_ID", "Region", "Total_Sales"]


@dataclass(frozen=True)
class DashboardMetrics:
    total_revenue: float
    total_orders: int
    total_units: int
    average_order_value: float
    top_product: str
    top_region: str
    best_month: str


def load_sales_data(path: str | Path = "sales_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def prepare_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared["Product"] = prepared["Product"].astype(str).str.strip().str.title()
    prepared["Region"] = prepared["Region"].astype(str).str.strip().str.title()
    prepared["Customer_ID"] = prepared["Customer_ID"].astype(str).str.strip().str.upper()
    prepared["Date"] = pd.to_datetime(prepared["Date"], errors="coerce")
    for col in ["Quantity", "Price", "Total_Sales"]:
        prepared[col] = pd.to_numeric(prepared[col], errors="coerce")
    prepared = prepared.dropna(subset=REQUIRED_COLUMNS)
    prepared = prepared[(prepared["Quantity"] > 0) & (prepared["Price"] > 0)]
    prepared["Calculated_Total"] = prepared["Quantity"] * prepared["Price"]
    prepared["Total_Mismatch"] = (prepared["Calculated_Total"] - prepared["Total_Sales"]).abs() > 0.01
    prepared["Month"] = prepared["Date"].dt.to_period("M").astype(str)
    prepared["Month_Name"] = prepared["Date"].dt.strftime("%B")
    prepared["Day"] = prepared["Date"].dt.day
    prepared["Revenue_Per_Unit"] = prepared["Total_Sales"] / prepared["Quantity"]
    prepared["Order_Value_Segment"] = pd.cut(
        prepared["Total_Sales"],
        bins=[0, 50000, 150000, 300000, float("inf")],
        labels=["Low", "Medium", "High", "Premium"],
        include_lowest=True,
    )
    return prepared


def summarize_dashboard(df: pd.DataFrame) -> dict[str, object]:
    product_summary = df.groupby("Product").agg(
        Revenue=("Total_Sales", "sum"),
        Orders=("Product", "size"),
        Units=("Quantity", "sum"),
        Average_Order_Value=("Total_Sales", "mean"),
        Average_Price=("Price", "mean"),
    ).sort_values("Revenue", ascending=False)
    region_summary = df.groupby("Region").agg(
        Revenue=("Total_Sales", "sum"),
        Orders=("Region", "size"),
        Units=("Quantity", "sum"),
        Average_Order_Value=("Total_Sales", "mean"),
    ).sort_values("Revenue", ascending=False)
    monthly_summary = df.groupby("Month").agg(
        Revenue=("Total_Sales", "sum"),
        Orders=("Month", "size"),
        Units=("Quantity", "sum"),
        Average_Order_Value=("Total_Sales", "mean"),
    )
    segment_summary = df.groupby("Order_Value_Segment", observed=True).agg(
        Orders=("Customer_ID", "size"),
        Revenue=("Total_Sales", "sum"),
        Average_Order_Value=("Total_Sales", "mean"),
    )
    correlation = df[["Quantity", "Price", "Total_Sales", "Revenue_Per_Unit", "Day"]].corr()
    metrics = DashboardMetrics(
        total_revenue=float(df["Total_Sales"].sum()),
        total_orders=int(len(df)),
        total_units=int(df["Quantity"].sum()),
        average_order_value=float(df["Total_Sales"].mean()),
        top_product=str(product_summary.index[0]),
        top_region=str(region_summary.index[0]),
        best_month=str(monthly_summary["Revenue"].idxmax()),
    )
    return {
        "metrics": metrics,
        "product_summary": product_summary,
        "region_summary": region_summary,
        "monthly_summary": monthly_summary,
        "segment_summary": segment_summary,
        "correlation": correlation,
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
        "duplicate_rows": int(df.duplicated().sum()),
        "total_mismatches": int(df["Total_Mismatch"].sum()),
    }


def format_inr(value: float) -> str:
    return f"INR {value:,.0f}"
