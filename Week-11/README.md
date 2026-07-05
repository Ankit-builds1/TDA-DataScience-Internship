# Week 11: Customer Segmentation & Prediction

This project applies advanced machine learning concepts to customer churn data. It uses clustering to create customer segments, then trains segment-specific Random Forest models with hyperparameter tuning and business recommendations.

## Project Goals

- Apply K-Means, Agglomerative Clustering, and DBSCAN.
- Use the Elbow method and silhouette scores to compare clustering results.
- Create customer segment profiles and business-friendly segment names.
- Build separate prediction models for 3+ segments.
- Tune Random Forest hyperparameters with GridSearchCV.
- Calculate accuracy, precision, recall, F1-score, and ROC-AUC.
- Create segment-specific business recommendations.

## Files

- `customer_segmentation.ipynb` - notebook walkthrough.
- `customer_segmentation.py` - reproducible script.
- `segmentation_data.csv` - project dataset.
- `segment_profiles.md` - customer segment profiles.
- `model_evaluation_results.csv` - segment model metrics.
- `business_recommendations.pdf` - required business recommendation PDF.
- `elbow_method.png`, `customer_segments.png`, `segment_churn_rates.png` - visual evidence.
- `requirements.txt` - dependencies.

## Setup Instructions

```bash
pip install -r requirements.txt
python customer_segmentation.py
```
