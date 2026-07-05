# Feature Engineering Documentation

## Engineered Features Created
1. `AvgChargePerTenure`: total charges divided by tenure to estimate average customer value over time.
2. `LifetimeValueProxy`: monthly charges multiplied by tenure.
3. `ChargeGap`: difference between recorded total charges and estimated lifetime value.
4. `TenureGroup`: customer tenure bucket: New, Established, or Loyal.
5. `MonthlyToTotalRatio`: monthly charge compared with total charge.
6. `HighMonthlyChargeFlag`: identifies customers in the top monthly charge quartile.
7. `LongTenureFlag`: identifies customers with tenure of at least 36 months.
8. `ContractRiskScore`: assigns higher churn risk to shorter contracts.
9. `PaperlessBillingFlag`: converts paperless billing to a binary feature.
10. `AutoPaymentFlag`: identifies lower-friction payment methods.
11. `MonthlyChargeIntensity`: compares monthly charge against the dataset average.

## Rationale
These features translate raw billing and account details into business signals. They help the model detect customer value, contract commitment, billing behavior, and tenure maturity.

## Outlier Handling
Outliers were detected with both IQR boundaries and Z-score thresholds. Numeric charge/value features were capped with IQR limits instead of removed so customer records remain available for training.

## Feature Selection
Feature selection was performed using logistic regression coefficient strength after preprocessing. The top features are exported to `selected_features.csv` and visualized in `feature_selection.png`.
