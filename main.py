"""
main.py
-------
Master orchestration script for the Customer Churn Prediction System.
Run this file to execute the complete end-to-end pipeline:

  python main.py

Pipeline:
  1. Data loading & preprocessing
  2. Feature engineering + SMOTE
  3. EDA visualisations
  4. SQL database + analytics
  5. Model training & evaluation
  6. Artifacts saved to disk

After running main.py, launch the dashboard with:
  streamlit run dashboard/app.py
"""

import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.utils import logger, print_separator, ensure_dirs
from src.preprocessing       import run_preprocessing_pipeline, load_data, clean_data, handle_outliers, encode_features
from src.feature_engineering import run_feature_engineering
from src.eda                 import run_eda
from src.sql_integration     import run_sql_pipeline
from src.train_model         import run_training_pipeline


def main():
    start_time = time.time()

    print_separator("CUSTOMER CHURN PREDICTION SYSTEM")
    print("  End-to-End ML Pipeline")
    print("  Author: Data Science Portfolio Project")
    print_separator()

    ensure_dirs()

    # ── STEP 1: Preprocessing
    print_separator("STEP 1: Data Loading & Preprocessing")
    X_train, X_test, y_train, y_test, scaler, encoders, df_processed = \
        run_preprocessing_pipeline()

    # Also keep the pre-encoded raw df for EDA
    df_raw = load_data()
    df_raw = clean_data(df_raw)
    df_raw = handle_outliers(df_raw)

    # ── STEP 2: Feature Engineering
    print_separator("STEP 2: Feature Engineering & SMOTE")
    X_train_bal, X_test_fe, y_train_bal, y_test = run_feature_engineering(
        df_processed, X_train, X_test, y_train, y_test
    )

    # ── STEP 3: EDA
    print_separator("STEP 3: Exploratory Data Analysis")
    saved_figures = run_eda(df_raw, df_processed)
    print(f"  {len(saved_figures)} figures saved to reports/figures/")

    # ── STEP 4: Model Training & Evaluation
    print_separator("STEP 4: Model Training & Evaluation")
    best_model, results, best_name = run_training_pipeline(
        X_train_bal, X_test_fe, y_train_bal, y_test
    )

    # ── STEP 5: SQL Database & Analytics
    print_separator("STEP 5: SQL Database & Analytics")
    from src.predict import predict_batch
    df_scored = predict_batch(df_processed, best_model)
    sql_results = run_sql_pipeline(df_scored)

    # ── SUMMARY
    elapsed = time.time() - start_time
    print_separator("PIPELINE COMPLETE")
    print(f"  [OK] Dataset rows:      {len(df_processed):,}")
    print(f"  [OK] Features used:     {X_test_fe.shape[1]}")
    print(f"  [OK] EDA figures:       {len(saved_figures)}")
    print(f"  [OK] Best model:        {best_name}")

    best_result = next(r for r in results if r["model"] == best_name)
    print(f"  [OK] ROC-AUC:           {best_result['roc_auc']:.4f}")
    print(f"  [OK] F1-Score:          {best_result['f1']:.4f}")
    print(f"  [OK] Elapsed time:      {elapsed:.1f}s")
    print()
    print("  Next step - Launch dashboard:")
    print("    streamlit run dashboard/app.py")
    print_separator()


if __name__ == "__main__":
    main()
