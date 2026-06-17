# Customer Sales Analysis Report

## Executive Summary
- Total revenue: **INR 12,365,048**.
- Total customers/orders: **100** customers and **100** orders.
- Average order value: **INR 123,650**.
- Top customer: **CUST016** with **INR 373,932**.
- Top product: **Laptop** with **INR 3,889,210**.
- Top region: **North** with **INR 3,983,635**.
- Best month: **2024-03** with **INR 4,485,006**.

## Data Quality
- Sales rows: 100; missing values: 0; duplicate rows: 0.
- Customer churn rows: 500; missing values: 0; duplicate rows: 0.
- Sales/customer churn ID overlap: 0 matched IDs.

## Advanced Filtering Evidence
- `premium_north_or_south` returned 20 rows.
- `phones_or_laptops` returned 52 rows.
- `march_high_value` returned 18 rows.

## Pivot Table Summaries
Product-region and month-product pivot tables are saved under `outputs/`.

## Retention and Cross-Selling Limitation
- Repeat sales customers found: 0.
- Direct customer retention from sales cannot be calculated because every sales customer appears once.
- Cross-selling cannot be calculated because each row contains one product and there is no shared order ID with multiple items.
- Churn analysis is therefore handled separately using the customer churn dataset.
- Overall churn rate in the churn dataset: 10.60%.

## Business Recommendations
- Prioritize Laptop promotions and stock planning because Laptop produces the highest revenue.
- Study the North region more deeply because it has the strongest revenue contribution.
- Treat March performance as the benchmark for campaign planning, while noting April is incomplete.
- For retention, focus on month-to-month contract customers because they show the highest churn rate.
- Collect order-level basket data and harmonized customer IDs in future datasets to enable true merging and cross-selling analysis.

## Visual Evidence
- `C:/Users/ommda/Documents/Codex/2026-06-10/files-mentioned-by-the-user-pasted/outputs/TDA-Week-5-Customer-Sales-Analysis/visualizations/revenue_by_product.png`
- `C:/Users/ommda/Documents/Codex/2026-06-10/files-mentioned-by-the-user-pasted/outputs/TDA-Week-5-Customer-Sales-Analysis/visualizations/monthly_sales_trend.png`
- `C:/Users/ommda/Documents/Codex/2026-06-10/files-mentioned-by-the-user-pasted/outputs/TDA-Week-5-Customer-Sales-Analysis/visualizations/regional_revenue.png`
- `C:/Users/ommda/Documents/Codex/2026-06-10/files-mentioned-by-the-user-pasted/outputs/TDA-Week-5-Customer-Sales-Analysis/visualizations/monthly_product_heatmap.png`
- `C:/Users/ommda/Documents/Codex/2026-06-10/files-mentioned-by-the-user-pasted/outputs/TDA-Week-5-Customer-Sales-Analysis/visualizations/churn_rate_by_contract.png`
