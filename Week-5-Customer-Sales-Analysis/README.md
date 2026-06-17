# TDA Internship Week 5: Customer Sales Analysis

This repository contains the Week 5 Data Science internship project for **Advanced Data Manipulation with Pandas**.

## Project Objective

Analyze customer purchasing patterns, identify top customers, summarize product and regional sales, create pivot-table summaries, and prepare a business-ready sales performance dashboard.

## Important Dataset Note

The supplied files are:

- `sales_data.csv`: 100 sales records with date, product, quantity, price, customer ID, region, and total sales.
- `customer_data.csv`: the supplied `customer_churn.csv` copied under the assignment-required customer-data name.

The two datasets do **not** share matching customer IDs. Sales IDs look like `CUST001`, while churn IDs look like `C00001`. The project therefore demonstrates a merge audit and clearly documents that no customer records matched. Repeat-purchase retention and basket-level cross-selling are also unsupported because each sales customer appears exactly once and each row contains only one product.

## Repository Structure

```text
TDA-Week-5-Customer-Sales-Analysis/
├── README.md
├── customer_analysis.ipynb
├── main.py
├── analysis.py
├── requirements.txt
├── sales_data.csv
├── customer_data.csv
├── analysis_report.pdf
├── reports/
│   └── analysis_report.md
├── visualizations/
│   ├── revenue_by_product.png
│   ├── monthly_sales_trend.png
│   ├── regional_revenue.png
│   ├── monthly_product_heatmap.png
│   └── churn_rate_by_contract.png
├── outputs/
│   ├── monthly_sales_summary.csv
│   ├── product_sales_summary.csv
│   ├── regional_sales_summary.csv
│   ├── customer_profile_merge_audit.csv
│   ├── pivot_product_region.csv
│   ├── pivot_month_product.csv
│   ├── churn_by_contract.csv
│   └── summary_metrics.json
├── docs/
│   └── TDA_INTERNSHIP_WEEK_5_DOCUMENTATION.docx
└── tests/
    └── test_analysis.py
```

## Setup Instructions

1. Install Python 3.10 or above.
2. Clone or download this repository.
3. Open the project folder.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the project:

```bash
python main.py
```

6. Run tests:

```bash
pytest -q
```

## Key Results

- Total revenue: **INR 12,365,048**
- Total customers/orders: **100**
- Average order value: **INR 123,650**
- Top customer: **CUST016 - INR 373,932**
- Top product: **Laptop - INR 3,889,210**
- Top region: **North - INR 3,983,635**
- Best month: **March 2024 - INR 4,485,006**
- Churn rate in supplied churn dataset: **10.60%**

## Technical Requirements Mapping

- Pandas data manipulation: implemented in `analysis.py`.
- Three aggregation types: customer, product, region, monthly, and churn-contract aggregations.
- Merging/joining: implemented in `create_customer_profile()` with merge audit.
- Pivot tables: product-region and month-product pivot tables exported under `outputs/`.
- Professional visualizations: five PNG charts exported under `visualizations/`.

## Testing Evidence

Automated tests validate dataset schemas, missing values, duplicate rows, arithmetic consistency, summary metrics, advanced filters, pivot tables, and merge-audit behavior.
