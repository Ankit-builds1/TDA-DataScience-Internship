# Week 12 Final Capstone: Comprehensive Data Science Project

## Executive Summary
This project completes an end-to-end data science workflow across sales, housing, and customer churn datasets. The deployable model focuses on churn prediction because customer retention has direct business impact.

## Business Problem
The company needs a repeatable way to identify customers likely to leave, understand revenue patterns, and present model-backed recommendations in a portfolio-ready format.

## Success Metrics
- Primary metric: churn prediction F1 score
- Supporting metrics: recall, ROC-AUC, house price R2, and sales growth patterns

## Results
- Churn rate: 10.60%
- Churn model accuracy: 0.9900
- Churn model recall: 1.0000
- Churn model F1 score: 0.9565
- Churn model ROC-AUC: 1.0000
- Total sales analyzed: 12,365,048
- Top product: Laptop
- Top region: North
- House price model R2: 0.9706

## Recommendations
1. Use the churn model to flag high-risk customers for retention outreach.
2. Prioritize high-value customers with short tenure and high monthly charges.
3. Use sales trend monitoring to align campaign timing with revenue peaks.
4. Keep the model retraining process repeatable through the included source modules and deployment files.

## Deployment Demo
The `deployment/app.py` file provides a Flask prediction API and simple web form. The saved model is stored in `models/churn_model.pkl`.
