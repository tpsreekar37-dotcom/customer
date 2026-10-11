"""
predict.py
----------
Prediction module for the Customer Churn Prediction System.
Loads the saved best model and provides single-customer and batch prediction.
"""

import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import logger, MODELS_DIR


# ──────────────────────────────────────────────────────────────────────────────
# 1. MODEL LOADING
# ──────────────────────────────────────────────────────────────────────────────

_model_cache = {}
_artifact_cache = None

def load_model(model_name: str = "best_model"):
    """Load model from disk with caching."""
    if model_name not in _model_cache:
        path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model file not found: {path}\n"
                "Run main.py or src/train_model.py first."
            )
        _model_cache[model_name] = joblib.load(path)
        logger.info(f"Loaded model: {path}")
    return _model_cache[model_name]


def get_best_model_name() -> str:
    """Read best model name from text file."""
    p = os.path.join(MODELS_DIR, "best_model_name.txt")
    if os.path.exists(p):
        with open(p) as f:
            return f.read().strip()
    return "best_model"


def load_preprocessing_artifacts():
    """Load the transformations and feature constants saved during training."""
    global _artifact_cache
    if _artifact_cache is None:
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
        encoders_path = os.path.join(MODELS_DIR, "encoders.pkl")
        config_path = os.path.join(MODELS_DIR, "feature_config.json")
        missing = [p for p in [scaler_path, encoders_path, config_path] if not os.path.exists(p)]
        if missing:
            raise FileNotFoundError(
                "Preprocessing artifacts are missing. Run 'python main.py' once to train "
                "and create scaler.pkl, encoders.pkl, and feature_config.json."
            )
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
        _artifact_cache = (joblib.load(scaler_path), joblib.load(encoders_path), config)
    return _artifact_cache


# ──────────────────────────────────────────────────────────────────────────────
# 2. PREPROCESSING FOR INFERENCE
# ──────────────────────────────────────────────────────────────────────────────

# Mapping tables mirroring preprocessing.py
BINARY_MAP = {"Yes": 1, "No": 0}

SERVICE_COLS = [
    "MultipleLines", "OnlineSecurity", "OnlineBackup",
    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
]

CONTRACT_MAP = {"Month-to-month": 0, "One year": 1, "Two year": 2}

GENDER_MAP   = {"Male": 1, "Female": 0}
PAYMENT_MAP  = {
    "Bank transfer (automatic)": 0,
    "Credit card (automatic)": 1,
    "Electronic check": 2,
    "Mailed check": 3,
}

INTERNET_MAP = {"DSL": 0, "Fiber optic": 1, "No": 2}


def preprocess_single(customer: dict) -> pd.DataFrame:
    """
    Accept a dict of raw customer data (as collected from dashboard)
    and return a preprocessed DataFrame ready for model inference.
    """
    row = customer.copy()
    scaler, encoders, config = load_preprocessing_artifacts()

    # ── Binary
    for col in ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]:
        if col in row:
            row[col] = BINARY_MAP.get(str(row[col]), 0)

    # ── Service columns
    for col in SERVICE_COLS:
        if col in row:
            val = str(row[col]).lower()
            row[col] = 0 if val in ["no", "no internet service", "no phone service"] else 1

    # ── Contract
    if "Contract" in row:
        row["Contract"] = CONTRACT_MAP.get(str(row["Contract"]), 0)

    # ── Label-encoded categories.  Use the fitted encoders rather than
    # hand-written maps so category codes cannot drift from training.
    for col in ["gender", "InternetService", "PaymentMethod"]:
        if col in row:
            encoder = encoders.get(col)
            value = str(row[col])
            if encoder is not None and hasattr(encoder, "classes_"):
                row[col] = int(encoder.transform([value])[0]) if value in encoder.classes_ else 0
            else:
                fallback = {"gender": GENDER_MAP, "InternetService": INTERNET_MAP,
                            "PaymentMethod": PAYMENT_MAP}[col]
                row[col] = fallback.get(value, 0)

    # ── Numeric coerce
    for col in ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]:
        if col in row:
            row[col] = float(row.get(col, 0))

    df = pd.DataFrame([row])

    # ── Feature engineering (mirroring feature_engineering.py)
    df["TotalCharges"]    = df.get("TotalCharges", df["MonthlyCharges"] * df["tenure"])
    df["ChargesPerTenure"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    # Keep this list identical to feature_engineering.create_features().
    # MultipleLines is deliberately not included in the trained ServiceCount.
    service_count_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies",
    ]
    df["ServiceCount"] = df[[c for c in service_count_cols if c in df.columns]].sum(axis=1)
    df["IsHighValue"]     = (df["MonthlyCharges"] >= config["monthly_charge_threshold"]).astype(int)
    df["HasLoyalty"]      = (df["tenure"] > 24).astype(int)
    contract_risk = (2 - df["Contract"]) / 2
    charges_norm = (df["MonthlyCharges"] - config["monthly_charge_min"]) / (
        config["monthly_charge_max"] - config["monthly_charge_min"] + 1e-9
    )
    tenure_norm = 1 - (df["tenure"] - config["tenure_min"]) / (
        config["tenure_max"] - config["tenure_min"] + 1e-9
    )
    df["RiskScore"] = (0.4 * contract_risk + 0.3 * charges_norm + 0.3 * tenure_norm).round(4)

    # The model was fitted with these three columns standardised.
    scale_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    df[scale_cols] = scaler.transform(df[scale_cols])

    return df


# ──────────────────────────────────────────────────────────────────────────────
# 3. PREDICTION FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def predict_single(customer: dict, model=None) -> dict:
    """
    Predict churn for a single customer.

    Args:
        customer: dict of raw customer features
        model:    optional pre-loaded model (for speed in dashboard)

    Returns:
        dict with keys:
          - churn_prediction (0/1)
          - churn_probability (float 0-1)
          - churn_label       ("Churn" / "No Churn")
          - risk_level        ("High" / "Medium" / "Low")
    """
    if model is None:
        model = load_model("best_model")

    df = preprocess_single(customer)

    # Align with model's expected feature order
    if hasattr(model, "feature_names_in_"):
        expected_cols = list(model.feature_names_in_)
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[expected_cols]

    prob = float(model.predict_proba(df)[0, 1])
    pred = int(model.predict(df)[0])

    if prob >= 0.65:
        risk = "High"
    elif prob >= 0.40:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "churn_prediction":  pred,
        "churn_probability": round(prob, 4),
        "churn_label":       "Churn" if pred == 1 else "No Churn",
        "risk_level":        risk,
    }


def preprocess_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Vectorized preprocessing of an entire DataFrame matching trained model features."""
    scaler, encoders, config = load_preprocessing_artifacts()
    df = df_raw.copy()

    # Binary columns
    for col in ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]:
        if col in df.columns:
            df[col] = df[col].astype(str).map(lambda x: 1 if x.strip().lower() in ["yes", "1", "true"] else 0)
        else:
            df[col] = 0

    # Service columns
    for col in SERVICE_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).map(lambda x: 0 if x.strip().lower() in ["no", "no internet service", "no phone service", "0", "false"] else 1)
        else:
            df[col] = 0

    # Contract
    if "Contract" in df.columns:
        df["Contract"] = df["Contract"].astype(str).map(lambda x: 2 if "two" in x.lower() else (1 if "one" in x.lower() else 0))
    else:
        df["Contract"] = 0

    # Categoricals with encoders
    for col in ["gender", "InternetService", "PaymentMethod"]:
        if col in df.columns:
            encoder = encoders.get(col)
            if encoder is not None and hasattr(encoder, "classes_"):
                known = set(encoder.classes_)
                df[col] = df[col].astype(str).map(lambda x: int(encoder.transform([x])[0]) if x in known else 0)
            else:
                fallback = {"gender": GENDER_MAP, "InternetService": INTERNET_MAP, "PaymentMethod": PAYMENT_MAP}[col]
                df[col] = df[col].astype(str).map(lambda x: fallback.get(x, 0))
        else:
            df[col] = 0

    # Numerics
    for col in ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        else:
            df[col] = 0.0

    # Feature engineering
    total_derived = df["MonthlyCharges"] * df["tenure"]
    df["TotalCharges"] = np.where(df["TotalCharges"] > 0, df["TotalCharges"], total_derived)
    df["ChargesPerTenure"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    service_count_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies",
    ]
    df["ServiceCount"] = df[[c for c in service_count_cols if c in df.columns]].sum(axis=1)
    df["IsHighValue"] = (df["MonthlyCharges"] >= config["monthly_charge_threshold"]).astype(int)
    df["HasLoyalty"] = (df["tenure"] > 24).astype(int)
    contract_risk = (2 - df["Contract"]) / 2
    charges_norm = (df["MonthlyCharges"] - config["monthly_charge_min"]) / (
        config["monthly_charge_max"] - config["monthly_charge_min"] + 1e-9
    )
    tenure_norm = 1 - (df["tenure"] - config["tenure_min"]) / (
        config["tenure_max"] - config["tenure_min"] + 1e-9
    )
    df["RiskScore"] = (0.4 * contract_risk + 0.3 * charges_norm + 0.3 * tenure_norm).round(4)

    scale_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    df[scale_cols] = scaler.transform(df[scale_cols])
    return df


def predict_batch(df_raw: pd.DataFrame, model=None) -> pd.DataFrame:
    """
    Predict churn for a batch of customers from a raw DataFrame.
    Returns standardized columns:
      - 'Churn Probability' (0.0 to 100.0)
      - 'Churn Prediction'  ('Will Churn' / 'Will Stay')
      - 'Risk Level'         ('🔴 High' / '🟡 Medium' / '🟢 Low')
    Plus lowercase backward-compatible columns:
      - 'churn_probability' (0.0 to 1.0)
      - 'churn_prediction'  (0 or 1)
      - 'risk_level'         ('High' / 'Medium' / 'Low')
    """
    if model is None:
        model = load_model("best_model")

    try:
        X = preprocess_dataframe(df_raw)
        if hasattr(model, "feature_names_in_"):
            expected = list(model.feature_names_in_)
            for c in expected:
                if c not in X.columns:
                    X[c] = 0
            X = X[expected]
        probs = model.predict_proba(X)[:, 1]
        preds = model.predict(X)
    except Exception as e:
        logger.warning(f"Vectorized batch prediction fallback: {e}")
        results = [predict_single(r.to_dict(), model) for _, r in df_raw.iterrows()]
        probs = np.array([r["churn_probability"] for r in results])
        preds = np.array([r["churn_prediction"] for r in results])

    def to_risk_emoji(p):
        if p >= 0.65:
            return "🔴 High"
        elif p >= 0.40:
            return "🟡 Medium"
        return "🟢 Low"

    def to_risk_plain(p):
        if p >= 0.65:
            return "High"
        elif p >= 0.40:
            return "Medium"
        return "Low"

    out = df_raw.copy()
    out["Churn Probability"] = (probs * 100).round(1)
    out["Churn Prediction"]  = np.where(preds == 1, "Will Churn", "Will Stay")
    out["Risk Level"]        = [to_risk_emoji(p) for p in probs]

    out["churn_probability"] = probs.round(4)
    out["churn_prediction"]  = preds.astype(int)
    out["risk_level"]        = [to_risk_plain(p) for p in probs]
    return out


if __name__ == "__main__":
    # Example prediction
    sample_customer = {
        "gender":          "Female",
        "SeniorCitizen":   0,
        "Partner":         "Yes",
        "Dependents":      "No",
        "tenure":          5,
        "PhoneService":    "Yes",
        "MultipleLines":   "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity":  "No",
        "OnlineBackup":    "No",
        "DeviceProtection":"No",
        "TechSupport":     "No",
        "StreamingTV":     "Yes",
        "StreamingMovies": "Yes",
        "Contract":        "Month-to-month",
        "PaperlessBilling":"Yes",
        "PaymentMethod":   "Electronic check",
        "MonthlyCharges":  90.45,
        "TotalCharges":    452.25,
    }

    result = predict_single(sample_customer)
    print("\nPrediction Result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
