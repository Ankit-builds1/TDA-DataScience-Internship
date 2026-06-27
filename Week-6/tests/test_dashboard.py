from pathlib import Path

from analysis import load_sales_data, prepare_sales_data, summarize_dashboard
from dashboard import create_interactive_dashboard, create_static_visualizations


ROOT = Path(__file__).resolve().parents[1]


def test_dataset_loads_and_cleans_correctly():
    raw = load_sales_data(ROOT / "sales_data.csv")
    df = prepare_sales_data(raw)
    assert len(df) == 100
    assert df.isna().sum().sum() == 0
    assert df["Total_Mismatch"].sum() == 0
    assert {"Month", "Month_Name", "Order_Value_Segment"}.issubset(df.columns)


def test_dashboard_metrics_match_known_sales_data():
    df = prepare_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    summary = summarize_dashboard(df)
    metrics = summary["metrics"]
    assert metrics.total_revenue == 12365048
    assert metrics.total_orders == 100
    assert metrics.total_units == 478
    assert metrics.top_product == "Laptop"
    assert metrics.top_region == "North"
    assert metrics.best_month == "2024-03"


def test_required_dashboard_summaries_exist():
    df = prepare_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    summary = summarize_dashboard(df)
    assert len(summary["product_summary"]) == 5
    assert len(summary["region_summary"]) == 4
    assert "Total_Sales" in summary["correlation"].columns
    assert summary["duplicate_rows"] == 0


def test_visualizations_and_interactive_dashboard_are_created(tmp_path, monkeypatch):
    import dashboard

    monkeypatch.setattr(dashboard, "ROOT", tmp_path)
    monkeypatch.setattr(dashboard, "VIS", tmp_path / "visualizations")
    monkeypatch.setattr(dashboard, "OUTPUTS", tmp_path / "outputs")
    df = prepare_sales_data(load_sales_data(ROOT / "sales_data.csv"))
    summary = summarize_dashboard(df)
    visuals = create_static_visualizations(df, summary)
    html = create_interactive_dashboard(df, summary)
    assert len(visuals) >= 6
    assert all(path.exists() and path.stat().st_size > 1000 for path in visuals)
    assert html.exists() and "plotly" in html.read_text(encoding="utf-8").lower()
