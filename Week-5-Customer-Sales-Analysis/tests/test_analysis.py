from pathlib import Path

import pandas as pd

from analysis import (
    advanced_filters,
    clean_churn_data,
    clean_sales_data,
    compute_sales_summary,
    create_customer_profile,
    load_churn_data,
    load_sales_data,
)


ROOT = Path(__file__).resolve().parents[1]


def test_sales_dataset_schema_and_quality():
    raw = load_sales_data(ROOT / "sales_data.csv")
    sales = clean_sales_data(raw)
    assert len(sales) == 100
    assert sales["Customer_ID"].nunique() == 100
    assert sales.duplicated().sum() == 0
    assert sales.isna().sum().sum() == 0
    assert int(sales["Total_Mismatch"].sum()) == 0


def test_churn_dataset_schema_and_quality():
    raw = load_churn_data(ROOT / "customer_data.csv")
    churn = clean_churn_data(raw)
    assert len(churn) == 500
    assert churn["CustomerID"].nunique() == 500
    assert churn.duplicated().sum() == 0
    assert churn.isna().sum().sum() == 0


def test_summary_metrics_match_verified_values():
    sales = clean_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    churn = clean_churn_data(load_churn_data(ROOT / "customer_data.csv"))
    summary = compute_sales_summary(sales, churn)
    assert summary["total_revenue"] == 12365048
    assert summary["total_units"] == 478
    assert summary["top_product"] == "Laptop"
    assert summary["top_region"] == "North"
    assert summary["best_month"] == "2024-03"
    assert round(summary["overall_churn_rate"], 3) == 0.106


def test_advanced_filters_and_pivot_tables_are_populated():
    sales = clean_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    churn = clean_churn_data(load_churn_data(ROOT / "customer_data.csv"))
    filters = advanced_filters(sales)
    summary = compute_sales_summary(sales, churn)
    assert set(filters) == {"premium_north_or_south", "phones_or_laptops", "march_high_value"}
    assert all(len(df) > 0 for df in filters.values())
    assert "All" in summary["pivot_product_region"].index
    assert "Laptop" in summary["pivot_month_product"].columns


def test_merge_audit_documents_no_matching_ids():
    sales = clean_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    churn = clean_churn_data(load_churn_data(ROOT / "customer_data.csv"))
    merged = create_customer_profile(sales, churn)
    assert len(merged) == 100
    assert (merged["_merge"] == "both").sum() == 0
