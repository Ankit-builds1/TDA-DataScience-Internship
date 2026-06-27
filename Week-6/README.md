# Week 6: Interactive Sales Dashboard

This project builds a professional sales dashboard using **Seaborn** for statistical visualizations and **Plotly** for interactive dashboard views.

## Objective

Analyze the sales dataset to understand revenue trends, product performance, regional distribution, customer/order segmentation, and relationships between numerical sales metrics.

## Dataset

The project uses `sales_data.csv`, which contains 100 sales records with these columns:

- `Date`
- `Product`
- `Quantity`
- `Price`
- `Customer_ID`
- `Region`
- `Total_Sales`

## How to Run

```bash
pip install -r requirements.txt
python dashboard.py
pytest -q
```

After running the script, open:

```text
outputs/interactive_sales_dashboard.html
```

## Main Files

- `analysis.py` - loads, cleans, validates, and summarizes the sales data.
- `dashboard.py` - creates Seaborn charts, Plotly dashboard, output summaries, GIF demo, and PDF report.
- `dashboard.ipynb` - notebook version of the dashboard workflow.
- `visualizations/` - generated Seaborn charts and dashboard overview image.
- `outputs/` - interactive HTML dashboard and summary CSV/JSON files.
- `reports/dashboard_guide.md` - interpretation guide for every visualization.
- `tests/test_dashboard.py` - automated validation tests.

## Visualizations Included

- Box plot for price distribution by product.
- Violin plot for sales distribution by region.
- Correlation heatmap for numerical metrics.
- Monthly revenue trend line chart.
- Product revenue bar chart.
- 2x2 dashboard overview.
- Interactive Plotly dashboard with hover details.

## Key Results

- Total revenue: **INR 12,365,048**
- Total orders: **100**
- Total units sold: **478**
- Average order value: **INR 123,650**
- Top product: **Laptop**
- Top region: **North**
- Best month: **2024-03**
