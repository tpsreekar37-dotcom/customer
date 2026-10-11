"""
feature_engineering.py
-----------------------
Advanced feature engineering for the Customer Churn Prediction System.
Creates new features and performs class-imbalance correction using SMOTE.
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import logger


# ──────────────────────────────────────────────────────────────────────────────
# 1. FEATURE ENGINEERING
# ──────────────────────────────────────────────────────────────────────────────

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive new predictive features from existing ones.

    New features:
    - ChargesPerTenure      : Monthly charges / (tenure + 1)
    - ServiceCount          : Total number of add-on services subscribed
    - IsHighValue           : Binary flag for high-revenue customers
    - HasLoyalty            : Binary flag for tenure > 24 months
    - RiskScore             : Composite churn risk score
    """
    df = df.copy()

    # Feature 1: Charges per month of tenure
    if "MonthlyCharges" in df.columns and "tenure" in df.columns:
        df["ChargesPerTenure"] = df["MonthlyCharges"] / (df["tenure"] + 1)

    # Feature 2: Count of add-on services subscribed
    service_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies",
    ]
    present_services = [c for c in service_cols if c in df.columns]
    if present_services:
        df["ServiceCount"] = df[present_services].sum(axis=1)

    # Feature 3: High-value customer flag (top 25% monthly charges)
    if "MonthlyCharges" in df.columns:
        threshold = df["MonthlyCharges"].quantile(0.75)
        df["IsHighValue"] = (df["MonthlyCharges"] >= threshold).astype(int)

    # Feature 4: Loyalty flag (> 2 years tenure)
    if "tenure" in df.columns:
        df["HasLoyalty"] = (df["tenure"] > 24).astype(int)

    # Feature 5: Composite risk score
    if "Contract" in df.columns and "MonthlyCharges" in df.columns:
        contract_risk = (2 - df["Contract"]) / 2
        charges_norm  = (df["MonthlyCharges"] - df["MonthlyCharges"].min()) / (
                         df["MonthlyCharges"].max() - df["MonthlyCharges"].min() + 1e-9)
        tenure_norm   = 1 - (df["tenure"] - df["tenure"].min()) / (
                             df["tenure"].max()  - df["tenure"].min()  + 1e-9)
        df["RiskScore"] = (0.4 * contract_risk + 0.3 * charges_norm + 0.3 * tenure_norm).round(4)

    new_cols = [c for c in ["ChargesPerTenure", "ServiceCount", "IsHighValue",
                             "HasLoyalty", "RiskScore"] if c in df.columns]
    logger.info(f"Feature engineering added: {new_cols}")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# 2. CLASS IMBALANCE HANDLING
# ──────────────────────────────────────────────────────────────────────────────

def apply_smote(X_train: pd.DataFrame, y_train: pd.Series,
                random_state: int = 42):
    """
    Apply SMOTE to oversample the minority class (churned customers).
    Returns: X_resampled, y_resampled as DataFrames.
    """
    churn_rate = y_train.mean()
    logger.info(f"Pre-SMOTE churn rate: {churn_rate:.2%}")

    smote = SMOTE(random_state=random_state, k_neighbors=5)
    X_res, y_res = smote.fit_resample(X_train, y_train)

    X_res = pd.DataFrame(X_res, columns=X_train.columns)
    y_res = pd.Series(y_res, name=y_train.name)

    logger.info(f"Post-SMOTE shape: {X_res.shape} | churn rate: {y_res.mean():.2%}")
    return X_res, y_res


# ──────────────────────────────────────────────────────────────────────────────
# 3. FULL PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

def run_feature_engineering(df: pd.DataFrame, X_train: pd.DataFrame,
                             X_test: pd.DataFrame, y_train: pd.Series,
                             y_test: pd.Series):
    """
    Engineer features and balance training set with SMOTE.
    Returns: X_train_bal, X_test_fe, y_train_bal, y_test
    """
    df_fe = create_features(df)

    new_feat_cols = [
        c for c in ["ChargesPerTenure", "ServiceCount", "IsHighValue",
                     "HasLoyalty", "RiskScore"]
        if c in df_fe.columns
    ]

    X_train_fe = X_train.copy()
    X_test_fe  = X_test.copy()

    for col in new_feat_cols:
        X_train_fe[col] = df_fe.loc[X_train.index, col].values
        X_test_fe[col]  = df_fe.loc[X_test.index,  col].values

    X_train_bal, y_train_bal = apply_smote(X_train_fe, y_train)

    return X_train_bal, X_test_fe, y_train_bal, y_test


if __name__ == "__main__":
    from src.preprocessing import run_preprocessing_pipeline
    X_tr, X_te, y_tr, y_te, scaler, encoders, df = run_preprocessing_pipeline()
    X_tr_b, X_te_fe, y_tr_b, y_te = run_feature_engineering(df, X_tr, X_te, y_tr, y_te)
    print(f"Balanced training set: {X_tr_b.shape}")
    print(f"Features: {list(X_tr_b.columns)}")
