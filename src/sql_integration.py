"""
sql_integration.py
-------------------
SQLite Database Management & Business Analytics Subsystem.

Provides:
  1. Relational schema setup (customers, service_contracts, churn_predictions)
  2. Safe parameterized storage of customer attributes and model prediction runs
  3. Run tracking & multi-run history isolation (run_id, prediction_timestamp)
  4. Verified SQL analytics for MRR/ARR at risk, ARPU, high-value churners, cohorts
"""

import os
import sys
import sqlite3
import datetime
import uuid
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils import logger, BASE_DIR, ensure_dirs

DB_PATH = os.path.join(BASE_DIR, "data", "churn.db")


# ──────────────────────────────────────────────────────────────────────────────
# 1. DATABASE INITIALIZATION & SCHEMA CREATION
# ──────────────────────────────────────────────────────────────────────────────

def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create robust SQLite connection with WAL journal mode and busy timeout."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 30000;")
        conn.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass
    return conn


def init_db(db_path: str = DB_PATH) -> str:
    """Initialize SQLite relational database schema with constraints and indexes."""
    ensure_dirs()
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        # Check if legacy customers table exists without customer_id column
        cursor.execute("PRAGMA table_info(customers);")
        cust_cols = [row[1] for row in cursor.fetchall()]
        if cust_cols and "customer_id" not in cust_cols:
            logger.info("Migrating legacy SQLite database schema...")
            cursor.execute("DROP TABLE IF EXISTS service_contracts;")
            cursor.execute("DROP TABLE IF EXISTS churn_predictions;")
            cursor.execute("DROP TABLE IF EXISTS customers;")

        # Table 1: customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id       TEXT PRIMARY KEY,
                gender            TEXT,
                senior_citizen    INTEGER DEFAULT 0,
                partner           TEXT,
                dependents        TEXT,
                tenure            INTEGER DEFAULT 0,
                phone_service     TEXT,
                multiple_lines    TEXT,
                internet_service  TEXT,
                online_security   TEXT,
                online_backup     TEXT,
                device_protection TEXT,
                tech_support      TEXT,
                streaming_tv      TEXT,
                streaming_movies  TEXT,
                contract          TEXT,
                paperless_billing TEXT,
                payment_method    TEXT,
                monthly_charges   REAL DEFAULT 0.0,
                total_charges     REAL DEFAULT 0.0,
                created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 2: service_contracts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_contracts (
                customer_id      TEXT PRIMARY KEY,
                contract         TEXT,
                internet_service TEXT,
                monthly_charges  REAL DEFAULT 0.0,
                total_charges    REAL DEFAULT 0.0,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
        """)

        # Table 3: churn_predictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS churn_predictions (
                prediction_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id          TEXT NOT NULL,
                predicted_churn      INTEGER NOT NULL,
                churn_probability    REAL NOT NULL,
                risk_category        TEXT NOT NULL,
                actual_churn         INTEGER,
                run_id               TEXT NOT NULL,
                prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );
        """)

        # Indexes for query performance & run filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_run ON churn_predictions(run_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_cust ON churn_predictions(customer_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id);")

        conn.commit()
        logger.info(f"Database initialized cleanly → {db_path}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise e
    finally:
        conn.close()

    return db_path


# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA STORAGE & PREDICTION RUN PERSISTENCE
# ──────────────────────────────────────────────────────────────────────────────

def clean_int(val, default=0) -> int:
    """Safely convert any value to int, defaulting if NaN, None, or invalid."""
    if val is None:
        return default
    try:
        res = pd.to_numeric(val, errors="coerce")
        if pd.isna(res) or np.isinf(res):
            return default
        return int(res)
    except Exception:
        return default

def clean_float(val, default=0.0) -> float:
    """Safely convert any value to float, defaulting if NaN, None, or invalid."""
    if val is None:
        return default
    try:
        res = pd.to_numeric(val, errors="coerce")
        if pd.isna(res) or np.isinf(res):
            return default
        return float(res)
    except Exception:
        return default

def store_predictions_to_sqlite(df_predicted: pd.DataFrame, run_id: str = None, db_path: str = DB_PATH) -> tuple[str, str]:
    """
    Persist customer attributes and model prediction outputs into SQLite.
    Associates predictions with a unique run_id and timestamp using fast batch executemany.
    """
    if df_predicted is None or df_predicted.empty:
        logger.warning("Empty DataFrame passed to store_predictions_to_sqlite. Skipping.")
        return db_path, run_id or ""

    init_db(db_path)
    
    if not run_id:
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"RUN_{timestamp_str}_{uuid.uuid4().hex[:6]}"

    df = df_predicted.copy()
    
    # Map column names cleanly once
    col_map = {str(c).strip().lower().replace("_", "").replace(" ", ""): c for c in df.columns}
    def get_series(candidates, default=None):
        for cand in candidates:
            c_clean = cand.lower().replace("_", "").replace(" ", "")
            if c_clean in col_map:
                return df[col_map[c_clean]]
        return default

    # Extract Series with fallbacks
    id_s = get_series(["customerid", "customer_id", "id", "custid", "accountid"])
    if id_s is not None:
        cust_ids = [str(v).strip() if pd.notna(v) and str(v).strip() not in ["None", "nan", ""] else f"CUST-{i+1:05d}"
                    for i, v in enumerate(id_s)]
    else:
        cust_ids = [f"CUST-{i+1:05d}" for i in range(len(df))]

    # Numeric billing columns
    mc_s = get_series(["monthlycharges", "monthly_charges", "monthly", "charges"])
    monthly_charges = [clean_float(v, 0.0) for v in mc_s] if mc_s is not None else [0.0] * len(df)

    t_s = get_series(["tenure", "months"])
    tenures = [clean_int(v, 0) for v in t_s] if t_s is not None else [0] * len(df)

    tc_s = get_series(["totalcharges", "total_charges", "total"])
    if tc_s is not None:
        total_charges = [clean_float(v, monthly_charges[i] * tenures[i]) for i, v in enumerate(tc_s)]
    else:
        total_charges = [monthly_charges[i] * tenures[i] for i in range(len(df))]

    # Categorical string columns
    def str_col(candidates, default="No"):
        s = get_series(candidates)
        if s is not None:
            return [str(v) if pd.notna(v) else default for v in s]
        return [default] * len(df)

    genders = str_col(["gender"], "Unknown")
    senior_s = get_series(["seniorcitizen", "senior_citizen", "senior"])
    seniors = [clean_int(v, 0) for v in senior_s] if senior_s is not None else [0] * len(df)
    partners = str_col(["partner"], "No")
    dependents_list = str_col(["dependents"], "No")
    phone_svcs = str_col(["phoneservice", "phone_service"], "Yes")
    mult_lines = str_col(["multiplelines", "multiple_lines"], "No")
    internet_svcs = str_col(["internetservice", "internet_service", "internet"], "Fiber optic")
    secs = str_col(["onlinesecurity", "online_security"], "No")
    backups = str_col(["onlinebackup", "online_backup"], "No")
    prots = str_col(["deviceprotection", "device_protection"], "No")
    supports = str_col(["techsupport", "tech_support"], "No")
    tvs = str_col(["streamingtv", "streaming_tv"], "No")
    movies_list = str_col(["streamingmovies", "streaming_movies"], "No")
    contracts = str_col(["contract", "contract_type"], "Month-to-month")
    paperless_list = str_col(["paperlessbilling", "paperless_billing"], "Yes")
    payments = str_col(["paymentmethod", "payment_method"], "Electronic check")

    # Prediction columns
    prob_s = get_series(["churnprobability", "churn_probability", "probability", "prob"])
    if prob_s is not None:
        probs = [clean_float(v, 0.0) for v in prob_s]
        probs = [p / 100.0 if p > 1.0 else p for p in probs]
    else:
        probs = [0.0] * len(df)

    pred_s = get_series(["churnprediction", "churn_prediction", "predicted_churn", "prediction"])
    if pred_s is not None:
        preds = []
        for i, val in enumerate(pred_s):
            v_str = str(val).strip().lower()
            if v_str in ["1", "yes", "true", "will churn", "churn", "1.0"]:
                preds.append(1)
            elif v_str in ["0", "no", "false", "retained", "stay", "0.0"]:
                preds.append(0)
            else:
                preds.append(1 if probs[i] >= 0.50 else 0)
    else:
        preds = [1 if p >= 0.50 else 0 for p in probs]

    risk_s = get_series(["risklevel", "risk_level", "riskcategory", "risk_category"])
    if risk_s is not None:
        risk_cats = []
        for i, val in enumerate(risk_s):
            v_str = str(val).strip().lower()
            if "high" in v_str:
                risk_cats.append("High")
            elif "medium" in v_str or "moderate" in v_str:
                risk_cats.append("Medium")
            elif "low" in v_str:
                risk_cats.append("Low")
            else:
                risk_cats.append("High" if probs[i] >= 0.65 else ("Medium" if probs[i] >= 0.40 else "Low"))
    else:
        risk_cats = ["High" if p >= 0.65 else ("Medium" if p >= 0.40 else "Low") for p in probs]

    act_s = get_series(["churn", "actual_churn", "target", "actual"])
    if act_s is not None:
        actuals = []
        for val in act_s:
            if pd.notna(val):
                v_str = str(val).strip().lower()
                if v_str in ["1", "yes", "true", "churn", "1.0"]:
                    actuals.append(1)
                elif v_str in ["0", "no", "false", "retained", "0.0"]:
                    actuals.append(0)
                else:
                    actuals.append(None)
            else:
                actuals.append(None)
    else:
        actuals = [None] * len(df)

    now_iso = datetime.datetime.now().isoformat()
    n = len(df)

    customers_data = [
        (cust_ids[i], genders[i], seniors[i], partners[i], dependents_list[i], tenures[i],
         phone_svcs[i], mult_lines[i], internet_svcs[i], secs[i], backups[i], prots[i],
         supports[i], tvs[i], movies_list[i], contracts[i], paperless_list[i], payments[i],
         monthly_charges[i], total_charges[i], now_iso)
        for i in range(n)
    ]

    contracts_data = [
        (cust_ids[i], contracts[i], internet_svcs[i], monthly_charges[i], total_charges[i])
        for i in range(n)
    ]

    predictions_data = [
        (cust_ids[i], preds[i], probs[i], risk_cats[i], actuals[i], run_id, now_iso)
        for i in range(n)
    ]

    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN IMMEDIATE;")
        cursor.executemany("""
            INSERT INTO customers (
                customer_id, gender, senior_citizen, partner, dependents, tenure,
                phone_service, multiple_lines, internet_service, online_security,
                online_backup, device_protection, tech_support, streaming_tv,
                streaming_movies, contract, paperless_billing, payment_method,
                monthly_charges, total_charges, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(customer_id) DO UPDATE SET
                tenure = excluded.tenure,
                contract = excluded.contract,
                payment_method = excluded.payment_method,
                monthly_charges = excluded.monthly_charges,
                total_charges = excluded.total_charges;
        """, customers_data)

        cursor.executemany("""
            INSERT INTO service_contracts (
                customer_id, contract, internet_service, monthly_charges, total_charges
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(customer_id) DO UPDATE SET
                contract = excluded.contract,
                internet_service = excluded.internet_service,
                monthly_charges = excluded.monthly_charges,
                total_charges = excluded.total_charges;
        """, contracts_data)

        cursor.executemany("""
            INSERT INTO churn_predictions (
                customer_id, predicted_churn, churn_probability, risk_category,
                actual_churn, run_id, prediction_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, predictions_data)

        conn.commit()
        logger.info(f"Successfully stored {len(df):,} customer prediction records under run_id '{run_id}' → {db_path}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting records into SQLite: {e}")
        raise e
    finally:
        conn.close()

    return db_path, run_id


def store_to_sqlite(df: pd.DataFrame, table_name: str = "customers") -> str:
    """Legacy helper for backward compatibility."""
    db_path, _ = store_predictions_to_sqlite(df)
    return db_path


# ──────────────────────────────────────────────────────────────────────────────
# 3. QUERY HELPERS & RUN IDENTIFICATION
# ──────────────────────────────────────────────────────────────────────────────

def run_query(sql: str, params: tuple = (), db_path: str = DB_PATH) -> pd.DataFrame:
    """Execute parameterized SQL query and return results as DataFrame."""
    conn = get_db_connection(db_path)
    try:
        return pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        logger.warning(f"SQL execution error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


def get_latest_run_id(db_path: str = DB_PATH) -> str:
    """Fetch the latest prediction run_id from churn_predictions table."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT run_id FROM churn_predictions ORDER BY prediction_timestamp DESC, prediction_id DESC LIMIT 1;")
        row = cursor.fetchone()
        return row[0] if row else ""
    except Exception:
        return ""
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# 4. BUSINESS ANALYTICS (PREDICTED CHURN & REVENUE AT RISK)
# ──────────────────────────────────────────────────────────────────────────────

def run_analytics(db_path: str = DB_PATH, run_id: str = None) -> dict:
    """
    Execute all key business analytics queries based on the latest valid prediction run.
    Calculates predicted MRR/ARR at risk, ARPU, high-value churn accounts, and cohort trends.
    """
    init_db(db_path)

    if not run_id:
        run_id = get_latest_run_id(db_path)

    results = {}

    if not run_id:
        logger.warning("No prediction runs found in SQLite database.")
        return results

    # Base CTE for filtering latest run predictions joined with customer records
    base_join = """
        FROM customers c
        INNER JOIN churn_predictions p
            ON c.customer_id = p.customer_id
        WHERE p.run_id = ?
    """

    queries = {
        "churn_summary": f"""
            SELECT
                COUNT(c.customer_id)                                                AS total_customers,
                COALESCE(SUM(p.predicted_churn), 0)                                 AS total_churned,
                COUNT(c.customer_id) - COALESCE(SUM(p.predicted_churn), 0)          AS total_retained,
                ROUND(100.0 * COALESCE(SUM(p.predicted_churn), 0) / NULLIF(COUNT(c.customer_id), 0), 2) AS churn_rate_pct
            {base_join}
        """,

        "churn_by_contract": f"""
            SELECT
                c.contract                                                          AS Contract,
                COUNT(c.customer_id)                                                AS total_customers,
                COALESCE(SUM(p.predicted_churn), 0)                                 AS churned,
                ROUND(100.0 * COALESCE(SUM(p.predicted_churn), 0) / NULLIF(COUNT(c.customer_id), 0), 2) AS churn_rate_pct,
                ROUND(AVG(c.monthly_charges), 2)                                    AS avg_monthly_charges,
                ROUND(SUM(CASE WHEN p.predicted_churn = 1 THEN c.monthly_charges ELSE 0 END), 2) AS mrr_at_risk
            {base_join}
            GROUP BY c.contract
            ORDER BY churn_rate_pct DESC
        """,

        "churn_by_payment": f"""
            SELECT
                c.payment_method                                                    AS PaymentMethod,
                COUNT(c.customer_id)                                                AS total_customers,
                COALESCE(SUM(p.predicted_churn), 0)                                 AS churned,
                ROUND(100.0 * COALESCE(SUM(p.predicted_churn), 0) / NULLIF(COUNT(c.customer_id), 0), 2) AS churn_rate_pct,
                ROUND(AVG(c.monthly_charges), 2)                                    AS avg_charges,
                ROUND(SUM(CASE WHEN p.predicted_churn = 1 THEN c.monthly_charges ELSE 0 END), 2) AS mrr_at_risk
            {base_join}
            GROUP BY c.payment_method
            ORDER BY churn_rate_pct DESC
        """,

        "revenue_by_segment": f"""
            SELECT
                CASE WHEN p.predicted_churn = 1 THEN 'Predicted Churned' ELSE 'Predicted Retained' END AS segment,
                COUNT(c.customer_id)                                                AS customers,
                ROUND(AVG(c.monthly_charges), 2)                                    AS avg_monthly_revenue,
                ROUND(SUM(c.monthly_charges), 2)                                    AS total_monthly_revenue,
                ROUND(AVG(c.total_charges), 2)                                      AS avg_lifetime_value
            {base_join}
            GROUP BY segment
            ORDER BY total_monthly_revenue DESC
        """,

        "top_churn_segments": f"""
            SELECT
                c.contract                                                          AS Contract,
                c.internet_service                                                  AS InternetService,
                COUNT(c.customer_id)                                                AS total,
                COALESCE(SUM(p.predicted_churn), 0)                                 AS churned,
                ROUND(100.0 * COALESCE(SUM(p.predicted_churn), 0) / NULLIF(COUNT(c.customer_id), 0), 2) AS churn_rate_pct,
                ROUND(SUM(CASE WHEN p.predicted_churn = 1 THEN c.monthly_charges ELSE 0 END), 2) AS mrr_at_risk,
                ROUND(AVG(c.monthly_charges), 2)                                    AS avg_charges
            {base_join}
            GROUP BY c.contract, c.internet_service
            ORDER BY churn_rate_pct DESC
            LIMIT 10
        """,

        "tenure_cohort_analysis": f"""
            SELECT
                CASE
                    WHEN c.tenure <= 12 THEN '0-12 months'
                    WHEN c.tenure <= 24 THEN '13-24 months'
                    WHEN c.tenure <= 48 THEN '25-48 months'
                    ELSE '49+ months'
                END AS tenure_cohort,
                COUNT(c.customer_id)                                                AS total_customers,
                COALESCE(SUM(p.predicted_churn), 0)                                 AS churned,
                ROUND(100.0 * COALESCE(SUM(p.predicted_churn), 0) / NULLIF(COUNT(c.customer_id), 0), 2) AS churn_rate_pct
            {base_join}
            GROUP BY tenure_cohort
            ORDER BY churn_rate_pct DESC
        """,

        "revenue_at_risk": f"""
            SELECT
                ROUND(SUM(CASE WHEN p.predicted_churn = 1 THEN c.monthly_charges ELSE 0 END), 2) AS monthly_revenue_at_risk,
                ROUND(12.0 * SUM(CASE WHEN p.predicted_churn = 1 THEN c.monthly_charges ELSE 0 END), 2) AS annual_revenue_at_risk,
                ROUND(AVG(c.monthly_charges), 2)                                    AS arpu,
                ROUND(AVG(CASE WHEN p.predicted_churn = 1 THEN c.monthly_charges END), 2) AS churner_arpu,
                COUNT(CASE WHEN p.predicted_churn = 1 AND c.monthly_charges >= (SELECT AVG(monthly_charges) FROM customers) THEN 1 END) AS high_value_churn_count,
                COUNT(c.customer_id)                                                AS total_customers,
                COALESCE(SUM(p.predicted_churn), 0)                                 AS predicted_churned_count
            {base_join}
        """,

        "high_risk_customers": f"""
            SELECT
                c.customer_id,
                c.tenure,
                c.monthly_charges,
                c.total_charges,
                c.contract,
                c.payment_method,
                c.internet_service,
                p.predicted_churn,
                p.churn_probability,
                p.risk_category
            {base_join}
              AND (p.predicted_churn = 1 OR p.churn_probability >= 0.50)
            ORDER BY p.churn_probability DESC, c.monthly_charges DESC
            LIMIT 25
        """
    }

    for name, sql in queries.items():
        try:
            results[name] = run_query(sql, params=(run_id,), db_path=db_path)
            logger.info(f"Query '{name}' (run: {run_id}) → {len(results[name])} rows")
        except Exception as e:
            logger.warning(f"Query '{name}' failed: {e}")
            results[name] = pd.DataFrame()

    return results


def print_analytics(results: dict) -> None:
    """Pretty-print analytics results to console."""
    for name, df in results.items():
        print(f"\n{'='*60}")
        print(f"  {name.replace('_', ' ').upper()}")
        print("=" * 60)
        if not df.empty:
            print(df.to_string(index=False))
        else:
            print("  [No data returned]")


# ──────────────────────────────────────────────────────────────────────────────
# 5. PIPELINE EXECUTION
# ──────────────────────────────────────────────────────────────────────────────

def run_sql_pipeline(df_predicted: pd.DataFrame) -> dict:
    """Store dataset with predictions into SQLite and execute analytics pipeline."""
    ensure_dirs()
    db_path, run_id = store_predictions_to_sqlite(df_predicted)
    results = run_analytics(db_path=db_path, run_id=run_id)
    print_analytics(results)
    return results


if __name__ == "__main__":
    from src.preprocessing import run_preprocessing_pipeline
    from src.predict import predict_batch, load_model
    
    _, _, _, _, _, _, df_clean = run_preprocessing_pipeline()
    model = load_model()
    df_scored = predict_batch(df_clean, model)
    run_sql_pipeline(df_scored)
