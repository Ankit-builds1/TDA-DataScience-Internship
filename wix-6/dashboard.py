from __future__ import annotations

from pathlib import Path
import json

import imageio.v2 as imageio
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns

from analysis import format_inr, load_sales_data, prepare_sales_data, summarize_dashboard


ROOT = Path(__file__).resolve().parent
VIS = ROOT / "visualizations"
OUTPUTS = ROOT / "outputs"
REPORTS = ROOT / "reports"


PALETTE = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD"]


def save_fig(fig: plt.Figure, name: str) -> Path:
    VIS.mkdir(exist_ok=True)
    path = VIS / name
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def create_static_visualizations(df: pd.DataFrame, summary: dict[str, object]) -> list[Path]:
    sns.set_theme(style="whitegrid", palette="deep")
    paths: list[Path] = []

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=df, x="Product", y="Price", hue="Product", ax=ax, palette="Blues", legend=False)
    ax.set_title("Price Distribution by Product")
    ax.set_xlabel("Product")
    ax.set_ylabel("Price (INR)")
    ax.tick_params(axis="x", rotation=25)
    paths.append(save_fig(fig, "boxplot_price_by_product.png"))

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.violinplot(data=df, x="Region", y="Total_Sales", hue="Region", ax=ax, palette="Greens", legend=False)
    ax.set_title("Total Sales Distribution by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Total Sales (INR)")
    paths.append(save_fig(fig, "violin_sales_by_region.png"))

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(summary["correlation"], annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("Correlation Heatmap for Sales Metrics")
    paths.append(save_fig(fig, "correlation_heatmap.png"))

    fig, ax = plt.subplots(figsize=(9, 5))
    monthly = summary["monthly_summary"]
    sns.lineplot(data=monthly.reset_index(), x="Month", y="Revenue", marker="o", ax=ax, color="#FF7F0E")
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (INR)")
    paths.append(save_fig(fig, "monthly_revenue_trend.png"))

    fig, ax = plt.subplots(figsize=(9, 5))
    product = summary["product_summary"].reset_index()
    sns.barplot(data=product, x="Product", y="Revenue", hue="Product", ax=ax, palette="Purples", legend=False)
    ax.set_title("Product Revenue Comparison")
    ax.set_xlabel("Product")
    ax.set_ylabel("Revenue (INR)")
    ax.tick_params(axis="x", rotation=25)
    paths.append(save_fig(fig, "product_revenue_bar.png"))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    sns.barplot(data=product, x="Product", y="Revenue", hue="Product", ax=axes[0, 0], palette="Blues", legend=False)
    axes[0, 0].set_title("Revenue by Product")
    axes[0, 0].tick_params(axis="x", rotation=25)
    sns.lineplot(data=monthly.reset_index(), x="Month", y="Revenue", marker="o", ax=axes[0, 1], color="#FF7F0E")
    axes[0, 1].set_title("Monthly Revenue")
    sns.boxplot(data=df, x="Product", y="Price", hue="Product", ax=axes[1, 0], palette="Greens", legend=False)
    axes[1, 0].set_title("Price Distribution")
    axes[1, 0].tick_params(axis="x", rotation=25)
    sns.heatmap(summary["correlation"], annot=True, cmap="coolwarm", fmt=".2f", ax=axes[1, 1])
    axes[1, 1].set_title("Correlation")
    fig.suptitle("Interactive Sales Dashboard - Static 2x2 Overview", fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    paths.append(save_fig(fig, "dashboard_2x2_overview.png"))

    return paths


def create_interactive_dashboard(df: pd.DataFrame, summary: dict[str, object]) -> Path:
    OUTPUTS.mkdir(exist_ok=True)
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Revenue by Product", "Monthly Trend", "Revenue by Region", "Order Segment Mix"),
        specs=[[{"type": "bar"}, {"type": "scatter"}], [{"type": "bar"}, {"type": "pie"}]],
    )
    product = summary["product_summary"].reset_index()
    monthly = summary["monthly_summary"].reset_index()
    region = summary["region_summary"].reset_index()
    segment = summary["segment_summary"].reset_index()
    fig.add_trace(go.Bar(x=product["Product"], y=product["Revenue"], marker_color=PALETTE[0], name="Product Revenue"), row=1, col=1)
    fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Revenue"], mode="lines+markers", marker_color=PALETTE[1], name="Monthly Revenue"), row=1, col=2)
    fig.add_trace(go.Bar(x=region["Region"], y=region["Revenue"], marker_color=PALETTE[2], name="Region Revenue"), row=2, col=1)
    fig.add_trace(go.Pie(labels=segment["Order_Value_Segment"].astype(str), values=segment["Orders"], name="Segments"), row=2, col=2)
    fig.update_layout(
        title="Week 6 Interactive Sales Dashboard",
        height=820,
        template="plotly_white",
        showlegend=True,
    )
    fig.update_yaxes(title_text="Revenue (INR)", row=1, col=1)
    fig.update_yaxes(title_text="Revenue (INR)", row=1, col=2)
    fig.update_yaxes(title_text="Revenue (INR)", row=2, col=1)
    path = OUTPUTS / "interactive_sales_dashboard.html"
    fig.write_html(path, include_plotlyjs="cdn")
    return path


def create_demo_gif(image_paths: list[Path]) -> Path:
    from PIL import Image

    frames = []
    for path in image_paths[:6]:
        image = Image.open(path).convert("RGB")
        image.thumbnail((900, 620))
        canvas = Image.new("RGB", (900, 620), "white")
        canvas.paste(image, ((900 - image.width) // 2, (620 - image.height) // 2))
        frames.append(canvas)
    gif = ROOT / "dashboard_demo.gif"
    imageio.mimsave(gif, frames, duration=1.1)
    return gif


def write_outputs(summary: dict[str, object], interactive_html: Path, visuals: list[Path]) -> None:
    OUTPUTS.mkdir(exist_ok=True)
    summary["product_summary"].to_csv(OUTPUTS / "product_summary.csv")
    summary["region_summary"].to_csv(OUTPUTS / "region_summary.csv")
    summary["monthly_summary"].to_csv(OUTPUTS / "monthly_summary.csv")
    summary["segment_summary"].to_csv(OUTPUTS / "segment_summary.csv")
    summary["correlation"].to_csv(OUTPUTS / "correlation_matrix.csv")
    metrics = summary["metrics"]
    payload = {
        "total_revenue": metrics.total_revenue,
        "total_orders": metrics.total_orders,
        "total_units": metrics.total_units,
        "average_order_value": metrics.average_order_value,
        "top_product": metrics.top_product,
        "top_region": metrics.top_region,
        "best_month": metrics.best_month,
        "missing_values": summary["missing_values"],
        "duplicate_rows": summary["duplicate_rows"],
        "total_mismatches": summary["total_mismatches"],
        "interactive_dashboard": str(interactive_html),
        "visualizations": [str(p) for p in visuals],
    }
    (OUTPUTS / "dashboard_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def create_dashboard_guide(summary: dict[str, object], visuals: list[Path], interactive_html: Path) -> Path:
    REPORTS.mkdir(exist_ok=True)
    metrics = summary["metrics"]
    path = REPORTS / "dashboard_guide.md"
    lines = [
        "# Interactive Sales Dashboard Guide",
        "",
        "## Executive Summary",
        f"- Total revenue: **{format_inr(metrics.total_revenue)}**.",
        f"- Orders: **{metrics.total_orders}**.",
        f"- Units sold: **{metrics.total_units}**.",
        f"- Average order value: **{format_inr(metrics.average_order_value)}**.",
        f"- Top product: **{metrics.top_product}**.",
        f"- Top region: **{metrics.top_region}**.",
        f"- Best month: **{metrics.best_month}**.",
        "",
        "## Visualization Interpretation",
        "- Box plot: compares price distribution across products and highlights spread/outliers.",
        "- Violin plot: shows regional total-sales distribution and density.",
        "- Correlation heatmap: shows relationships among quantity, price, total sales, unit revenue, and day.",
        "- Monthly line chart: shows revenue trend over time.",
        "- Product bar chart: ranks product categories by total revenue.",
        "- 2x2 dashboard: combines the most important static visual views in one professional layout.",
        "- Plotly HTML dashboard: adds hover details and interactive exploration.",
        "",
        "## Generated Files",
        f"- Interactive dashboard: `{interactive_html.as_posix()}`",
    ]
    for visual in visuals:
        lines.append(f"- `{visual.as_posix()}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def create_pdf_report(summary: dict[str, object]) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    path = ROOT / "dashboard_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    metrics = summary["metrics"]
    rows = [
        ["Metric", "Value"],
        ["Total Revenue", format_inr(metrics.total_revenue)],
        ["Orders", str(metrics.total_orders)],
        ["Units Sold", str(metrics.total_units)],
        ["Average Order Value", format_inr(metrics.average_order_value)],
        ["Top Product", metrics.top_product],
        ["Top Region", metrics.top_region],
        ["Best Month", metrics.best_month],
    ]
    table = Table(rows, colWidths=[190, 270])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story = [
        Paragraph("Interactive Sales Dashboard Report", styles["Title"]),
        Paragraph("Week 6: Data Visualization Mastery with Seaborn", styles["Heading2"]),
        Spacer(1, 12),
        table,
        Spacer(1, 12),
        Paragraph("Dashboard Interpretation", styles["Heading2"]),
        Paragraph("The dashboard uses Seaborn statistical charts and Plotly interactive views to communicate product performance, regional sales distribution, correlation patterns, and monthly revenue trends.", styles["BodyText"]),
    ]
    doc.build(story)
    return path


def main() -> None:
    df = prepare_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    summary = summarize_dashboard(df)
    visuals = create_static_visualizations(df, summary)
    interactive_html = create_interactive_dashboard(df, summary)
    gif = create_demo_gif(visuals)
    write_outputs(summary, interactive_html, visuals)
    create_dashboard_guide(summary, visuals, interactive_html)
    create_pdf_report(summary)
    metrics = summary["metrics"]
    print("INTERACTIVE SALES DASHBOARD")
    print(f"Total Revenue: {format_inr(metrics.total_revenue)}")
    print(f"Top Product: {metrics.top_product}")
    print(f"Top Region: {metrics.top_region}")
    print(f"Generated {len(visuals)} static visuals, {interactive_html.name}, and {gif.name}.")


if __name__ == "__main__":
    main()
