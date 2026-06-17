from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd

from analysis import (
    advanced_filters,
    clean_churn_data,
    clean_sales_data,
    compute_sales_summary,
    format_inr,
    load_churn_data,
    load_sales_data,
)


ROOT = Path(__file__).resolve().parent


def save_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def create_visualizations(sales: pd.DataFrame, churn: pd.DataFrame, summary: dict[str, object]) -> list[Path]:
    out = ROOT / "visualizations"
    out.mkdir(exist_ok=True)
    paths: list[Path] = []
    plt.style.use("seaborn-v0_8-whitegrid")

    product = summary["product"]
    fig, ax = plt.subplots(figsize=(9, 5))
    product["Revenue"].plot(kind="bar", ax=ax, color="#2E86AB")
    ax.set_title("Revenue by Product")
    ax.set_ylabel("Revenue (INR)")
    ax.set_xlabel("Product")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    path = out / "revenue_by_product.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    monthly = summary["monthly"]
    fig, ax = plt.subplots(figsize=(9, 5))
    monthly["Monthly_Revenue"].plot(kind="line", marker="o", ax=ax, color="#F18F01", linewidth=2)
    ax.set_title("Monthly Sales Trend")
    ax.set_ylabel("Revenue (INR)")
    ax.set_xlabel("Month")
    fig.tight_layout()
    path = out / "monthly_sales_trend.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    region = summary["region"]
    fig, ax = plt.subplots(figsize=(8, 5))
    region["Revenue"].plot(kind="barh", ax=ax, color="#5DA271")
    ax.set_title("Regional Revenue Performance")
    ax.set_xlabel("Revenue (INR)")
    fig.tight_layout()
    path = out / "regional_revenue.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    pivot = summary["pivot_month_product"]
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(pivot.values, cmap="Blues")
    ax.set_title("Product Revenue Heatmap by Month")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    fig.colorbar(im, ax=ax, label="Revenue (INR)")
    fig.tight_layout()
    path = out / "monthly_product_heatmap.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    churn_contract = summary["churn_by_contract"]
    fig, ax = plt.subplots(figsize=(8, 5))
    (churn_contract["Churn_Rate"] * 100).plot(kind="bar", ax=ax, color="#C73E1D")
    ax.set_title("Churn Rate by Contract Type")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_xlabel("Contract")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    path = out / "churn_rate_by_contract.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    paths.append(path)

    return paths


def create_markdown_report(summary: dict[str, object], filters: dict[str, pd.DataFrame], visual_paths: list[Path]) -> Path:
    report = ROOT / "reports" / "analysis_report.md"
    report.parent.mkdir(exist_ok=True)
    lines = [
        "# Customer Sales Analysis Report",
        "",
        "## Executive Summary",
        f"- Total revenue: **{format_inr(summary['total_revenue'])}**.",
        f"- Total customers/orders: **{summary['total_customers']}** customers and **{summary['total_orders']}** orders.",
        f"- Average order value: **{format_inr(summary['average_order_value'])}**.",
        f"- Top customer: **{summary['top_customer']}** with **{format_inr(summary['top_customer_revenue'])}**.",
        f"- Top product: **{summary['top_product']}** with **{format_inr(summary['top_product_revenue'])}**.",
        f"- Top region: **{summary['top_region']}** with **{format_inr(summary['top_region_revenue'])}**.",
        f"- Best month: **{summary['best_month']}** with **{format_inr(summary['best_month_revenue'])}**.",
        "",
        "## Data Quality",
        f"- Sales rows: {summary['sales_quality'].rows}; missing values: {sum(summary['sales_quality'].missing_values.values())}; duplicate rows: {summary['sales_quality'].duplicate_rows}.",
        f"- Customer churn rows: {summary['churn_quality'].rows}; missing values: {sum(summary['churn_quality'].missing_values.values())}; duplicate rows: {summary['churn_quality'].duplicate_rows}.",
        f"- Sales/customer churn ID overlap: {summary['id_overlap']} matched IDs.",
        "",
        "## Advanced Filtering Evidence",
    ]
    for name, df in filters.items():
        lines.append(f"- `{name}` returned {len(df)} rows.")
    lines += [
        "",
        "## Pivot Table Summaries",
        "Product-region and month-product pivot tables are saved under `outputs/`.",
        "",
        "## Retention and Cross-Selling Limitation",
        f"- Repeat sales customers found: {summary['repeat_customers']}.",
        "- Direct customer retention from sales cannot be calculated because every sales customer appears once.",
        "- Cross-selling cannot be calculated because each row contains one product and there is no shared order ID with multiple items.",
        "- Churn analysis is therefore handled separately using the customer churn dataset.",
        f"- Overall churn rate in the churn dataset: {summary['overall_churn_rate'] * 100:.2f}%.",
        "",
        "## Business Recommendations",
        "- Prioritize Laptop promotions and stock planning because Laptop produces the highest revenue.",
        "- Study the North region more deeply because it has the strongest revenue contribution.",
        "- Treat March performance as the benchmark for campaign planning, while noting April is incomplete.",
        "- For retention, focus on month-to-month contract customers because they show the highest churn rate.",
        "- Collect order-level basket data and harmonized customer IDs in future datasets to enable true merging and cross-selling analysis.",
        "",
        "## Visual Evidence",
    ]
    for path in visual_paths:
        lines.append(f"- `{path.as_posix()}`")
    lines.append("")
    write_text(report, "\n".join(lines))
    return report


def create_pdf_report(markdown_path: Path, summary: dict[str, object]) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    pdf = ROOT / "analysis_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [
        Paragraph("Customer Sales Analysis Report", styles["Title"]),
        Paragraph("Week 5: Advanced Data Manipulation with Pandas", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph("Executive Summary", styles["Heading2"]),
    ]
    data = [
        ["Metric", "Value"],
        ["Total Revenue", format_inr(summary["total_revenue"])],
        ["Total Customers", str(summary["total_customers"])],
        ["Average Order Value", format_inr(summary["average_order_value"])],
        ["Top Customer", f"{summary['top_customer']} - {format_inr(summary['top_customer_revenue'])}"],
        ["Top Product", f"{summary['top_product']} - {format_inr(summary['top_product_revenue'])}"],
        ["Top Region", f"{summary['top_region']} - {format_inr(summary['top_region_revenue'])}"],
        ["Overall Churn Rate", f"{summary['overall_churn_rate'] * 100:.2f}%"],
    ]
    table = Table(data, colWidths=[190, 270])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story += [table, Spacer(1, 12)]
    for heading, body in [
        ("Dataset Limitations", "The sales and churn datasets do not share matching customer IDs, so the merge requirement is demonstrated through a left merge that transparently records zero matched rows. Repeat-purchase retention and basket-level cross-selling are not supported by the supplied sales file because every customer appears once and each row contains one product."),
        ("Recommendations", "Prioritize Laptop stock and promotions, investigate North region performance, use March as the strongest monthly benchmark, and target month-to-month customers for retention campaigns."),
    ]:
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Paragraph(body, styles["BodyText"]))
        story.append(Spacer(1, 8))
    doc.build(story)
    return pdf


def write_outputs(summary: dict[str, object], filters: dict[str, pd.DataFrame]) -> None:
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    summary["monthly"].to_csv(out / "monthly_sales_summary.csv")
    summary["product"].to_csv(out / "product_sales_summary.csv")
    summary["region"].to_csv(out / "regional_sales_summary.csv")
    summary["customer_profile"].to_csv(out / "customer_profile_merge_audit.csv", index=False)
    summary["pivot_product_region"].to_csv(out / "pivot_product_region.csv")
    summary["pivot_month_product"].to_csv(out / "pivot_month_product.csv")
    summary["churn_by_contract"].to_csv(out / "churn_by_contract.csv")
    serializable = {
        k: v for k, v in summary.items()
        if isinstance(v, (str, int, float))
    }
    serializable["sales_quality"] = summary["sales_quality"].__dict__
    serializable["churn_quality"] = summary["churn_quality"].__dict__
    serializable["filters"] = {name: len(df) for name, df in filters.items()}
    (out / "summary_metrics.json").write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def main() -> None:
    sales_raw = load_sales_data(ROOT / "sales_data.csv")
    churn_raw = load_churn_data(ROOT / "customer_data.csv")
    sales = clean_sales_data(sales_raw)
    churn = clean_churn_data(churn_raw)
    filters = advanced_filters(sales)
    summary = compute_sales_summary(sales, churn)
    write_outputs(summary, filters)
    visuals = create_visualizations(sales, churn, summary)
    md = create_markdown_report(summary, filters, visuals)
    create_pdf_report(md, summary)
    print("CUSTOMER SALES ANALYSIS REPORT")
    print(f"Total Revenue: {format_inr(summary['total_revenue'])}")
    print(f"Total Customers: {summary['total_customers']}")
    print(f"Average Order Value: {format_inr(summary['average_order_value'])}")
    print(f"Top Customer: {summary['top_customer']} - {format_inr(summary['top_customer_revenue'])}")
    print("Analysis complete. Reports, outputs, and visualizations generated.")


if __name__ == "__main__":
    main()
