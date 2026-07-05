# Week 9: House Price Prediction

This project introduces basic machine learning concepts through a house price prediction workflow. It uses the provided house price dataset to train regression models, compare model performance, and explain the most important features behind price predictions.

## Project Goals

- Load and understand the house price dataset.
- Prepare numerical and categorical features for machine learning.
- Implement a simple linear regression model from scratch.
- Train scikit-learn regression models with a proper train-test split.
- Evaluate models using MAE, MSE, RMSE, and R2.
- Visualize predicted prices against actual prices.

## Files

- `house_price_prediction.ipynb` - notebook version of the full workflow.
- `house_price_prediction.py` - reproducible Python script.
- `house_data.csv` - project dataset.
- `model_evaluation_report.md` - model methodology, metrics, and insights.
- `predictions_vs_actual.png` - required prediction visualization.
- `model_comparison.png` - model comparison chart.
- `feature_importance.png` - top pricing drivers.
- `requirements.txt` - Python dependencies.

## Setup Instructions

```bash
pip install -r requirements.txt
python house_price_prediction.py
```

Running the script regenerates the evaluation report, metrics files, and visualization images.

## Key Result

The project compares scratch linear regression, linear regression, polynomial regression, decision tree regression, and random forest regression. The final report identifies the best-performing model using test-set metrics and explains the business meaning of the results.
