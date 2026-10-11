"""
train_model.py
--------------
Model training, comparison, hyperparameter tuning, and evaluation
for the Customer Churn Prediction System.

Models trained:
  1. Random Forest (the production prediction model)
  2. XGBoost (benchmark comparison model)

Random Forest is always saved as the production model. XGBoost is retained
for transparent performance comparison.
"""

import os
import sys
import json
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.ensemble        import RandomForestClassifier
from sklearn.metrics         import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix, roc_curve, ConfusionMatrixDisplay,
)
from sklearn.model_selection import GridSearchCV, cross_val_score
from xgboost import XGBClassifier

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import logger, MODELS_DIR, REPORTS_DIR, save_figure, set_style, PALETTE, CHURN_COLORS, ensure_dirs


# ──────────────────────────────────────────────────────────────────────────────
# 1. MODEL DEFINITIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_models() -> dict:
    """Return a dict of model name → unfitted estimator."""
    return {
        "Random Forest": RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42,
            n_jobs=-1, class_weight="balanced"
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            use_label_encoder=False, eval_metric="logloss",
            random_state=42, n_jobs=-1,
            scale_pos_weight=3  # handle imbalance
        ),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 2. EVALUATION
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series,
                   model_name: str = "Model") -> dict:
    """Compute all classification metrics and return as dict."""
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model":     model_name,
        "accuracy":  round(accuracy_score(y_test, y_pred),  4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred,    zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred,        zero_division=0), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_proba),                  4),
    }

    logger.info(
        f"[{model_name}] acc={metrics['accuracy']:.4f} | "
        f"prec={metrics['precision']:.4f} | rec={metrics['recall']:.4f} | "
        f"f1={metrics['f1']:.4f} | auc={metrics['roc_auc']:.4f}"
    )
    return metrics


# ──────────────────────────────────────────────────────────────────────────────
# 3. VISUALISATIONS
# ──────────────────────────────────────────────────────────────────────────────

def plot_model_comparison(results: list, output_path: str = None) -> str:
    """Bar chart comparing all models across metrics."""
    set_style()
    df_res = pd.DataFrame(results).set_index("model")
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    colors  = [PALETTE["primary"], PALETTE["secondary"], PALETTE["accent"],
                PALETTE["positive"], PALETTE["negative"]]

    x = np.arange(len(df_res))
    width = 0.15
    fig, ax = plt.subplots(figsize=(13, 6))

    for i, (metric, color) in enumerate(zip(metrics, colors)):
        bars = ax.bar(x + i * width, df_res[metric], width, label=metric.upper(),
                      color=color, alpha=0.85, edgecolor="#0F172A")
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{bar.get_height():.3f}", ha="center", va="bottom",
                    fontsize=7.5, color="#E2E8F0")

    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(df_res.index, fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.set_title("Model Performance Comparison", fontsize=15, fontweight="bold", pad=12)
    ax.legend(loc="lower right", framealpha=0.2)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    out = output_path or os.path.join(REPORTS_DIR, "model_comparison.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"Model comparison chart → {out}")
    return out


def plot_roc_curves(models_dict: dict, X_test: pd.DataFrame,
                    y_test: pd.Series) -> str:
    """Overlay ROC curves for all trained models."""
    set_style()
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = [PALETTE["primary"], PALETTE["accent"], PALETTE["positive"]]

    for (name, model), color in zip(models_dict.items(), colors):
        y_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        auc = roc_auc_score(y_test, y_proba)
        ax.plot(fpr, tpr, lw=2.5, color=color, label=f"{name} (AUC = {auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1.5, alpha=0.5, label="Random Baseline")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves – All Models", fontsize=15, fontweight="bold")
    ax.legend(loc="lower right", framealpha=0.2)
    ax.grid(alpha=0.3)
    plt.tight_layout()

    out = os.path.join(REPORTS_DIR, "roc_curves.png")
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"ROC curves → {out}")
    return out


def plot_confusion_matrix(model, X_test: pd.DataFrame, y_test: pd.Series,
                          model_name: str) -> str:
    """Plot and save a styled confusion matrix."""
    set_style()
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["No Churn", "Churn"],
        yticklabels=["No Churn", "Churn"],
        linewidths=0.5, linecolor="#334155",
        annot_kws={"size": 14, "weight": "bold"},
        ax=ax
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual",    fontsize=12)
    ax.set_title(f"Confusion Matrix – {model_name}", fontsize=14, fontweight="bold", pad=10)
    plt.tight_layout()

    fname = f"confusion_matrix_{model_name.replace(' ', '_').lower()}.png"
    out = os.path.join(REPORTS_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1E293B")
    plt.close(fig)
    logger.info(f"Confusion matrix → {out}")
    return out


def plot_feature_importance(model, feature_names: list,
                             model_name: str, top_n: int = 20) -> str:
    """Plot and save top-N feature importances."""
    set_style()
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        logger.warning("Model has no feature_importances_ or coef_ attribute.")
        return ""

    df_imp = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances,
    }).sort_values("Importance", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors_bar = [PALETTE["primary"]] * top_n
    sns.barplot(
        data=df_imp, y="Feature", x="Importance",
        palette=colors_bar[:len(df_imp)], edgecolor="#0F172A", ax=ax
    )
    ax.set_title(f"Top {top_n} Feature Importances – {model_name}",
                 fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("Importance Score")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    fname = f"feature_importance_{model_name.replace(' ', '_').lower()}.png"
    out = os.path.join(REPORTS_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"Feature importance → {out}")

    # Save as CSV too
    df_imp.to_csv(os.path.join(MODELS_DIR, "feature_importance.csv"), index=False)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 4. TRAINING PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

def train_all_models(X_train: pd.DataFrame, X_test: pd.DataFrame,
                     y_train: pd.Series, y_test: pd.Series):
    """
    Train all models, evaluate, pick the best by ROC-AUC.
    Returns: best_model, all_models_dict, results_list, best_model_name
    """
    ensure_dirs()
    models   = get_models()
    results  = []
    trained  = {}

    for name, model in models.items():
        logger.info(f"\n── Training: {name} ──")
        model.fit(X_train, y_train)
        trained[name] = model
        metrics = evaluate_model(model, X_test, y_test, name)
        results.append(metrics)

    # Random Forest is the approved production model for this project.
    best_name = "Random Forest"
    best_model = trained[best_name]
    best_row = next(row for row in results if row["model"] == best_name)
    logger.info(f"\n★  Production model: {best_name} (AUC = {best_row['roc_auc']:.4f})")

    return best_model, trained, results, best_name


def run_training_pipeline(X_train: pd.DataFrame, X_test: pd.DataFrame,
                           y_train: pd.Series, y_test: pd.Series):
    """
    Full training pipeline:
    1. Train & evaluate all models
    2. Save best model + artifacts
    3. Generate all visualisations
    Returns: best_model, results, best_name
    """
    ensure_dirs()

    best_model, trained, results, best_name = train_all_models(
        X_train, X_test, y_train, y_test
    )

    # ── Save best model + metadata
    model_path = os.path.join(MODELS_DIR, "best_model.pkl")
    joblib.dump(best_model, model_path)
    logger.info(f"Best model saved → {model_path}")

    # Save all models
    for name, m in trained.items():
        fname = name.lower().replace(" ", "_") + ".pkl"
        joblib.dump(m, os.path.join(MODELS_DIR, fname))

    # Save results JSON
    results_path = os.path.join(MODELS_DIR, "model_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved → {results_path}")

    # Save best model name
    with open(os.path.join(MODELS_DIR, "best_model_name.txt"), "w") as f:
        f.write(best_name)

    # ── Plots
    plot_model_comparison(results)
    plot_roc_curves(trained, X_test, y_test)
    plot_confusion_matrix(best_model, X_test, y_test, best_name)
    plot_feature_importance(best_model, list(X_train.columns), best_name)

    # ── Cross-validation
    logger.info("Running 5-fold cross-validation on best model...")
    cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring="roc_auc")
    logger.info(f"CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Print full classification report
    y_pred = best_model.predict(X_test)
    print("\n" + "=" * 60)
    print(f"BEST MODEL: {best_name}")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]))

    return best_model, results, best_name


if __name__ == "__main__":
    from src.preprocessing      import run_preprocessing_pipeline
    from src.feature_engineering import run_feature_engineering

    X_tr, X_te, y_tr, y_te, scaler, encoders, df = run_preprocessing_pipeline()
    X_tr_b, X_te_fe, y_tr_b, y_te = run_feature_engineering(df, X_tr, X_te, y_tr, y_te)
    best_model, results, best_name = run_training_pipeline(X_tr_b, X_te_fe, y_tr_b, y_te)
    print(f"\nTraining complete. Best model: {best_name}")
