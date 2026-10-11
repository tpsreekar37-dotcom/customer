"""
utils.py
--------
Shared utility functions for the Customer Churn Prediction System.
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────────────

def get_logger(name: str = "churn") -> logging.Logger:
    """Return a configured logger instance."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(name)


logger = get_logger()

# ──────────────────────────────────────────────────────────────────────────────
# PATH HELPERS
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def path(*parts: str) -> str:
    """Resolve a path relative to project root."""
    return os.path.join(BASE_DIR, *parts)


DATA_RAW        = path("data", "raw")
DATA_PROCESSED  = path("data", "processed")
MODELS_DIR      = path("models")
REPORTS_DIR     = path("reports", "figures")
SQL_DIR         = path("sql")


def ensure_dirs() -> None:
    """Create output directories if they don't exist."""
    for d in [DATA_RAW, DATA_PROCESSED, MODELS_DIR, REPORTS_DIR, SQL_DIR]:
        os.makedirs(d, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────────
# PLOT HELPERS
# ──────────────────────────────────────────────────────────────────────────────

PALETTE = {
    "primary":   "#C59B27",   # Champagne Gold
    "secondary": "#B8860B",   # Deep Burnished Gold
    "accent":    "#D4AF37",   # Radiant Gold
    "positive":  "#059669",   # Emerald (Retained / Low Risk)
    "negative":  "#DC2626",   # Crimson (Critical / High Risk)
    "neutral":   "#64748B",   # Muted Stone Slate
}

CHURN_COLORS = [PALETTE["positive"], PALETTE["negative"]]

def set_style() -> None:
    """Apply Alabaster Sovereign design system style to matplotlib."""
    plt.rcParams.update({
        "figure.facecolor":  "#FAFAF7",
        "axes.facecolor":    "#FFFFFF",
        "axes.edgecolor":    "#E6D5B8",
        "axes.labelcolor":   "#0F172A",
        "xtick.color":       "#64748B",
        "ytick.color":       "#64748B",
        "text.color":        "#0F172A",
        "grid.color":        "#F0E7D8",
        "grid.alpha":        0.8,
        "font.family":       "sans-serif",
        "axes.titlesize":    14,
        "axes.labelsize":    11,
        "figure.titlesize":  16,
    })


def save_figure(fig: plt.Figure, filename: str) -> str:
    """Save figure to reports/figures/ and return path."""
    out = os.path.join(REPORTS_DIR, filename)
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    logger.info(f"Saved figure → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# METRIC & NUMERICAL HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def safe_float(v, default=0.0) -> float:
    """Safely convert any value to float, handling None, NaN, inf, or formatting."""
    if v is None or pd.isna(v):
        return default
    try:
        res = float(v)
        return default if np.isnan(res) or np.isinf(res) else res
    except Exception:
        return default


def safe_int(v, default=0) -> int:
    """Safely convert any value to int, handling None, NaN, inf, or formatting."""
    if v is None or pd.isna(v):
        return default
    try:
        res = float(v)
        return default if np.isnan(res) or np.isinf(res) else int(res)
    except Exception:
        return default


def find_col(df: pd.DataFrame, candidates: list, default=None):
    """Find the first matching column name in df from a list of candidates."""
    if df is None or not hasattr(df, "columns"):
        return default
    for c in df.columns:
        c_clean = str(c).strip().lower().replace("_", "").replace(" ", "")
        for cand in candidates:
            cand_clean = cand.lower().replace("_", "").replace(" ", "")
            if c_clean == cand_clean or cand_clean in c_clean:
                return c
    return default


def get_revenue_metrics(predicted: pd.DataFrame, sql_results: dict = None) -> dict:
    """Calculate executive MRR, ARR, ARPU, and capital exposure metrics."""
    if sql_results and "revenue_at_risk" in sql_results and not sql_results["revenue_at_risk"].empty:
        r = sql_results["revenue_at_risk"].iloc[0]
        return {
            "mrr": safe_float(r.get("monthly_revenue_at_risk"), 0.0),
            "arr": safe_float(r.get("annual_revenue_at_risk"), 0.0),
            "arpu": safe_float(r.get("arpu"), 0.0),
            "churner_arpu": safe_float(r.get("churner_arpu"), 0.0),
            "high_val": safe_int(r.get("high_value_churn_count"), 0),
            "total": safe_int(r.get("total_customers"), len(predicted) if predicted is not None else 0),
        }
    if predicted is None or predicted.empty:
        return {"mrr": 0.0, "arr": 0.0, "arpu": 0.0, "churner_arpu": 0.0, "high_val": 0, "total": 0}
    monthly_col = find_col(predicted, ["monthlycharges", "monthly_charges", "monthly", "charges"])
    if monthly_col is None:
        predicted = predicted.copy()
        predicted["_mc"] = 70.0
        monthly_col = "_mc"
    else:
        predicted[monthly_col] = pd.to_numeric(predicted[monthly_col], errors="coerce").fillna(0)
    churned = predicted[predicted["Churn Prediction"] == "Will Churn"]
    high_risk = predicted[predicted["Risk Level"].astype(str).str.contains("High", case=False, na=False)]
    mrr = float(churned[monthly_col].sum())
    return {
        "mrr": mrr, "arr": mrr * 12.0,
        "arpu": float(predicted[monthly_col].mean() if len(predicted) > 0 else 0.0),
        "churner_arpu": float(churned[monthly_col].mean() if len(churned) > 0 else 0.0),
        "high_val": len(high_risk),
        "total": len(predicted),
    }


def print_separator(title: str = "") -> None:
    """Print a formatted separator line."""
    width = 70
    if title:
        padding = (width - len(title) - 2) // 2
        print("-" * padding + f" {title} " + "-" * padding)
    else:
        print("-" * width)

