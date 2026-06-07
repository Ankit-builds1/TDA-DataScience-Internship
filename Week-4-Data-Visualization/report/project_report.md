# E-commerce Sales Analysis Report

## Project Overview

This project analyzes a sales dataset to understand product performance, regional sales contribution, and sales trends over time. The goal is to practice a complete data analysis workflow: loading data, validating it, cleaning it, calculating metrics, creating charts, and writing business insights.

## Dataset Summary

- Rows before cleaning: 100
- Rows after cleaning: 100
- Date range: 2024-01-01 to 2024-04-09
- Unique customers: 100
- Product categories: 5
- Regions: 4

## Cleaning and Validation

- Missing required values found: 0
- Duplicate rows found: 0
- Rows removed during cleaning: 0
- Total sales mismatches corrected: 0
- Validation rule used for sales totals: `Quantity * Price == Total_Sales`

## Key Metrics

- Total revenue: INR 12,365,048
- Total units sold: 478
- Total orders: 100
- Average order value: INR 123,650
- Best-selling product by revenue: Laptop (INR 3,889,210)
- Highest-revenue region: North (INR 3,983,635)

## Product Sales

| Product | Total_Sales | Units_Sold |
| --- | --- | --- |
| Laptop | INR 3,889,210 | 136 |
| Tablet | INR 2,884,340 | 127 |
| Phone | INR 2,859,394 | 101 |
| Headphones | INR 1,384,033 | 48 |
| Monitor | INR 1,348,071 | 66 |

## Regional Sales

| Region | Total_Sales | Units_Sold |
| --- | --- | --- |
| North | INR 3,983,635 | 147 |
| South | INR 3,737,852 | 143 |
| East | INR 2,519,639 | 94 |
| West | INR 2,123,922 | 94 |

## Monthly Sales Trend

| Month | Total_Sales | Units_Sold |
| --- | --- | --- |
| January 2024 | INR 4,120,524 | 147 |
| February 2024 | INR 2,656,050 | 112 |
| March 2024 | INR 4,485,006 | 175 |
| April 2024 | INR 1,103,468 | 44 |

## Visualizations

### Total Sales by Product

![Total Sales by Product](../visualizations/sales_by_product.png)

### Monthly Sales Trend

![Monthly Sales Trend](../visualizations/sales_trend_over_time.png)

### Sales Share by Region

![Sales Share by Region](../visualizations/sales_share_by_region.png)

## Written Insights

1. Laptop is the strongest product category by revenue, contributing 31.5% of total sales. This product should be prioritized in marketing and inventory planning.
2. North is the highest-revenue region, contributing 32.2% of total sales. This region may have stronger demand or better customer reach.
3. The highest-sales month was March 2024 with INR 4,485,006 in revenue.
4. The business generated INR 12,365,048 across 100 orders, with an average order value of INR 123,650.
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
