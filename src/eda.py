"""
eda.py
------
Comprehensive Exploratory Data Analysis (EDA) for the
Customer Churn Prediction System.

Generates and saves 10+ professional visualisations to reports/figures/.
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import (logger, REPORTS_DIR, set_style,
                        save_figure, PALETTE, CHURN_COLORS, ensure_dirs)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _dark_fig(w=12, h=6):
    """Create a pre-styled dark-background figure."""
    set_style()
    return plt.subplots(figsize=(w, h))


# ──────────────────────────────────────────────────────────────────────────────
# 1. CHURN DISTRIBUTION
# ──────────────────────────────────────────────────────────────────────────────

def plot_churn_distribution(df: pd.DataFrame) -> str:
    set_style()
    churn_col = "Churn"
    if churn_col not in df.columns:
        return ""

    counts = df[churn_col].value_counts()
    labels = ["No Churn", "Churn"] if 0 in counts.index else list(counts.index)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Customer Churn Distribution", fontsize=16, fontweight="bold", y=1.02)

    # Pie
    wedge_props = dict(width=0.55, edgecolor="#0F172A", linewidth=2)
    axes[0].pie(
        counts.values, labels=labels, autopct="%1.1f%%",
        colors=CHURN_COLORS, startangle=90,
        wedgeprops=wedge_props, textprops={"color": "#E2E8F0", "fontsize": 12}
    )
    axes[0].set_title("Churn Ratio", fontsize=13)

    # Bar
    bars = axes[1].bar(labels, counts.values, color=CHURN_COLORS,
                       edgecolor="#0F172A", linewidth=1.5, width=0.5)
    for bar, val in zip(bars, counts.values):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 30, f"{val:,}",
                     ha="center", va="bottom", fontsize=12, color="#E2E8F0")
    axes[1].set_title("Churn Count", fontsize=13)
    axes[1].set_ylabel("Number of Customers")
    axes[1].set_ylim(0, counts.max() * 1.15)
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "01_churn_distribution.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 2. TENURE ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def plot_tenure_analysis(df: pd.DataFrame) -> str:
    if "tenure" not in df.columns or "Churn" not in df.columns:
        return ""
    set_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Customer Tenure Analysis", fontsize=16, fontweight="bold")

    # Histogram by churn
    for churn_val, color, label in [(0, CHURN_COLORS[0], "No Churn"),
                                     (1, CHURN_COLORS[1], "Churn")]:
        subset = df[df["Churn"] == churn_val]["tenure"]
        axes[0].hist(subset, bins=30, alpha=0.7, color=color, label=label, edgecolor="#0F172A")
    axes[0].set_xlabel("Tenure (months)")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Tenure Distribution by Churn")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Box plot
    data_no_churn = df[df["Churn"] == 0]["tenure"]
    data_churn    = df[df["Churn"] == 1]["tenure"]
    bp = axes[1].boxplot(
        [data_no_churn, data_churn],
        tick_labels=["No Churn", "Churn"],
        patch_artist=True, medianprops=dict(color="white", lw=2),
        boxprops=dict(linewidth=1.5)
    )
    for patch, color in zip(bp["boxes"], CHURN_COLORS):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
    axes[1].set_ylabel("Tenure (months)")
    axes[1].set_title("Tenure Spread – Churners vs Retainers")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "02_tenure_analysis.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 3. CONTRACT TYPE ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def plot_contract_analysis(df_raw: pd.DataFrame) -> str:
    """Expects the raw (pre-encoded) dataframe or a version with Contract as string."""
    col = "Contract"
    if col not in df_raw.columns or "Churn" not in df_raw.columns:
        return ""

    set_style()
    # Group churn rate by contract
    grouped = df_raw.groupby(col)["Churn"].agg(["mean", "count"]).reset_index()
    grouped.columns = [col, "ChurnRate", "Count"]
    grouped["ChurnRate"] = grouped["ChurnRate"] * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Contract Type & Churn", fontsize=16, fontweight="bold")

    colors = [PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"]]

    # Churn rate bar
    bars = axes[0].bar(grouped[col].astype(str), grouped["ChurnRate"],
                       color=colors[:len(grouped)], edgecolor="#0F172A", width=0.55)
    for bar, val in zip(bars, grouped["ChurnRate"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.5, f"{val:.1f}%",
                     ha="center", fontsize=11, color="#E2E8F0")
    axes[0].set_ylabel("Churn Rate (%)")
    axes[0].set_title("Churn Rate by Contract Type")
    axes[0].grid(axis="y", alpha=0.3)

    # Count bar
    bars2 = axes[1].bar(grouped[col].astype(str), grouped["Count"],
                        color=colors[:len(grouped)], edgecolor="#0F172A", width=0.55)
    for bar, val in zip(bars2, grouped["Count"]):
        axes[1].text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 20, f"{val:,}",
                     ha="center", fontsize=11, color="#E2E8F0")
    axes[1].set_ylabel("Number of Customers")
    axes[1].set_title("Customer Count by Contract Type")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "03_contract_analysis.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 4. MONTHLY CHARGES ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

def plot_monthly_charges(df: pd.DataFrame) -> str:
    if "MonthlyCharges" not in df.columns or "Churn" not in df.columns:
        return ""
    set_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Monthly Charges Analysis", fontsize=16, fontweight="bold")

    # KDE
    for val, color, label in [(0, CHURN_COLORS[0], "No Churn"),
                               (1, CHURN_COLORS[1], "Churn")]:
        subset = df[df["Churn"] == val]["MonthlyCharges"]
        axes[0].hist(subset, bins=35, alpha=0.55, color=color, label=label,
                     density=True, edgecolor="#0F172A")
        subset.plot.kde(ax=axes[0], color=color, lw=2.5)
    axes[0].set_xlabel("Monthly Charges ($)")
    axes[0].set_ylabel("Density")
    axes[0].set_title("Monthly Charges Distribution")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Violin
    data_groups = [
        df[df["Churn"] == 0]["MonthlyCharges"].values,
        df[df["Churn"] == 1]["MonthlyCharges"].values,
    ]
    vp = axes[1].violinplot(data_groups, positions=[1, 2], showmedians=True)
    for i, (pc, color) in enumerate(zip(vp["bodies"], CHURN_COLORS)):
        pc.set_facecolor(color); pc.set_alpha(0.7)
    vp["cmedians"].set_color("white"); vp["cmedians"].set_lw(2)
    vp["cbars"].set_color("#94A3B8"); vp["cmins"].set_color("#94A3B8"); vp["cmaxes"].set_color("#94A3B8")
    axes[1].set_xticks([1, 2]); axes[1].set_xticklabels(["No Churn", "Churn"])
    axes[1].set_ylabel("Monthly Charges ($)")
    axes[1].set_title("Monthly Charges Violin Plot")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "04_monthly_charges.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 5. FEATURE CORRELATION HEATMAP
# ──────────────────────────────────────────────────────────────────────────────

def plot_correlation_heatmap(df: pd.DataFrame) -> str:
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        return ""

    set_style()
    corr = num_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f",
        cmap="coolwarm", center=0, linewidths=0.5,
        linecolor="#0F172A", ax=ax,
        cbar_kws={"shrink": 0.8},
        annot_kws={"size": 8}
    )
    ax.set_title("Feature Correlation Heatmap", fontsize=16, fontweight="bold", pad=12)
    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "05_correlation_heatmap.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1E293B")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 6. CHURN BY DEMOGRAPHICS
# ──────────────────────────────────────────────────────────────────────────────

def plot_churn_by_demographics(df: pd.DataFrame) -> str:
    if "Churn" not in df.columns:
        return ""
    set_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Churn by Customer Demographics", fontsize=16, fontweight="bold")

    demo_cols = ["gender", "SeniorCitizen", "Partner", "Dependents"]
    demo_labels = {
        "gender":        {0: "Female", 1: "Male"},
        "SeniorCitizen": {0: "Not Senior", 1: "Senior"},
        "Partner":       {0: "No Partner", 1: "Has Partner"},
        "Dependents":    {0: "No Dependents", 1: "Has Dependents"},
    }

    for ax, col in zip(axes.flat, demo_cols):
        if col not in df.columns:
            ax.axis("off"); continue
        grouped = df.groupby(col)["Churn"].mean() * 100
        labels  = [demo_labels.get(col, {}).get(k, str(k)) for k in grouped.index]
        colors  = [PALETTE["positive"] if v < 30 else PALETTE["negative"] for v in grouped.values]
        bars = ax.bar(labels, grouped.values, color=colors, edgecolor="#0F172A", width=0.5)
        for bar, val in zip(bars, grouped.values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5, f"{val:.1f}%",
                    ha="center", fontsize=11, color="#E2E8F0")
        ax.set_title(f"Churn Rate by {col.replace('_', ' ').title()}", fontsize=12)
        ax.set_ylabel("Churn Rate (%)")
        ax.grid(axis="y", alpha=0.3)
        ax.set_ylim(0, grouped.max() * 1.25)

    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "06_churn_demographics.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 7. INTERNET SERVICE & PAYMENT METHOD
# ──────────────────────────────────────────────────────────────────────────────

def plot_service_payment_analysis(df: pd.DataFrame) -> str:
    if "Churn" not in df.columns:
        return ""
    set_style()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Internet Service & Payment Method Analysis", fontsize=16, fontweight="bold")

    for ax, col, title in [
        (axes[0], "InternetService", "Churn by Internet Service"),
        (axes[1], "PaymentMethod",   "Churn by Payment Method"),
    ]:
        if col not in df.columns:
            ax.axis("off"); continue
        grouped = df.groupby(col)["Churn"].mean() * 100
        bars = ax.barh(
            [str(x) for x in grouped.index], grouped.values,
            color=PALETTE["primary"], edgecolor="#0F172A"
        )
        for bar, val in zip(bars, grouped.values):
            ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%", va="center", fontsize=10, color="#E2E8F0")
        ax.set_xlabel("Churn Rate (%)")
        ax.set_title(title, fontsize=12)
        ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "07_service_payment.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 8. MONTHLY CHARGES vs TENURE SCATTER
# ──────────────────────────────────────────────────────────────────────────────

def plot_charges_vs_tenure(df: pd.DataFrame) -> str:
    if not all(c in df.columns for c in ["tenure", "MonthlyCharges", "Churn"]):
        return ""
    set_style()
    fig, ax = plt.subplots(figsize=(10, 6))

    for val, color, label in [(0, CHURN_COLORS[0], "No Churn"),
                               (1, CHURN_COLORS[1], "Churn")]:
        subset = df[df["Churn"] == val]
        ax.scatter(subset["tenure"], subset["MonthlyCharges"],
                   c=color, label=label, alpha=0.4, s=15, edgecolors="none")

    ax.set_xlabel("Tenure (months)")
    ax.set_ylabel("Monthly Charges ($)")
    ax.set_title("Monthly Charges vs Tenure by Churn Status", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "08_charges_vs_tenure.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 9. CHURN BY TOTAL CHARGES QUARTILE
# ──────────────────────────────────────────────────────────────────────────────

def plot_churn_by_total_charges(df: pd.DataFrame) -> str:
    if "TotalCharges" not in df.columns or "Churn" not in df.columns:
        return ""
    set_style()
    df2 = df.copy()
    df2["TotalChargesQ"] = pd.qcut(df2["TotalCharges"], q=4,
                                    labels=["Q1 (Low)", "Q2", "Q3", "Q4 (High)"])
    grouped = df2.groupby("TotalChargesQ", observed=True)["Churn"].mean() * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [PALETTE["positive"], PALETTE["secondary"], PALETTE["accent"], PALETTE["negative"]]
    bars = ax.bar(grouped.index.astype(str), grouped.values,
                  color=colors, edgecolor="#0F172A", width=0.55)
    for bar, val in zip(bars, grouped.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3, f"{val:.1f}%",
                ha="center", fontsize=11, color="#E2E8F0")
    ax.set_ylabel("Churn Rate (%)")
    ax.set_xlabel("Total Charges Quartile")
    ax.set_title("Churn Rate by Total Charges Quartile", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = os.path.join(REPORTS_DIR, "09_churn_by_total_charges.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0F172A")
    plt.close(fig)
    logger.info(f"Saved → {out}")
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 10. FULL EDA PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

def run_eda(df_raw: pd.DataFrame, df_encoded: pd.DataFrame) -> list:
    """
    Run all EDA plots.
    df_raw     = before encoding (for human-readable labels)
    df_encoded = after encoding  (for correlation heatmap)
    Returns list of output paths.
    """
    ensure_dirs()
    outputs = []

    outputs.append(plot_churn_distribution(df_encoded))
    outputs.append(plot_tenure_analysis(df_encoded))
    outputs.append(plot_contract_analysis(df_raw))
    outputs.append(plot_monthly_charges(df_encoded))
    outputs.append(plot_correlation_heatmap(df_encoded))
    outputs.append(plot_churn_by_demographics(df_encoded))
    outputs.append(plot_service_payment_analysis(df_raw))
    outputs.append(plot_charges_vs_tenure(df_encoded))
    outputs.append(plot_churn_by_total_charges(df_encoded))

    saved = [p for p in outputs if p]
    logger.info(f"\nEDA complete. {len(saved)} figures saved to reports/figures/")
    return saved


if __name__ == "__main__":
    from src.preprocessing import load_data, clean_data, handle_outliers, encode_features

    df_raw = load_data()
    df_raw = clean_data(df_raw)
    df_raw = handle_outliers(df_raw)

    df_enc, _ = encode_features(df_raw.copy())

    run_eda(df_raw, df_enc)
    print("EDA complete.")
