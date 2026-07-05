# Week 12: Final Capstone & Career Preparation

This final capstone project demonstrates a complete data science workflow from business problem framing to modeling, reporting, presentation, and a basic deployment demo.

## Business Problem

The project focuses on customer retention. The main deployable model predicts churn risk, while sales and house price datasets are used as supporting portfolio analyses to show broader data science capability.

## Structure

- `capstone_project.ipynb` - main analysis notebook.
- `src/` - reusable source code for the ML workflow.
- `data/` - project datasets.
- `reports/` - technical and business reports plus figures.
- `deployment/` - Flask prediction API and web form.
- `presentation/` - final presentation slides.
- `models/` - saved model artifact.

## Setup

```bash
pip install -r requirements.txt
python src/capstone_pipeline.py
python deployment/app.py
```

Open `http://127.0.0.1:5000` after starting the Flask app to try the churn prediction demo.

## Outputs

- Business report: `reports/business_report.pdf`
- Technical documentation: `reports/technical_documentation.md`
- Presentation: `presentation/final_capstone_presentation.pptx`
- Deployment demo: `deployment/app.py`
