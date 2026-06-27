from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from scipy import stats
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parent


def money(value):
    return f"INR {value:,.0f}"


def load_data():
    df = pd.read_csv(ROOT / "business_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def run_analysis(df):
    numeric = ["Quantity", "Price", "Marketing_Spend", "Revenue", "Profit", "Tenure", "MonthlyCharges", "TotalCharges", "Churn"]
    descriptive = df[numeric].agg(["count", "mean", "median", "std", "min", "max"]).T
    descriptive["mode"] = df[numeric].mode().iloc[0]
    descriptive = descriptive[["count", "mean", "median", "mode", "std", "min", "max"]]

    tests = []
    comparisons = [
        ("Revenue: high marketing spend vs low marketing spend", df[df["Marketing_Spend"] >= df["Marketing_Spend"].median()]["Revenue"], df[df["Marketing_Spend"] < df["Marketing_Spend"].median()]["Revenue"]),
        ("Revenue: laptop vs non-laptop products", df[df["Product"] == "Laptop"]["Revenue"], df[df["Product"] != "Laptop"]["Revenue"]),
        ("Monthly charges: churned vs retained customers", df[df["Churn"] == 1]["MonthlyCharges"], df[df["Churn"] == 0]["MonthlyCharges"]),
    ]
    for name, a, b in comparisons:
        result = stats.ttest_ind(a, b, equal_var=False)
        tests.append((name, "Welch independent t-test", result.statistic, result.pvalue, result.pvalue < 0.05))
    anova = stats.f_oneway(*(group["Revenue"].values for _, group in df.groupby("Region")))
    tests.append(("Revenue differences across regions", "One-way ANOVA", anova.statistic, anova.pvalue, anova.pvalue < 0.05))

    correlation = df[numeric].corr()
    revenue_ci = stats.t.interval(0.95, len(df) - 1, loc=df["Revenue"].mean(), scale=stats.sem(df["Revenue"]))
    marketing_ci = stats.t.interval(0.95, len(df) - 1, loc=df["Marketing_Spend"].mean(), scale=stats.sem(df["Marketing_Spend"]))
    X = sm.add_constant(df[["Marketing_Spend", "Quantity", "Price", "Tenure", "MonthlyCharges"]])
    model = sm.OLS(df["Revenue"], X).fit()
    return descriptive, tests, correlation, revenue_ci, marketing_ci, model


def create_figures(df, correlation):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df["Revenue"], bins=14, density=True, alpha=0.72, color="#4C78A8")
    x = np.linspace(df["Revenue"].min(), df["Revenue"].max(), 200)
    ax.plot(x, stats.gaussian_kde(df["Revenue"])(x), color="#F58518", linewidth=2)
    ax.set_title("Revenue Distribution")
    fig.tight_layout()
    fig.savefig(ROOT / "revenue_distribution.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    im = ax.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(correlation.columns)), correlation.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(correlation.index)), correlation.index)
    for i in range(len(correlation.index)):
        for j in range(len(correlation.columns)):
            ax.text(j, i, f"{correlation.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title("Pearson Correlation Heatmap")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(ROOT / "correlation_heatmap.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(df["Marketing_Spend"], df["Revenue"], alpha=0.8, color="#54A24B")
    slope, intercept, r_value, _, _ = stats.linregress(df["Marketing_Spend"], df["Revenue"])
    xs = np.array([df["Marketing_Spend"].min(), df["Marketing_Spend"].max()])
    ax.plot(xs, intercept + slope * xs, color="#E45756", label=f"R^2 = {r_value**2:.2f}")
    ax.set_title("Marketing Spend vs Revenue")
    ax.set_xlabel("Marketing Spend")
    ax.set_ylabel("Revenue")
    ax.legend()
    fig.tight_layout()
    fig.savefig(ROOT / "regression_marketing_revenue.png", dpi=160)
    plt.close(fig)


def write_results(descriptive, tests, correlation, revenue_ci, marketing_ci, model):
    lines = ["STATISTICAL ANALYSIS REPORT", "", "Hypothesis Test Results"]
    for name, method, statistic, p_value, significant in tests:
        lines.append(f"- {name}")
        lines.append(f"  Method: {method}")
        lines.append(f"  Test statistic: {statistic:.4f}")
        lines.append(f"  p-value: {p_value:.6f} ({'SIGNIFICANT' if significant else 'NOT SIGNIFICANT'})")
    lines.extend([
        "",
        f"95% CI - Revenue mean: {money(revenue_ci[0])} to {money(revenue_ci[1])}",
        f"95% CI - Marketing spend mean: {money(marketing_ci[0])} to {money(marketing_ci[1])}",
        f"Correlation (Marketing Spend-Revenue): {correlation.loc['Marketing_Spend', 'Revenue']:.4f}",
        f"Regression R-squared: {model.rsquared:.4f}",
    ])
    (ROOT / "hypothesis_tests_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pdf(df, descriptive, tests, correlation, revenue_ci, model):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(ROOT / "statistical_report.pdf"), pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = [
        Paragraph("Statistical Business Analysis Report", styles["Title"]),
        Paragraph("Week 7: Introduction to Statistics for Data Science", styles["Heading2"]),
        Spacer(1, 10),
        Paragraph(f"Average sales: {money(df['Revenue'].mean())} with 95% CI from {money(revenue_ci[0])} to {money(revenue_ci[1])}. Marketing-revenue correlation is {correlation.loc['Marketing_Spend', 'Revenue']:.2f}. Regression R-squared is {model.rsquared:.2f}.", styles["BodyText"]),
        Spacer(1, 10),
    ]
    rows = [["Test", "p-value", "Result"]] + [[name, f"{p:.6f}", "Significant" if sig else "Not significant"] for name, _, _, p, sig in tests]
    table = Table(rows, colWidths=[315, 85, 100])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    story.extend([Paragraph("Hypothesis Test Summary", styles["Heading2"]), table, PageBreak(), Paragraph("Visual Documentation", styles["Heading2"])])
    for title, image in [("Revenue distribution", "revenue_distribution.png"), ("Correlation heatmap", "correlation_heatmap.png"), ("Regression analysis", "regression_marketing_revenue.png")]:
        story.extend([Paragraph(title, styles["Heading3"]), Image(str(ROOT / image), width=440, height=265), Spacer(1, 10)])
    doc.build(story)


def main():
    df = load_data()
    descriptive, tests, correlation, revenue_ci, marketing_ci, model = run_analysis(df)
    create_figures(df, correlation)
    write_results(descriptive, tests, correlation, revenue_ci, marketing_ci, model)
    write_pdf(df, descriptive, tests, correlation, revenue_ci, model)
    print("STATISTICAL ANALYSIS REPORT")
    print(f"Average Sales: {money(df['Revenue'].mean())} ({money(revenue_ci[0])} to {money(revenue_ci[1])} 95% CI)")
    print(f"Correlation (Sales-Marketing): {correlation.loc['Marketing_Spend', 'Revenue']:.2f}")
    print(f"Regression R-squared: {model.rsquared:.2f}")


if __name__ == "__main__":
    main()
