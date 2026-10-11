"""
preprocessing.py
----------------
Data loading, cleaning, and preprocessing for the Customer Churn Prediction System.
Handles the IBM Telco Customer Churn dataset (downloaded automatically via URL).
"""

import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import logger, DATA_RAW, DATA_PROCESSED, MODELS_DIR, ensure_dirs

# ──────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────

RAW_CSV_PATH = os.path.join(DATA_RAW, "telco_churn_raw.csv")


def load_data() -> pd.DataFrame:
    """
    Load the Telco Customer Churn dataset.
    If the raw CSV already exists, load from disk.
    Otherwise, download from a public URL and cache it.
    """
    ensure_dirs()

    if os.path.exists(RAW_CSV_PATH):
        logger.info(f"Loading cached dataset from {RAW_CSV_PATH}")
        return pd.read_csv(RAW_CSV_PATH)

    # Try to download from public IBM dataset URL
    import urllib.request

    urls = [
        "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv",
        "https://raw.githubusercontent.com/dsrscientist/dataset1/master/Telecom.csv",
    ]

    df = None
    for url in urls:
        try:
            logger.info(f"Downloading dataset from: {url}")
            urllib.request.urlretrieve(url, RAW_CSV_PATH)
            df = pd.read_csv(RAW_CSV_PATH)
            logger.info(f"Dataset downloaded: {df.shape[0]} rows × {df.shape[1]} cols")
            break
        except Exception as e:
            logger.warning(f"Download failed ({url}): {e}")

    if df is None:
        logger.warning("All downloads failed. Generating synthetic dataset...")
        df = _generate_synthetic_dataset()
        df.to_csv(RAW_CSV_PATH, index=False)

    return df


def _generate_synthetic_dataset(n: int = 7043) -> pd.DataFrame:
    """
    Generate a realistic synthetic Telco churn dataset that mirrors
    the IBM Telco structure. Used as fallback if download fails.
    """
    np.random.seed(42)
    rng = np.random.default_rng(42)

    # Demographics
    genders         = rng.choice(["Male", "Female"], size=n)
    senior_citizen  = rng.choice([0, 1], size=n, p=[0.84, 0.16])
    partners        = rng.choice(["Yes", "No"], size=n)
    dependents      = rng.choice(["Yes", "No"], size=n, p=[0.30, 0.70])

    # Service info
    tenure = rng.integers(0, 72, size=n)
    phone_service = rng.choice(["Yes", "No"], size=n, p=[0.90, 0.10])
    multiple_lines = np.where(
        phone_service == "No", "No phone service",
        rng.choice(["Yes", "No"], size=n)
    )

    internet_service = rng.choice(["DSL", "Fiber optic", "No"], size=n, p=[0.34, 0.44, 0.22])

    def internet_dep(choices, no_label="No internet service"):
        return np.where(internet_service == "No", no_label, rng.choice(choices, size=n))

    online_security    = internet_dep(["Yes", "No"])
    online_backup      = internet_dep(["Yes", "No"])
    device_protection  = internet_dep(["Yes", "No"])
    tech_support       = internet_dep(["Yes", "No"])
    streaming_tv       = internet_dep(["Yes", "No"])
    streaming_movies   = internet_dep(["Yes", "No"])

    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"],
        size=n, p=[0.55, 0.21, 0.24]
    )
    paperless_billing = rng.choice(["Yes", "No"], size=n, p=[0.59, 0.41])
    payment_method = rng.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        size=n, p=[0.34, 0.23, 0.22, 0.21]
    )

    # Monthly charges
    base_charge = np.where(internet_service == "No", 20,
                  np.where(internet_service == "DSL", 50, 75))
    monthly_charges = base_charge + rng.normal(0, 10, size=n)
    monthly_charges = np.clip(monthly_charges, 18, 120).round(2)

    total_charges = (monthly_charges * tenure).round(2)

    # Churn label (logistic-like probability)
    churn_prob = (
        0.05
        + 0.25 * (contract == "Month-to-month").astype(float)
        + 0.15 * (internet_service == "Fiber optic").astype(float)
        + 0.10 * (payment_method == "Electronic check").astype(float)
        - 0.20 * (tenure / 72)
        + 0.05 * senior_citizen
    )
    churn_prob = np.clip(churn_prob, 0.01, 0.99)
    churn = np.where(rng.random(n) < churn_prob, "Yes", "No")

    df = pd.DataFrame({
        "customerID":         [f"CUST-{i:05d}" for i in range(n)],
        "gender":             genders,
        "SeniorCitizen":      senior_citizen,
        "Partner":            partners,
        "Dependents":         dependents,
        "tenure":             tenure,
        "PhoneService":       phone_service,
        "MultipleLines":      multiple_lines,
        "InternetService":    internet_service,
        "OnlineSecurity":     online_security,
        "OnlineBackup":       online_backup,
        "DeviceProtection":   device_protection,
        "TechSupport":        tech_support,
        "StreamingTV":        streaming_tv,
        "StreamingMovies":    streaming_movies,
        "Contract":           contract,
        "PaperlessBilling":   paperless_billing,
        "PaymentMethod":      payment_method,
        "MonthlyCharges":     monthly_charges,
        "TotalCharges":       total_charges.astype(str),  # mimic IBM format
        "Churn":              churn,
    })
    logger.info(f"Synthetic dataset generated: {df.shape}")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# 2. CLEANING
# ──────────────────────────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all data cleaning steps:
    - Drop duplicates
    - Fix TotalCharges dtype
    - Handle missing values
    - Standardise column names
    """
    logger.info("─── Starting data cleaning ───")
    original_shape = df.shape

    # ── 2.1  Drop customer ID (not predictive)
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    # ── 2.2  Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    logger.info(f"Removed {before - len(df)} duplicate rows")

    # ── 2.3  Fix TotalCharges (may contain spaces → NaN)
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        # Impute with tenure × monthly charges for new customers
        mask = df["TotalCharges"].isna()
        df.loc[mask, "TotalCharges"] = df.loc[mask, "MonthlyCharges"] * df.loc[mask, "tenure"]
        logger.info(f"Fixed {mask.sum()} TotalCharges NaN values")

    # ── 2.4  Encode binary target
    if "Churn" in df.columns:
        df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0}).fillna(df["Churn"])

    # ── 2.5  Ensure numeric types
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 2.6  Fill remaining NaN for numeric cols with median
    num_df = df.select_dtypes(include=[np.number])
    for col in num_df.columns:
        if df[col].isna().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)
            logger.info(f"  Imputed {col} with median")

    # ── 2.7  Fill remaining NaN for categorical cols with mode
    cat_df = df.select_dtypes(include=["object"])
    for col in cat_df.columns:
        if df[col].isna().sum() > 0:
            df[col].fillna(df[col].mode()[0], inplace=True)
            logger.info(f"  Imputed {col} with mode")

    logger.info(f"Cleaning done: {original_shape} → {df.shape}")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# 3. OUTLIER HANDLING
# ──────────────────────────────────────────────────────────────────────────────

def handle_outliers(df: pd.DataFrame, cols: list = None) -> pd.DataFrame:
    """
    Cap outliers using IQR method (Winsorisation) on specified numeric columns.
    """
    if cols is None:
        cols = ["MonthlyCharges", "TotalCharges"]

    for col in cols:
        if col not in df.columns:
            continue
        Q1 = df[col].quantile(0.01)
        Q3 = df[col].quantile(0.99)
        before_min, before_max = df[col].min(), df[col].max()
        df[col] = np.clip(df[col], Q1, Q3)
        logger.info(f"Outlier cap [{col}]: [{before_min:.2f},{before_max:.2f}] → [{Q1:.2f},{Q3:.2f}]")

    return df


# ──────────────────────────────────────────────────────────────────────────────
# 4. ENCODING
# ──────────────────────────────────────────────────────────────────────────────

BINARY_MAP = {"Yes": 1, "No": 0}

# Columns that have the value "No internet service" or "No phone service"
# These are effectively "No" → encode as 0
SERVICE_COLS = [
    "MultipleLines", "OnlineSecurity", "OnlineBackup",
    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
]

ORDINAL_COLS_MAP = {
    "Contract": {"Month-to-month": 0, "One year": 1, "Two year": 2},
}


def encode_features(df: pd.DataFrame):
    """
    Encode categorical features:
    - Binary Yes/No columns → 0/1
    - Service columns (with 'No internet/phone service') → 0/1
    - Contract → ordinal
    - Remaining categoricals → label encoded
    Returns: encoded DataFrame, fitted encoders dict
    """
    df = df.copy()
    encoders = {}

    # ── Binary Yes/No
    binary_cols = [
        c for c in ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]
        if c in df.columns
    ]
    for col in binary_cols:
        df[col] = df[col].map(BINARY_MAP).fillna(df[col])

    # ── Service columns
    for col in SERVICE_COLS:
        if col not in df.columns:
            continue
        df[col] = df[col].apply(
            lambda x: 0 if str(x).lower() in ["no", "no internet service", "no phone service"] else 1
        )

    # ── Ordinal
    for col, mapping in ORDINAL_COLS_MAP.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(0).astype(int)
            encoders[col] = mapping

    # ── Label encode remaining categoricals
    remaining_cats = df.select_dtypes(include=["object"]).columns.tolist()
    for col in remaining_cats:
        if col == "Churn":
            continue
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        logger.info(f"Label-encoded '{col}' → {list(le.classes_)}")

    return df, encoders


# ──────────────────────────────────────────────────────────────────────────────
# 5. FEATURE SCALING
# ──────────────────────────────────────────────────────────────────────────────

SCALE_COLS = ["tenure", "MonthlyCharges", "TotalCharges"]


def scale_features(X_train: pd.DataFrame, X_test: pd.DataFrame):
    """
    Standardise continuous features using StandardScaler fitted on training data.
    Returns scaled X_train, X_test, and the fitted scaler.
    """
    scaler = StandardScaler()
    scale_cols = [c for c in SCALE_COLS if c in X_train.columns]

    X_train = X_train.copy()
    X_test  = X_test.copy()

    X_train[scale_cols] = scaler.fit_transform(X_train[scale_cols])
    X_test[scale_cols]  = scaler.transform(X_test[scale_cols])

    logger.info(f"Scaled columns: {scale_cols}")
    return X_train, X_test, scaler


# ──────────────────────────────────────────────────────────────────────────────
# 6. TRAIN/TEST SPLIT
# ──────────────────────────────────────────────────────────────────────────────

def split_data(df: pd.DataFrame, target: str = "Churn", test_size: float = 0.20):
    """
    Split into train/test sets (stratified).
    Returns: X_train, X_test, y_train, y_test
    """
    X = df.drop(columns=[target])
    y = df[target].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    logger.info(f"Train set: {X_train.shape} | Test set: {X_test.shape}")
    logger.info(f"Churn rate – train: {y_train.mean():.2%} | test: {y_test.mean():.2%}")
    return X_train, X_test, y_train, y_test


# ──────────────────────────────────────────────────────────────────────────────
# 7. FULL PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

def run_preprocessing_pipeline():
    """
    End-to-end preprocessing pipeline.
    Returns X_train, X_test, y_train, y_test, scaler, encoders, processed_df
    """
    ensure_dirs()

    df = load_data()
    logger.info(f"Raw data: {df.shape}")

    df = clean_data(df)
    df = handle_outliers(df)
    df, encoders = encode_features(df)

    # Feature-engineering constants are learned from the training population.
    # Saving them prevents dashboard/API inference from using different rules.
    feature_config = {
        "monthly_charge_threshold": float(df["MonthlyCharges"].quantile(0.75)),
        "monthly_charge_min": float(df["MonthlyCharges"].min()),
        "monthly_charge_max": float(df["MonthlyCharges"].max()),
        "tenure_min": float(df["tenure"].min()),
        "tenure_max": float(df["tenure"].max()),
    }
    with open(os.path.join(MODELS_DIR, "feature_config.json"), "w", encoding="utf-8") as f:
        json.dump(feature_config, f, indent=2)

    # Save processed (pre-split) dataset
    processed_path = os.path.join(DATA_PROCESSED, "churn_processed.csv")
    df.to_csv(processed_path, index=False)
    logger.info(f"Processed dataset saved → {processed_path}")

    X_train, X_test, y_train, y_test = split_data(df)
    X_train, X_test, scaler = scale_features(X_train, X_test)

    # Persist the fitted transformations with the model.  Inference must use
    # exactly the same scaling and category encodings as training.
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(encoders, os.path.join(MODELS_DIR, "encoders.pkl"))
    logger.info("Saved preprocessing artifacts to models/")

    # Save train/test splits
    train_df = X_train.copy(); train_df["Churn"] = y_train.values
    test_df  = X_test.copy();  test_df["Churn"]  = y_test.values
    train_df.to_csv(os.path.join(DATA_PROCESSED, "train.csv"), index=False)
    test_df.to_csv(os.path.join(DATA_PROCESSED, "test.csv"),  index=False)
    logger.info("Train/test CSVs saved to data/processed/")

    return X_train, X_test, y_train, y_test, scaler, encoders, df


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, scaler, encoders, df = run_preprocessing_pipeline()
    print(f"\nPreprocessing complete.")
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test  shape: {X_test.shape}")
