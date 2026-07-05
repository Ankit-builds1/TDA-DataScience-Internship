# Week 9: House Price Prediction Model

## Project Overview
This project builds a beginner-friendly machine learning workflow to predict house prices using area, bedrooms, bathrooms, property age, location, and property type. The goal is to compare simple and advanced regression models, evaluate model quality, and explain which features most strongly affect the predicted price.

## Dataset Summary
- Source file: `house_data.csv`
- Rows analyzed: 300
- Columns used: Area, Bedrooms, Bathrooms, Age, Location, Property_Type, Price
- Target variable: `Price`
- Missing values found in required columns: 0

## Methodology
1. Loaded and validated the house price dataset.
2. Selected numerical and categorical predictors.
3. Used an 80/20 train-test split with `random_state=42` for reproducibility.
4. Implemented simple linear regression from scratch using `Area` as the only feature.
5. Trained scikit-learn regression models using preprocessing pipelines.
6. Compared all models with MAE, MSE, RMSE, and R2.
7. Visualized predicted prices against actual prices.

## Model Evaluation Results
| Model                                 |          MAE |                 MSE |         RMSE |     R2 |
|:--------------------------------------|-------------:|--------------------:|-------------:|-------:|
| Polynomial Regression (degree 2)      |  714540.7337 |   803331726308.1992 |  896287.7475 | 0.9944 |
| Random Forest Regressor               | 1474882.0833 |  3902733461869.2124 | 1975533.7157 | 0.9726 |
| Linear Regression                     | 2188736.3437 |  8454330868276.5762 | 2907633.2073 | 0.9406 |
| Decision Tree Regressor               | 2454538.2638 |  9344365521952.2383 | 3056855.4958 | 0.9344 |
| Scratch Linear Regression (Area only) | 6008382.4063 | 57161898244305.0859 | 7560548.8058 | 0.5986 |

## Best Model
- Best model: **Polynomial Regression (degree 2)**
- MAE: **INR 714,541**
- MSE: **803,331,726,308.20**
- RMSE: **INR 896,288**
- R2 Score: **0.9944**

## Scratch Linear Regression Formula
The from-scratch model used:

`Price = intercept + slope * Area`

- Intercept: 3,162,013.16
- Slope: 7,889.31

## Key Feature Insights
Top Random Forest feature importance values:

| Feature              |   Importance |
|:---------------------|-------------:|
| Area                 |       0.6866 |
| Location_City Center |       0.1524 |
| Location_Rural       |       0.0982 |
| Location_Suburb      |       0.0312 |
| Bedrooms             |       0.0196 |

## Business Interpretation
The model confirms that property area is the strongest pricing signal, while location and property type add useful context. A real estate team can use this model as a quick estimate tool for initial pricing discussions, but final pricing should still include local market conditions, amenities, demand, and recent comparable sales.

## Testing Evidence
- The script validates required columns before modeling.
- The same random seed is used for repeatable results.
- The train-test split keeps evaluation data separate from training data.
- The script regenerates the report and figures from the source dataset.
