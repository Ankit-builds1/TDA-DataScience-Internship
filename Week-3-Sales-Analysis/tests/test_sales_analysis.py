import unittest

import pandas as pd

from sales_analysis import analyze_sales, clean_sales_data


class SalesAnalysisTests(unittest.TestCase):
    def test_clean_sales_data_fills_missing_values_and_removes_duplicates(self):
        raw_data = pd.DataFrame(
            [
                {
                    "Date": "2024-01-01",
                    "Product": "Phone",
                    "Quantity": 2,
                    "Price": 100,
                    "Customer_ID": "CUST001",
                    "Region": "East",
                    "Total_Sales": None,
                },
                {
                    "Date": "2024-01-01",
                    "Product": "Phone",
                    "Quantity": 2,
                    "Price": 100,
                    "Customer_ID": "CUST001",
                    "Region": "East",
                    "Total_Sales": None,
                },
                {
                    "Date": None,
                    "Product": None,
                    "Quantity": None,
                    "Price": 50,
                    "Customer_ID": None,
                    "Region": None,
                    "Total_Sales": 250,
                },
            ]
        )

        cleaned = clean_sales_data(raw_data)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned.loc[0, "Total_Sales"], 200)
        self.assertEqual(cleaned.loc[1, "Quantity"], 0)
        self.assertEqual(cleaned.loc[1, "Product"], "Unknown")
        self.assertEqual(cleaned.loc[1, "Region"], "Unknown")
        self.assertEqual(cleaned.loc[1, "Customer_ID"], "Unknown")
        self.assertTrue(pd.notna(cleaned.loc[1, "Date"]))

    def test_analyze_sales_returns_required_metrics(self):
        sales_data = pd.DataFrame(
            [
                {
                    "Date": "2024-01-01",
                    "Product": "Phone",
                    "Quantity": 2,
                    "Price": 100,
                    "Customer_ID": "CUST001",
                    "Region": "East",
                    "Total_Sales": 300,
                },
                {
                    "Date": "2024-01-02",
                    "Product": "Laptop",
                    "Quantity": 1,
                    "Price": 500,
                    "Customer_ID": "CUST002",
                    "Region": "West",
                    "Total_Sales": 500,
                },
                {
                    "Date": "2024-01-03",
                    "Product": "Phone",
                    "Quantity": 3,
                    "Price": 100,
                    "Customer_ID": "CUST003",
                    "Region": "East",
                    "Total_Sales": 300,
                },
            ]
        )

        metrics = analyze_sales(sales_data)

        self.assertEqual(metrics["total_revenue"], 1100)
        self.assertAlmostEqual(metrics["average_sale"], 366.6666666666667)
        self.assertEqual(metrics["highest_sale"], 500)
        self.assertEqual(metrics["lowest_sale"], 300)
        self.assertEqual(metrics["best_selling_product_by_quantity"], "Phone")
        self.assertEqual(metrics["top_revenue_product"], "Phone")
        self.assertEqual(metrics["top_region_by_revenue"], "East")


if __name__ == "__main__":
    unittest.main()
