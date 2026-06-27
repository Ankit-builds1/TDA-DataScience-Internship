# TDA Internship Week 6: Interactive Sales Dashboard

This folder contains the Week 6 Data Science internship project for **Data Visualization Mastery with Seaborn**.

## Project Objective

Create a professional interactive sales dashboard using Seaborn and Plotly. The dashboard explains sales trends, customer/order segmentation, product performance, regional distribution, and relationships between numerical metrics.

## Dataset

- `sales_data.csv`
- 100 rows
- 7 columns: `Date`, `Product`, `Quantity`, `Price`, `Customer_ID`, `Region`, `Total_Sales`

## Repository Structure

```text
wix-6/
|-- README.md
|-- dashboard.ipynb
|-- dashboard.py
|-- analysis.py
|-- sales_data.csv
|-- requirements.txt
|-- dashboard_demo.gif
|-- dashboard_report.pdf
|-- visualizations/
|-- outputs/
|-- reports/
|-- docs/
`-- tests/
```

## Setup Instructions

```bash
pip install -r requirements.txt
python dashboard.py
pytest -q
```

Open `outputs/interactive_sales_dashboard.html` in a browser to view the Plotly dashboard.

## Key Results

- Total revenue: **INR 12,365,048**
- Total orders: **100**
- Total units sold: **478**
- Average order value: **INR 123,650**
- Top product: **Laptop**
- Top region: **North**
- Best month: **2024-03**

## Technical Requirements Mapping

- Seaborn statistical plots: box plot, violin plot, heatmap, bar plot, line plot, and 2x2 subplot dashboard.
- At least five chart types: six static visual outputs are generated.
- Plotly interactivity: HTML dashboard with hover information and interactive traces.
- Cohesive color scheme: blue, orange, green, red, and purple dashboard palette.
- Professional layout: generated `dashboard_2x2_overview.png` and `interactive_sales_dashboard.html`.
