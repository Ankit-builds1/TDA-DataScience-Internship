from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sales_data.csv"
VISUALIZATION_DIR = BASE_DIR / "visualizations"
REPORT_DIR = BASE_DIR / "report"
REPORT_PATH = REPORT_DIR / "project_report.md"

REQUIRED_COLUMNS = [
    "Date",
    "Product",
    "Quantity",
    "Price",
    "Customer_ID",
    "Region",
    "Total_Sales",
]


def format_currency(value):
    """Return a simple INR currency string for reports and chart labels."""
    return f"INR {value:,.0f}"


def load_data(path):
    """Load the sales CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Data file was not found: {path}")

    return pd.read_csv(path)


def validate_data(df):
    """Validate that the dataset has the expected columns and usable rows."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise ValueError(
            "Missing required column(s): " + ", ".join(missing_columns)
        )

    if df.empty:
        raise ValueError("The dataset is empty. Add sales records before analysis.")

    missing_values = df[REQUIRED_COLUMNS].isna().sum().to_dict()
    duplicate_rows = int(df.duplicated().sum())

    return {
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "original_rows": int(len(df)),
    }


def clean_data(df):
    """Clean dates, numeric fields, text fields, and sales totals."""
    cleaned = df.copy()

    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")

    for column in ["Quantity", "Price", "Total_Sales"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    for column in ["Product", "Customer_ID", "Region"]:
        cleaned[column] = cleaned[column].astype("string").str.strip()

    required_after_conversion = [
        "Date",
        "Product",
        "Quantity",
        "Price",
        "Customer_ID",
        "Region",
        "Total_Sales",
    ]
    rows_before_drop = len(cleaned)
    cleaned = cleaned.dropna(subset=required_after_conversion)
    rows_removed = rows_before_drop - len(cleaned)

    cleaned = cleaned[
        (cleaned["Quantity"] > 0)
        & (cleaned["Price"] > 0)
        & (cleaned["Total_Sales"] >= 0)
    ].copy()

    cleaned["Calculated_Total"] = cleaned["Quantity"] * cleaned["Price"]
    mismatch_mask = cleaned["Calculated_Total"].round(2) != cleaned["Total_Sales"].round(2)
    total_sales_mismatches = int(mismatch_mask.sum())

    if total_sales_mismatches:
        cleaned.loc[mismatch_mask, "Total_Sales"] = cleaned.loc[
            mismatch_mask, "Calculated_Total"
        ]

    cleaned["Month"] = cleaned["Date"].dt.to_period("M").dt.to_timestamp()
    cleaned = cleaned.sort_values("Date").reset_index(drop=True)

    cleaning_notes = {
        "rows_removed": int(rows_removed),
        "final_rows": int(len(cleaned)),
        "total_sales_mismatches": total_sales_mismatches,
    }

    return cleaned, cleaning_notes


def analyze_data(df):
    """Calculate project metrics and grouped sales summaries."""
    total_revenue = float(df["Total_Sales"].sum())
    total_units = int(df["Quantity"].sum())
    total_orders = int(len(df))
    average_order_value = float(df["Total_Sales"].mean())
    unique_customers = int(df["Customer_ID"].nunique())
    date_min = df["Date"].min()
    date_max = df["Date"].max()

    product_sales = (
        df.groupby("Product", as_index=False)
        .agg(Total_Sales=("Total_Sales", "sum"), Units_Sold=("Quantity", "sum"))
        .sort_values("Total_Sales", ascending=False)
    )

    region_sales = (
        df.groupby("Region", as_index=False)
        .agg(Total_Sales=("Total_Sales", "sum"), Units_Sold=("Quantity", "sum"))
        .sort_values("Total_Sales", ascending=False)
    )

    monthly_sales = (
        df.groupby("Month", as_index=False)
        .agg(Total_Sales=("Total_Sales", "sum"), Units_Sold=("Quantity", "sum"))
        .sort_values("Month")
    )

    top_product = product_sales.iloc[0]
    top_region = region_sales.iloc[0]
    best_month = monthly_sales.sort_values("Total_Sales", ascending=False).iloc[0]

    return {
        "total_revenue": total_revenue,
        "total_units": total_units,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "unique_customers": unique_customers,
        "date_min": date_min,
        "date_max": date_max,
        "product_sales": product_sales,
        "region_sales": region_sales,
        "monthly_sales": monthly_sales,
        "top_product": top_product,
        "top_region": top_region,
        "best_month": best_month,
    }


def currency_axis():
    """Format chart axes with compact INR values."""
    return FuncFormatter(lambda value, _: f"INR {value / 1_000_000:.1f}M")


def create_visualizations(df, summary):
    """Create and save all required charts."""
    VISUALIZATION_DIR.mkdir(parents=True, exist_ok=True)

    product_sales = summary["product_sales"]
    monthly_sales = summary["monthly_sales"]
    region_sales = summary["region_sales"]

    plt.style.use("seaborn-v0_8-whitegrid")

    product_chart = VISUALIZATION_DIR / "sales_by_product.png"
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        product_sales["Product"],
        product_sales["Total_Sales"],
        color=["#2f6f73", "#d99b39", "#6f5f90", "#b84a4a", "#4d7cb8"],
    )
    ax.set_title("Total Sales by Product", fontsize=16, weight="bold")
    ax.set_xlabel("Product")
    ax.set_ylabel("Total Sales")
    ax.yaxis.set_major_formatter(currency_axis())
    ax.set_ylim(0, product_sales["Total_Sales"].max() * 1.15)
    ax.tick_params(axis="x", rotation=25)
    ax.bar_label(
        bars,
        labels=[format_currency(value) for value in product_sales["Total_Sales"]],
        padding=3,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(product_chart, dpi=160)
    plt.close(fig)

    trend_chart = VISUALIZATION_DIR / "sales_trend_over_time.png"
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        monthly_sales["Month"],
        monthly_sales["Total_Sales"],
        color="#2f6f73",
        marker="o",
        linewidth=2.5,
    )
    ax.set_title("Monthly Sales Trend", fontsize=16, weight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales")
    ax.yaxis.set_major_formatter(currency_axis())
    ax.set_ylim(0, monthly_sales["Total_Sales"].max() * 1.15)
    ax.set_xticks(monthly_sales["Month"])
    ax.set_xticklabels(monthly_sales["Month"].dt.strftime("%b %Y"), rotation=25)
    fig.tight_layout()
    fig.savefig(trend_chart, dpi=160)
    plt.close(fig)

    region_chart = VISUALIZATION_DIR / "sales_share_by_region.png"
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        region_sales["Total_Sales"],
        labels=region_sales["Region"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#2f6f73", "#d99b39", "#6f5f90", "#b84a4a"],
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    ax.set_title("Sales Share by Region", fontsize=16, weight="bold")
    fig.tight_layout()
    fig.savefig(region_chart, dpi=160)
    plt.close(fig)

    return {
        "product_chart": product_chart,
        "trend_chart": trend_chart,
        "region_chart": region_chart,
    }


def table_to_markdown(df, currency_columns=None):
    """Convert a small dataframe into a Markdown table."""
    currency_columns = currency_columns or []
    display = df.copy()

    for column in currency_columns:
        if column in display.columns:
            display[column] = display[column].apply(format_currency)

    headers = [str(column) for column in display.columns]
    rows = display.astype(str).values.tolist()

    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_rows = ["| " + " | ".join(row) + " |" for row in rows]

    return "\n".join([header_row, separator_row, *body_rows])


def create_report(df, summary, validation_notes, cleaning_notes, chart_paths):
    """Create a complete Markdown project report with insights."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    product_sales = summary["product_sales"]
    region_sales = summary["region_sales"]
    monthly_sales = summary["monthly_sales"].copy()
    monthly_sales["Month"] = monthly_sales["Month"].dt.strftime("%B %Y")

    top_product = summary["top_product"]
    top_region = summary["top_region"]
    best_month = summary["best_month"]

    product_share = top_product["Total_Sales"] / summary["total_revenue"] * 100
    region_share = top_region["Total_Sales"] / summary["total_revenue"] * 100

    report = f"""# E-commerce Sales Analysis Report

## Project Overview

This project analyzes a sales dataset to understand product performance, regional sales contribution, and sales trends over time. The goal is to practice a complete data analysis workflow: loading data, validating it, cleaning it, calculating metrics, creating charts, and writing business insights.

## Dataset Summary

- Rows before cleaning: {validation_notes["original_rows"]}
- Rows after cleaning: {cleaning_notes["final_rows"]}
- Date range: {summary["date_min"].date()} to {summary["date_max"].date()}
- Unique customers: {summary["unique_customers"]}
- Product categories: {df["Product"].nunique()}
- Regions: {df["Region"].nunique()}

## Cleaning and Validation

- Missing required values found: {sum(validation_notes["missing_values"].values())}
- Duplicate rows found: {validation_notes["duplicate_rows"]}
- Rows removed during cleaning: {cleaning_notes["rows_removed"]}
- Total sales mismatches corrected: {cleaning_notes["total_sales_mismatches"]}
- Validation rule used for sales totals: `Quantity * Price == Total_Sales`

## Key Metrics

- Total revenue: {format_currency(summary["total_revenue"])}
- Total units sold: {summary["total_units"]:,}
- Total orders: {summary["total_orders"]:,}
- Average order value: {format_currency(summary["average_order_value"])}
- Best-selling product by revenue: {top_product["Product"]} ({format_currency(top_product["Total_Sales"])})
- Highest-revenue region: {top_region["Region"]} ({format_currency(top_region["Total_Sales"])})

## Product Sales

{table_to_markdown(product_sales, currency_columns=["Total_Sales"])}

## Regional Sales

{table_to_markdown(region_sales, currency_columns=["Total_Sales"])}

## Monthly Sales Trend

{table_to_markdown(monthly_sales, currency_columns=["Total_Sales"])}

## Visualizations

### Total Sales by Product

![Total Sales by Product](../visualizations/sales_by_product.png)

### Monthly Sales Trend

![Monthly Sales Trend](../visualizations/sales_trend_over_time.png)

### Sales Share by Region

![Sales Share by Region](../visualizations/sales_share_by_region.png)

## Written Insights

1. {top_product["Product"]} is the strongest product category by revenue, contributing {product_share:.1f}% of total sales. This product should be prioritized in marketing and inventory planning.
2. {top_region["Region"]} is the highest-revenue region, contributing {region_share:.1f}% of total sales. This region may have stronger demand or better customer reach.
3. The highest-sales month was {best_month["Month"].strftime("%B %Y")} with {format_currency(best_month["Total_Sales"])} in revenue.
4. The business generated {format_currency(summary["total_revenue"])} across {summary["total_orders"]} orders, with an average order value of {format_currency(summary["average_order_value"])}.
5. Product revenue is not evenly distributed, so comparing product categories is useful for deciding where to focus promotions, stock, and sales strategy.

## Technical Details

- Language: Python
- Libraries: pandas, matplotlib
- Data structure used for analysis: pandas DataFrame
- Charts are exported as PNG images
- The report is generated automatically as a Markdown file
- The script uses validation checks before analysis so data issues are reported clearly

## Testing Evidence

The script was tested by running:

```bash
python main.py
```

Successful execution confirms:

- The CSV file loads correctly from `data/sales_data.csv`
- Required columns are present
- Date and numeric fields are converted safely
- Missing values, duplicate rows, and total sales mismatches are checked
- The three visualization files are created
- This report is created at `report/project_report.md`
"""

    REPORT_PATH.write_text(report, encoding="utf-8")
    return REPORT_PATH


def main():
    """Run the complete data analysis project."""
    print("Starting E-commerce Sales Analysis...")

    raw_data = load_data(DATA_PATH)
    validation_notes = validate_data(raw_data)
    cleaned_data, cleaning_notes = clean_data(raw_data)

    if cleaned_data.empty:
        raise ValueError("No valid rows remain after cleaning. Please check the dataset.")

    summary = analyze_data(cleaned_data)
    chart_paths = create_visualizations(cleaned_data, summary)
    report_path = create_report(
        cleaned_data,
        summary,
        validation_notes,
        cleaning_notes,
        chart_paths,
    )

    print("Analysis complete.")
    print(f"Rows analyzed: {cleaning_notes['final_rows']}")
    print(f"Total revenue: {format_currency(summary['total_revenue'])}")
    print(f"Top product: {summary['top_product']['Product']}")
    print(f"Top region: {summary['top_region']['Region']}")
    print(f"Report saved to: {report_path}")
    print(f"Charts saved to: {VISUALIZATION_DIR}")


if __name__ == "__main__":
    main()
