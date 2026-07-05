# Technical Documentation

## Methodology
The project loads three datasets, validates structure, performs exploratory analysis, engineers churn features, trains machine learning models, saves a deployable model, and creates reports/presentation materials.

## Model Architecture
- Main model: Random Forest classifier for churn prediction
- Tuning: GridSearchCV over tree count, max depth, and minimum leaf size
- Supporting model: Random Forest regressor for house price prediction

## Results
- Churn F1: 0.9565
- Churn recall: 1.0000
- Churn ROC-AUC: 1.0000
- House model R2: 0.9706

## Deployment
The Flask app in `deployment/app.py` loads `models/churn_model.pkl`, accepts customer inputs, creates engineered features, and returns churn probability.

## Testing Evidence
- Required datasets are loaded from `data/`.
- The pipeline regenerates all reports and charts from source data.
- The saved model is used by the deployment demo.
- Metrics are exported to `reports/capstone_metrics.json`.
