# Week 10: Data Preprocessing and Feature Engineering

This project builds a complete customer churn preprocessing pipeline. It converts categorical data, scales numerical variables, handles outliers, creates engineered features, selects important features, and trains a churn prediction model.

## Project Goals

- Explore customer churn distribution and data types.
- Implement binary label encoding, ordinal encoding, and one-hot encoding.
- Compare StandardScaler and MinMaxScaler preprocessing.
- Detect outliers using IQR and Z-score methods.
- Create more than five engineered features.
- Build an end-to-end scikit-learn preprocessing pipeline.
- Document every preprocessing decision and rationale.

## Files

- `churn_prediction_pipeline.ipynb` - notebook walkthrough.
- `churn_prediction_pipeline.py` - reproducible script.
- `churn_data.csv` - project dataset.
- `preprocessing_report.md` - preprocessing methodology, results, and validation.
- `feature_engineering_documentation.md` - engineered features and rationale.
- `churn_distribution.png` - churn class distribution chart.
- `feature_selection.png` - selected feature importance chart.
- `confusion_matrix.png` - model testing evidence.
- `requirements.txt` - dependencies.

## Setup Instructions

```bash
pip install -r requirements.txt
python churn_prediction_pipeline.py
```

Running the script regenerates the reports, metrics files, outlier outputs, selected features, and visual documentation.
