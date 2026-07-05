from pathlib import Path
import pickle

import pandas as pd
from flask import Flask, request


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "churn_model.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

app = Flask(__name__)


FORM = """
<h1>Customer Churn Prediction Demo</h1>
<form method="post" action="/predict">
  <label>Tenure: <input name="Tenure" value="12"></label><br>
  <label>Monthly Charges: <input name="MonthlyCharges" value="120"></label><br>
  <label>Total Charges: <input name="TotalCharges" value="2400"></label><br>
  <label>Contract:
    <select name="Contract"><option>Month-to-month</option><option>One year</option><option>Two year</option></select>
  </label><br>
  <label>Payment Method:
    <select name="PaymentMethod"><option>Electronic Check</option><option>Credit Card</option><option>Bank Transfer</option></select>
  </label><br>
  <label>Paperless Billing:
    <select name="PaperlessBilling"><option>Yes</option><option>No</option></select>
  </label><br>
  <label>Senior Citizen: <input name="SeniorCitizen" value="0"></label><br>
  <button type="submit">Predict</button>
</form>
"""


def build_features(form):
    row = {
        "Tenure": float(form["Tenure"]),
        "MonthlyCharges": float(form["MonthlyCharges"]),
        "TotalCharges": float(form["TotalCharges"]),
        "Contract": form["Contract"],
        "PaymentMethod": form["PaymentMethod"],
        "PaperlessBilling": form["PaperlessBilling"],
        "SeniorCitizen": int(form["SeniorCitizen"]),
    }
    tenure_safe = row["Tenure"] or 1
    row["LifetimeValueProxy"] = row["MonthlyCharges"] * row["Tenure"]
    row["AvgChargePerTenure"] = row["TotalCharges"] / tenure_safe
    row["MonthlyToTotalRatio"] = row["MonthlyCharges"] / row["TotalCharges"] if row["TotalCharges"] else 0
    row["ContractRiskScore"] = {"Month-to-month": 3, "One year": 2, "Two year": 1}.get(row["Contract"], 0)
    row["PaperlessBillingFlag"] = 1 if row["PaperlessBilling"] == "Yes" else 0
    row["AutoPaymentFlag"] = 1 if row["PaymentMethod"] in ["Credit Card", "Bank Transfer"] else 0
    row["HighMonthlyChargeFlag"] = 1 if row["MonthlyCharges"] >= 158 else 0
    row["ShortTenureFlag"] = 1 if row["Tenure"] <= 12 else 0
    return pd.DataFrame([row])


@app.route("/")
def index():
    return FORM


@app.route("/predict", methods=["POST"])
def predict():
    features = build_features(request.form)
    probability = model.predict_proba(features)[0, 1]
    label = "High churn risk" if probability >= 0.5 else "Low churn risk"
    return f"<h2>{label}</h2><p>Predicted churn probability: {probability:.2%}</p><a href='/'>Try another</a>"


if __name__ == "__main__":
    app.run(debug=True)
