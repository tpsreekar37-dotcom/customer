"""
generic_pipeline.py
--------------------
A fully schema-agnostic ML pipeline for universal churn prediction.
Works on ANY tabular customer dataset — not just telecom.

Steps:
  1. Auto-detect column types (numeric, categorical, date)
  2. Impute missing values
  3. Encode categoricals (binary → 0/1, multi → label encode)
  4. Scale numeric features
  5. Apply SMOTE if class imbalance exists
  6. Train Random Forest and XGBoost
  7. Use Random Forest as the production model; retain XGBoost as a benchmark
  8. Return predictions + feature importances + metrics

Usage:
  from src.generic_pipeline import run_generic_pipeline, predict_generic
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import joblib


# ──────────────────────────────────────────────────────────────────────────────
# 1. COLUMN TYPE DETECTION
# ──────────────────────────────────────────────────────────────────────────────

def detect_column_types(df: pd.DataFrame, target_col: str, id_col: str = None):
    """
    Auto-detect which columns are numeric, categorical, and date.
    Returns a dict: {col_name: "numeric" | "categorical" | "date" | "drop"}
    """
    col_types = {}
    for col in df.columns:
        if col == target_col:
            col_types[col] = "target"
            continue
        if id_col and col == id_col:
            col_types[col] = "drop"
            continue

        # Prevent target data leakage: drop other churn/outcome columns from X
        col_lower = str(col).strip().lower()
        if ("churn" in col_lower or "attrition" in col_lower or 
            col_lower in ["exited", "customer status", "target", "outcome"]):
            col_types[col] = "drop"
            continue

        dtype = df[col].dtype
        n_unique = df[col].nunique(dropna=True)

        # Date detection
        if dtype == object:
            sample = df[col].dropna().head(50).astype(str)
            date_like = sample.str.match(
                r"^\d{1,4}[-/]\d{1,2}[-/]\d{2,4}$|^\d{4}-\d{2}-\d{2}$"
            ).sum()
            if date_like > len(sample) * 0.7:
                col_types[col] = "date"
                continue

            # Check if object column is actually numeric (e.g. TotalCharges with spaces or formatted numbers)
            clean_str = df[col].astype(str).str.strip().str.replace("$", "", regex=False).str.replace(",", "", regex=False)
            clean_str = clean_str.replace(["", "nan", "none", "null"], np.nan)
            num_converted = pd.to_numeric(clean_str, errors="coerce")
            if num_converted.notna().sum() > len(df[col].dropna()) * 0.75:
                if num_converted.nunique() <= 2:
                    col_types[col] = "binary"
                else:
                    col_types[col] = "numeric"
                continue

        if pd.api.types.is_numeric_dtype(dtype):
            if n_unique <= 2:
                col_types[col] = "binary"
            else:
                col_types[col] = "numeric"
        elif dtype == object or pd.api.types.is_categorical_dtype(dtype):
            if n_unique <= 2:
                col_types[col] = "binary"
            elif n_unique > 50:
                col_types[col] = "drop"   # too high cardinality → drop
            else:
                col_types[col] = "categorical"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_types[col] = "date"
        else:
            col_types[col] = "numeric"

    return col_types


# ──────────────────────────────────────────────────────────────────────────────
# 2. PREPROCESSING
# ──────────────────────────────────────────────────────────────────────────────

def normalize_target(series: pd.Series) -> pd.Series:
    """
    Convert any binary target column to 0/1 integers.
    Handles: Yes/No, True/False, 1/0, Churned/Active, floats with NaNs/infs, string variations.
    The churn/positive class is reliably mapped to 1.
    """
    # Try numeric conversion first
    num_series = pd.to_numeric(series, errors="coerce")
    if num_series.dropna().nunique() == 2:
        max_val = num_series.dropna().max()
        return (num_series == max_val).astype(int)

    # String normalization: strip whitespace and lowercase
    str_series = series.astype(str).str.strip().str.lower()
    valid_mask = ~str_series.isin(["nan", "none", "null", ""])
    unique_vals = str_series[valid_mask].unique()

    positive_hints = {"yes", "true", "churn", "churned", "1", "1.0", "left", "cancelled",
                      "inactive", "attrition", "exited", "lost", "y"}

    if len(unique_vals) == 2:
        pos_val = None
        for v in unique_vals:
            if v in positive_hints:
                pos_val = v
                break
        if pos_val is None:
            pos_val = sorted(unique_vals)[-1]
        return (str_series == pos_val).astype(int)

    # If any positive hint appears in the series
    has_pos = str_series.isin(positive_hints)
    if has_pos.sum() > 0:
        return has_pos.astype(int)

    if len(unique_vals) <= 1:
        return pd.Series(0, index=series.index)

    # Multi-value fallback
    return (str_series == unique_vals[1]).astype(int)


def preprocess_generic(df: pd.DataFrame, target_col: str,
                        id_col: str = None) -> tuple:
    """
    Full preprocessing pipeline for any dataset.

    Returns:
        X_train, X_test, y_train, y_test, scaler, encoders, col_types,
        feature_names, scaler_columns
    """
    df = df.copy()

    # ── Drop rows where target_col is NaN or infinite
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=[target_col])

    # ── Normalize target
    df[target_col] = normalize_target(df[target_col])

    # ── Detect column types
    col_types = detect_column_types(df, target_col, id_col)

    # ── Drop high-cardinality / ID columns
    drop_cols = [c for c, t in col_types.items() if t == "drop"]
    df.drop(columns=drop_cols, inplace=True, errors="ignore")

    # ── Parse date columns → days-since-min feature
    date_cols = [c for c, t in col_types.items() if t == "date"]
    for col in date_cols:
        if col not in df.columns:
            continue
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
            ref = parsed.min()
            df[col + "_days"] = (parsed - ref).dt.days.fillna(0).astype(int)
            df.drop(columns=[col], inplace=True)
            col_types[col + "_days"] = "numeric"
        except Exception:
            df.drop(columns=[col], inplace=True)

    # ── Impute missing values
    for col in df.columns:
        if col == target_col:
            continue
        ctype = col_types.get(col, "numeric")
        if df[col].isna().sum() > 0:
            if ctype in ("numeric",):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 0)

    # ── Encode binary columns (2 unique values)
    encoders = {}
    binary_cols = [c for c, t in col_types.items()
                   if t == "binary" and c in df.columns and c != target_col]
    for col in binary_cols:
        unique_vals = df[col].dropna().unique()
        if set(map(str, unique_vals)) <= {"0", "1", "0.0", "1.0"}:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    # ── Label-encode multi-category columns
    cat_cols = [c for c, t in col_types.items()
                if t == "categorical" and c in df.columns and c != target_col]
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # ── Ensure all remaining object cols are encoded
    remaining_obj = df.select_dtypes(include="object").columns.tolist()
    remaining_obj = [c for c in remaining_obj if c != target_col]
    for col in remaining_obj:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # ── Split X / y
    X = df.drop(columns=[target_col])
    y = pd.to_numeric(df[target_col], errors="coerce").fillna(0).astype(int)
    feature_names = list(X.columns)

    # ── Train / test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # ── Scale numeric columns
    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    scaler = StandardScaler()
    X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test[numeric_cols]  = scaler.transform(X_test[numeric_cols])

    return (X_train, X_test, y_train, y_test, scaler, encoders, col_types,
            feature_names, numeric_cols)


# ──────────────────────────────────────────────────────────────────────────────
# 3. SMOTE
# ──────────────────────────────────────────────────────────────────────────────

def apply_smote_generic(X_train: pd.DataFrame, y_train: pd.Series):
    """Apply SMOTE only if minority class has enough samples."""
    minority_count = y_train.value_counts().min()
    if minority_count < 6:
        # Not enough samples for SMOTE
        return X_train, y_train

    churn_rate = y_train.mean()
    if churn_rate < 0.35 or churn_rate > 0.65:
        # Class imbalance — apply SMOTE
        k = min(5, minority_count - 1)
        smote = SMOTE(random_state=42, k_neighbors=k)
        X_res, y_res = smote.fit_resample(X_train, y_train)
        X_res = pd.DataFrame(X_res, columns=X_train.columns)
        y_res = pd.Series(y_res, name=y_train.name)
        return X_res, y_res

    return X_train, y_train


# ──────────────────────────────────────────────────────────────────────────────
# 4. MODEL TRAINING
# ──────────────────────────────────────────────────────────────────────────────

def get_generic_models() -> dict:
    """Return the production Random Forest and XGBoost benchmark."""
    return {
        "Random Forest": RandomForestClassifier(
            n_estimators=150, max_depth=10, random_state=42,
            n_jobs=-1, class_weight="balanced"
        ),
        "XGBoost": XGBClassifier(
            n_estimators=150, max_depth=6, learning_rate=0.1,
            eval_metric="logloss", random_state=42, n_jobs=-1,
            scale_pos_weight=3,
        ),
    }


def train_generic_models(X_train, X_test, y_train, y_test) -> tuple:
    """
    Train the two approved models. Random Forest is the production model.
    """
    models  = get_generic_models()
    results = []
    trained = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        trained[name] = model

        y_pred  = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "model":     name,
            "accuracy":  round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
            "roc_auc":   round(roc_auc_score(y_test, y_proba), 4),
        }
        results.append(metrics)

    best_name = "Random Forest"
    best_model = trained[best_name]

    return best_model, trained, results, best_name


# ──────────────────────────────────────────────────────────────────────────────
# 5. FEATURE IMPORTANCE
# ──────────────────────────────────────────────────────────────────────────────

def get_feature_importance(model, feature_names: list) -> pd.DataFrame:
    """Extract feature importances from any supported model."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        return pd.DataFrame(columns=["Feature", "Importance"])

    return (
        pd.DataFrame({"Feature": feature_names, "Importance": importances})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )


# ──────────────────────────────────────────────────────────────────────────────
# 6. FULL PIPELINE (called from dashboard)
# ──────────────────────────────────────────────────────────────────────────────

def run_generic_pipeline(df: pd.DataFrame, target_col: str,
                         id_col: str = None) -> dict:
    """
    Full end-to-end pipeline for any uploaded dataset.

    Args:
        df:         Raw uploaded DataFrame
        target_col: Name of the churn/target column (binary)
        id_col:     Name of customer ID column to exclude (optional)

    Returns dict with keys:
        best_model, best_name, results, feature_importance_df,
        X_test, y_test, scaler, encoders, col_types, feature_names,
        churn_rate, n_rows, n_features
    """
    # 1. Preprocess
    X_train, X_test, y_train, y_test, scaler, encoders, col_types, feature_names, scaler_columns = \
        preprocess_generic(df, target_col, id_col)

    n_rows     = len(df)
    n_features = len(feature_names)
    churn_rate = y_train.mean()

    # 2. SMOTE
    X_train_bal, y_train_bal = apply_smote_generic(X_train, y_train)

    # 3. Train models
    best_model, trained, results, best_name = train_generic_models(
        X_train_bal, X_test, y_train_bal, y_test
    )

    # 4. Feature importance
    fi_df = get_feature_importance(best_model, feature_names)

    return {
        "best_model":            best_model,
        "all_models":            trained,
        "best_name":             best_name,
        "results":               results,
        "feature_importance_df": fi_df,
        "X_test":                X_test,
        "y_test":                y_test,
        "scaler":                scaler,
        "encoders":              encoders,
        "col_types":             col_types,
        "feature_names":         feature_names,
        "scaler_columns":        scaler_columns,
        "churn_rate":            churn_rate,
        "n_rows":                n_rows,
        "n_features":            n_features,
        "target_column":          target_col,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 7. BATCH PREDICTION (called from dashboard after training)
# ──────────────────────────────────────────────────────────────────────────────

def predict_generic_batch(df_raw: pd.DataFrame, pipeline_result: dict,
                           target_col: str, id_col: str = None) -> pd.DataFrame:
    """
    Run predictions on the full uploaded dataset.
    Returns df_raw with added columns: churn_probability, churn_prediction, risk_level.
    """
    best_model   = pipeline_result["best_model"]
    scaler       = pipeline_result["scaler"]
    encoders     = pipeline_result["encoders"]
    col_types    = pipeline_result["col_types"]
    feature_names = pipeline_result["feature_names"]
    scaler_columns = pipeline_result["scaler_columns"]

    df = df_raw.copy()
    df = df.replace([np.inf, -np.inf], np.nan)

    # ── Preprocess same way as training (without splitting)
    # Drop target and ID
    drop_cols = [c for c, t in col_types.items() if t == "drop"]
    keep_cols = [c for c in feature_names if c in df.columns]

    # Handle any columns added during date processing
    for col in list(df.columns):
        if col + "_days" in feature_names and col not in feature_names:
            try:
                parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                ref = parsed.min()
                df[col + "_days"] = (parsed - ref).dt.days.fillna(0).astype(int)
            except Exception:
                pass

    # Keep only feature columns
    X = pd.DataFrame(index=df.index)
    for col in feature_names:
        if col in df.columns:
            X[col] = df[col]
        else:
            X[col] = 0

    # Replace any remaining infinite values in X with NaN
    X = X.replace([np.inf, -np.inf], np.nan)

    # Impute missing
    for col in X.columns:
        if pd.api.types.is_numeric_dtype(X[col]) or col in scaler_columns:
            X[col] = pd.to_numeric(X[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
            med = X[col].median()
            X[col] = X[col].fillna(med if pd.notna(med) else 0)
        else:
            if X[col].isna().sum() > 0:
                X[col] = X[col].fillna(0)

    # Encode
    for col, le in encoders.items():
        if col in X.columns:
            known_classes = set(le.classes_)
            X[col] = X[col].apply(lambda v: le.transform([str(v)])[0]
                                   if str(v) in known_classes else 0)

    # Use exact column sequence fitted by StandardScaler
    X[scaler_columns] = scaler.transform(X[scaler_columns])

    # Align feature order
    X = X[feature_names]

    # Predict
    probas = best_model.predict_proba(X)[:, 1]
    preds  = best_model.predict(X)

    def risk_level(p):
        if p >= 0.55:
            return "🔴 High"
        elif p >= 0.35:
            return "🟡 Medium"
        else:
            return "🟢 Low"

    result_df = df_raw.copy()
    result_df["Churn Probability"]  = (probas * 100).round(1)
    result_df["Churn Prediction"]   = np.where(preds == 1, "Will Churn", "Will Stay")
    result_df["Risk Level"]         = [risk_level(p) for p in probas]

    return result_df
