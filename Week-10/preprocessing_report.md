# Week 10: Customer Churn Preprocessing Report

## Project Overview
This project prepares customer churn data for machine learning by applying categorical encoding, feature scaling, outlier handling, feature engineering, feature selection, and an end-to-end preprocessing pipeline.

## Dataset Summary
- Source file: `churn_data.csv`
- Rows: 500
- Columns: 9
- Target: `Churn`
- Churn rate: 10.60%

## Preprocessing Steps
1. Validated required columns and checked data types.
2. Created engineered customer behavior and value features.
3. Detected outliers using IQR and Z-score methods.
4. Capped high-variance numeric features using IQR boundaries.
5. Applied three encoding methods: binary label mapping, ordinal encoding, and one-hot encoding.
6. Compared two scaling methods: StandardScaler and MinMaxScaler.
7. Built complete scikit-learn pipelines for repeatable preprocessing and modeling.

## Encoding Methods Implemented
- Binary label encoding: `PaperlessBilling`, `SeniorCitizen`, `HighMonthlyChargeFlag`, `LongTenureFlag`, `AutoPaymentFlag`
- Ordinal encoding: `Contract`, ordered from month-to-month to two-year
- One-hot encoding: `PaymentMethod`, `TenureGroup`

## Scaling Techniques Implemented
- StandardScaler for the primary logistic regression pipeline
- MinMaxScaler for comparison against the primary pipeline

## Model and Pipeline Results
| Pipeline                             |   Accuracy |   Precision |   Recall |     F1 |   ROC_AUC |
|:-------------------------------------|-----------:|------------:|---------:|-------:|----------:|
| StandardScaler + Logistic Regression |     0.9500 |      0.6875 |   1.0000 | 0.8148 |    0.9949 |
| MinMaxScaler + Logistic Regression   |     0.9300 |      0.6111 |   1.0000 | 0.7586 |    0.9969 |
| StandardScaler + Random Forest       |     0.9900 |      0.9167 |   1.0000 | 0.9565 |    1.0000 |

## Selected Important Features
| Feature                 |   Coefficient |   AbsCoefficient |
|:------------------------|--------------:|-----------------:|
| TenureGroup_New         |        2.4234 |           2.4234 |
| TenureGroup_Established |       -1.9522 |           1.9522 |
| Tenure                  |       -1.1940 |           1.1940 |
| HighMonthlyChargeFlag   |       -1.1373 |           1.1373 |
| LifetimeValueProxy      |       -0.8673 |           0.8673 |
| MonthlyCharges          |        0.6250 |           0.6250 |
| MonthlyChargeIntensity  |        0.6250 |           0.6250 |
| ContractRiskScore       |        0.5789 |           0.5789 |
| ChargeGap               |        0.5107 |           0.5107 |
| LongTenureFlag          |       -0.4717 |           0.4717 |

## Testing Evidence
- Required column validation is performed before feature creation.
- Train-test split uses stratification to preserve churn distribution.
- Pipeline handles missing numeric and categorical values.
- The script regenerates metrics, outlier reports, selected features, and charts from the source CSV.
