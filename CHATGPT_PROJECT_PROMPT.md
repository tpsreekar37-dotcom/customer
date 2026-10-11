# ChatGPT Prompt — Customer Churn Prediction System (Complete Project Context)

> **Copy everything below this line and paste it into ChatGPT as a single message.**
> After pasting, you can ask any how/what/why/when question about the project.

---

You are an expert technical assistant. I am going to give you the complete architecture, codebase logic, algorithms, data pipeline, and decision rationale for my **Customer Churn Prediction System** project. After reading all of this, answer ANY question I ask — whether it is a "how", "what", "why", or "when" question — using the details provided below. If I ask you to explain something to a viva examiner, professor, interviewer, or in a report, use this context as your source of truth. Do NOT make up information beyond what is described here.

---

## 1. PROJECT OVERVIEW

**Project Name:** Customer Churn Prediction System (also called "ChurnGuard AI" / "Business Analytics System")  
**Objective:** Predict which telecom customers will cancel (churn) their subscription using Machine Learning, so the company can take proactive retention actions.  
**Domain:** Telecommunications / SaaS Customer Analytics  
**Language:** Python 3.10+  
**Key Libraries:** pandas, numpy, scikit-learn, XGBoost, imbalanced-learn (SMOTE), matplotlib, seaborn, plotly, streamlit, SQLAlchemy, SQLite, joblib, SHAP  

---

## 2. WHAT IS CUSTOMER CHURN?

Customer churn (also called customer attrition) means a customer stops using a company's product or service. In telecom, this means a subscriber cancels their phone/internet plan. Churn is expensive because acquiring a new customer costs 5–7× more than retaining an existing one. Therefore, predicting churn early lets companies offer targeted discounts, loyalty programs, or improved support to at-risk customers before they leave.

**How do we define churn in this project?**
- A customer is labeled **Churn = 1** if they have cancelled/left the service.
- A customer is labeled **Churn = 0** if they are still active/retained.
- The target column in the original dataset is `"Churn"` with values `"Yes"` or `"No"`, which we convert to 1 and 0 respectively.

---

## 3. DATASET

**Source:** IBM Telco Customer Churn Dataset (publicly available on GitHub/Kaggle)  
**Size:** 7,043 customer records × 21 columns  
**Download URL:** `https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv`  
**Fallback:** If download fails, the system generates a realistic synthetic dataset of 7,043 rows with identical schema and statistical distributions (using numpy random generator with seed 42 for reproducibility).

### 3.1 Dataset Columns and Descriptions

| Column | Type | Description |
|--------|------|-------------|
| `customerID` | String | Unique customer identifier (dropped before training — not predictive) |
| `gender` | Categorical | Male / Female |
| `SeniorCitizen` | Binary (0/1) | Whether the customer is a senior citizen |
| `Partner` | Binary (Yes/No) | Whether the customer has a partner |
| `Dependents` | Binary (Yes/No) | Whether the customer has dependents |
| `tenure` | Numeric | Number of months the customer has been with the company (0–72) |
| `PhoneService` | Binary (Yes/No) | Whether the customer has phone service |
| `MultipleLines` | Categorical | Yes / No / No phone service |
| `InternetService` | Categorical | DSL / Fiber optic / No |
| `OnlineSecurity` | Categorical | Yes / No / No internet service |
| `OnlineBackup` | Categorical | Yes / No / No internet service |
| `DeviceProtection` | Categorical | Yes / No / No internet service |
| `TechSupport` | Categorical | Yes / No / No internet service |
| `StreamingTV` | Categorical | Yes / No / No internet service |
| `StreamingMovies` | Categorical | Yes / No / No internet service |
| `Contract` | Ordinal | Month-to-month (0) / One year (1) / Two year (2) |
| `PaperlessBilling` | Binary (Yes/No) | Whether customer uses paperless billing |
| `PaymentMethod` | Categorical | Electronic check / Mailed check / Bank transfer (automatic) / Credit card (automatic) |
| `MonthlyCharges` | Numeric | Amount charged each month ($18–$120) |
| `TotalCharges` | Numeric | Total amount charged over entire tenure (stored as string in raw data — must be converted) |
| `Churn` | Binary (Yes/No) | **TARGET VARIABLE** — Did the customer churn? |

### 3.2 Key Dataset Statistics
- **Churn rate:** ~26.5% of customers churned (class imbalance exists)
- **Average tenure:** ~32 months
- **Median monthly charges:** ~$70
- **Missing values:** 11 records have blank `TotalCharges` (new customers with tenure = 0)

---

## 4. PROJECT ARCHITECTURE & FILE STRUCTURE

```
churn_predicting/
├── main.py                          # Master orchestration — runs the ENTIRE pipeline end-to-end
├── requirements.txt                 # All Python dependencies
├── dashboard/
│   └── app.py                       # Streamlit web dashboard (3 tabs)
├── src/
│   ├── utils.py                     # Logging, path helpers, plot styling, color palette
│   ├── preprocessing.py             # Data loading, cleaning, encoding, scaling, train/test split
│   ├── feature_engineering.py       # Create derived features + SMOTE class balancing
│   ├── eda.py                       # 9+ EDA visualizations (distribution, correlation, demographics)
│   ├── train_model.py               # Train Random Forest & XGBoost, evaluate, save best model
│   ├── predict.py                   # Single-customer and batch prediction using saved model
│   ├── sql_integration.py           # Store data in SQLite, run 8 business analytics queries
│   └── generic_pipeline.py          # Schema-agnostic pipeline for ANY uploaded CSV/Excel dataset
├── data/
│   ├── raw/                         # Raw downloaded CSV
│   └── processed/                   # Cleaned, encoded, split CSVs (train.csv, test.csv)
├── models/                          # Saved .pkl model files, scaler, encoders, feature config
├── reports/
│   └── figures/                     # All generated charts (PNG)
├── sql/                             # SQL directory
└── notebooks/                       # Jupyter notebooks (optional exploration)
```

---

## 5. COMPLETE DATA PIPELINE (Step-by-Step)

### STEP 1: Data Loading (`preprocessing.py → load_data()`)
- Check if `data/raw/telco_churn_raw.csv` exists on disk.
- If yes: load from cache (fast).
- If no: download from IBM GitHub URL. If download fails, generate synthetic data.
- Returns a raw pandas DataFrame.

### STEP 2: Data Cleaning (`preprocessing.py → clean_data()`)
1. **Drop `customerID`** — it's a unique identifier, not predictive.
2. **Remove duplicate rows** — ensures data integrity.
3. **Fix `TotalCharges`** — The raw dataset stores this as a string. Some entries contain blank spaces (for new customers). We convert to numeric using `pd.to_numeric(errors='coerce')`, then impute NaN values with `tenure × MonthlyCharges`.
4. **Encode target column** — Map `"Yes" → 1`, `"No" → 0`.
5. **Coerce numeric types** — Ensure `tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen` are proper floats.
6. **Impute remaining NaN** — Numeric columns: fill with **median**. Categorical columns: fill with **mode** (most frequent value).

### STEP 3: Outlier Handling (`preprocessing.py → handle_outliers()`)
- Uses **IQR-based Winsorisation** on `MonthlyCharges` and `TotalCharges`.
- Clips values at the 1st and 99th percentiles.
- **Why?** Extreme outliers can distort model training. Winsorisation preserves the data point but caps its influence.

### STEP 4: Feature Encoding (`preprocessing.py → encode_features()`)

| Column Type | Encoding Method |
|-------------|----------------|
| Binary Yes/No (`Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`) | Direct mapping: Yes→1, No→0 |
| Service columns (`MultipleLines`, `OnlineSecurity`, etc.) | "No" / "No internet service" / "No phone service" → 0, "Yes" → 1 |
| `Contract` | Ordinal encoding: Month-to-month→0, One year→1, Two year→2 |
| `gender`, `InternetService`, `PaymentMethod` | **Label Encoding** using sklearn `LabelEncoder` |

- All fitted `LabelEncoder` objects are saved as `models/encoders.pkl` so inference uses the exact same encoding.

### STEP 5: Train/Test Split (`preprocessing.py → split_data()`)
- **80/20 split** (80% training, 20% testing)
- **Stratified** on the target (`Churn`) to preserve the original churn ratio in both splits.
- `random_state=42` for reproducibility.

### STEP 6: Feature Scaling (`preprocessing.py → scale_features()`)
- **StandardScaler** applied to: `tenure`, `MonthlyCharges`, `TotalCharges`
- **Why StandardScaler?** It transforms features to have mean=0 and std=1, which helps distance-based algorithms and speeds up convergence.
- **Important:** Scaler is `.fit_transform()` on training data only, then `.transform()` on test data to prevent data leakage.
- Fitted scaler saved as `models/scaler.pkl`.

### STEP 7: Feature Engineering (`feature_engineering.py → create_features()`)

Five new features are derived:

| Feature | Formula | Why It Matters |
|---------|---------|----------------|
| `ChargesPerTenure` | `MonthlyCharges / (tenure + 1)` | Captures cost intensity relative to loyalty. New customers paying a lot per month of tenure are high risk. |
| `ServiceCount` | Sum of 6 service binary columns (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies) | More services subscribed = more invested = lower churn probability. |
| `IsHighValue` | 1 if `MonthlyCharges >= 75th percentile`, else 0 | Identifies premium-tier customers whose churn would cause disproportionate revenue loss. |
| `HasLoyalty` | 1 if `tenure > 24 months`, else 0 | Customers who stayed 2+ years have demonstrated commitment. |
| `RiskScore` | `0.4 × contract_risk + 0.3 × charges_normalized + 0.3 × tenure_normalized` | A composite score combining contract vulnerability (month-to-month = highest), payment level, and recency. Values range 0–1. |

- **Feature config** (thresholds for IsHighValue, normalization min/max for RiskScore) is saved as `models/feature_config.json` to ensure inference uses the EXACT same thresholds learned from training data.

### STEP 8: Class Imbalance Handling — SMOTE (`feature_engineering.py → apply_smote()`)
- **Problem:** Only ~26.5% of customers churned. The dataset is **imbalanced**. Without correction, the model would simply predict "No Churn" for everyone and still get ~73% accuracy — but it would completely miss actual churners.
- **Solution:** **SMOTE (Synthetic Minority Over-sampling Technique)** generates new synthetic samples of the minority class (churned customers) by interpolating between existing minority samples and their k=5 nearest neighbors.
- Applied **only on training data** (never on test data — that would be data leakage).
- After SMOTE, the training set has 50% churn / 50% non-churn.

### STEP 9: Model Training (`train_model.py → train_all_models()`)

Two models are trained:

#### Model 1: Random Forest Classifier (PRODUCTION MODEL)
```python
RandomForestClassifier(
    n_estimators=200,       # 200 decision trees in the ensemble
    max_depth=10,           # Each tree can be at most 10 levels deep
    random_state=42,        # Reproducibility
    n_jobs=-1,              # Use all CPU cores
    class_weight="balanced" # Adjust weights inversely proportional to class frequency
)
```
**How Random Forest works:**
1. Create 200 decision trees, each trained on a random bootstrap sample of the data.
2. Each tree uses a random subset of features at each split point.
3. For prediction: each tree "votes" for Churn (1) or No Churn (0). The majority vote wins.
4. For probability: the proportion of trees voting "Churn" = churn probability.

**Why Random Forest?**
- Handles non-linear relationships well
- Robust to overfitting due to ensemble averaging
- Provides built-in feature importance rankings
- Works well with both numeric and encoded categorical features
- Handles class imbalance via `class_weight="balanced"`

#### Model 2: XGBoost Classifier (BENCHMARK MODEL)
```python
XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
    scale_pos_weight=3      # Upweights the minority class by 3×
)
```
**How XGBoost works:**
- Gradient Boosting: trains trees sequentially, where each new tree corrects the errors of the previous ensemble.
- Uses second-order gradient information (Hessian) for better optimization.
- Regularization (L1/L2) prevents overfitting.

**Why is Random Forest chosen as the production model instead of XGBoost?**
- Both achieve similar AUC (~83–86%), but Random Forest is:
  - Simpler to interpret (no learning rate tuning)
  - More stable across different datasets
  - Faster inference for real-time dashboard predictions
- XGBoost is kept as a benchmark for transparent comparison.

### STEP 10: Model Evaluation (`train_model.py → evaluate_model()`)

Five metrics are computed:

| Metric | What It Measures | How It's Calculated |
|--------|------------------|---------------------|
| **Accuracy** | Overall correctness | `(TP + TN) / Total` |
| **Precision** | Of those predicted as "Churn", how many actually churned? | `TP / (TP + FP)` |
| **Recall (Sensitivity)** | Of actual churners, how many did we catch? | `TP / (TP + FN)` |
| **F1-Score** | Harmonic mean of Precision and Recall | `2 × (Precision × Recall) / (Precision + Recall)` |
| **ROC-AUC** | Area under the Receiver Operating Characteristic curve. Measures the model's ability to distinguish between classes across all probability thresholds | `sklearn.roc_auc_score(y_true, y_proba)` |

**Verified Evaluation Results (Test Set):**
- **Random Forest (Production Model):** Accuracy **77.44%**, Precision **55.84%**, Recall **70.70%** (70.43% CV), F1-Score **62.40%**, **ROC-AUC: 83.81%** (83.62% CV)
- **XGBoost (Benchmark Model):** Accuracy **73.59%**, Precision **50.09%**, Recall **76.08%**, F1-Score **60.41%**, **ROC-AUC: 82.09%**
- **5-Fold Cross-Validation ROC-AUC:** **83.62% ± 0.8%**

### STEP 11: Artifact Persistence
After training, these files are saved to `models/`:
- `best_model.pkl` — The fitted Random Forest model
- `random_forest.pkl`, `xgboost.pkl` — Individual model files
- `scaler.pkl` — Fitted StandardScaler
- `encoders.pkl` — Fitted LabelEncoders
- `feature_config.json` — Thresholds (MonthlyCharges percentile, tenure min/max)
- `best_model_name.txt` — Contains "Random Forest"
- `model_results.json` — All evaluation metrics for all models
- `feature_importance.csv` — Top features ranked by importance

---

## 6. HOW DO WE DECIDE IF A CUSTOMER WILL CHURN?

### 6.1 The Decision Process (Inference Pipeline)

When a new customer's data comes in (either single customer or batch upload):

1. **Preprocess** the raw data using the SAME transformations as training:
   - Encode binary columns (Yes/No → 1/0)
   - Encode service columns (No/No internet service → 0, Yes → 1)
   - Ordinal-encode Contract type
   - Label-encode gender, InternetService, PaymentMethod using the saved `encoders.pkl`
   - Compute derived features (ChargesPerTenure, ServiceCount, IsHighValue, HasLoyalty, RiskScore) using saved `feature_config.json` thresholds
   - Scale `tenure`, `MonthlyCharges`, `TotalCharges` using saved `scaler.pkl`

2. **Predict** using the loaded Random Forest model:
   - `model.predict(X)` → binary output: 0 (No Churn) or 1 (Churn)
   - `model.predict_proba(X)[:, 1]` → probability between 0.0 and 1.0

3. **Classify Risk Level** based on churn probability:
   - Probability ≥ 0.65 → 🔴 **High Risk** ("Will almost certainly churn")
   - Probability ≥ 0.40 → 🟡 **Medium Risk** ("At risk, needs attention")
   - Probability < 0.40 → 🟢 **Low Risk** ("Likely to stay")

### 6.2 What Features Matter Most? (Feature Importance)

The Random Forest model ranks features by **Gini Importance** (how much each feature reduces impurity across all trees). Top predictors:

1. **tenure** — #1 most important. Short tenure = high churn risk.
2. **MonthlyCharges** — Higher charges correlate with higher churn.
3. **TotalCharges** — Reflects both tenure and spending.
4. **Contract** — Month-to-month contracts have dramatically higher churn (~42%) than two-year contracts (~3%).
5. **InternetService** — Fiber optic customers churn more (possibly due to higher costs).
6. **RiskScore** — The composite engineered feature.
7. **OnlineSecurity / TechSupport** — Customers WITHOUT these services churn more.
8. **PaymentMethod** — Electronic check users churn significantly more.

### 6.3 Real-World Interpretation

A customer is predicted to churn when they exhibit combinations of:
- **Short tenure** (0–12 months)
- **Month-to-month contract** (no commitment)
- **High monthly charges** ($70+) without bundled services
- **Electronic check payment** (less friction to cancel)
- **No OnlineSecurity, TechSupport, DeviceProtection** (low investment in extras)
- **Fiber optic internet** (expensive, competitive market)
- **Paperless billing** (digital-first customers who compare options online)

---

## 7. THE DASHBOARD (Streamlit Web Interface)

**File:** `dashboard/app.py`  
**Launch:** `streamlit run dashboard/app.py`  
**Design:** Dark theme (#0B0F19 background), professional enterprise design with gradient buttons, glassmorphism cards

### Tab 1: Upload & Predict
- Upload any CSV/Excel customer dataset
- System auto-detects target column (Churn/target/outcome) and ID column
- Runs the **generic pipeline** (schema-agnostic — works on ANY tabular customer dataset, not just telecom)
- Shows: Predicted churn rate, high-risk count, risk pie chart, probability histogram
- Generates an **Executive Risk Summary** narrative
- Download predictions as CSV

### Tab 2: Business Revenue & Risk Telemetry
- Computes **MRR (Monthly Recurring Revenue) at Risk** = sum of MonthlyCharges for predicted churners
- Computes **ARR (Annualized Revenue at Risk)** = MRR × 12
- Shows revenue breakdown by Contract type and Internet service type
- Generates a **Financial Impact Narrative**

### Tab 3: Model Test
- Upload a ground-truth test dataset (with actual churn labels)
- System trains on the data, predicts, then compares predictions vs. actual
- Shows: Accuracy, Precision, Recall, F1-Score, Confusion Matrix (TP/TN/FP/FN)
- Side-by-side table: Actual vs. Predicted with ✅/❌ match indicators
- **Epoch Training Simulation**: Visualizes how model accuracy improves over 10–100 training iterations with live convergence curves

---

## 8. THE GENERIC PIPELINE (Schema-Agnostic — Any Dataset)

**File:** `src/generic_pipeline.py`  
This is the pipeline used by the dashboard for uploaded datasets. It works on ANY tabular dataset:

1. **Auto-detect column types**: Examines each column — numeric, categorical (≤50 unique values), binary (2 values), date, or drop (ID/high-cardinality)
2. **Target normalization**: Converts any binary target to 0/1 (handles Yes/No, True/False, Churned/Active, 1.0/0.0, etc.)
3. **Date columns** → converted to "days since earliest date" (numeric feature)
4. **Missing value imputation**: Numeric → median, Categorical → mode
5. **Encoding**: Binary → 0/1, Multi-category → LabelEncoder
6. **Scaling**: StandardScaler on all numeric columns
7. **SMOTE**: Applied if class imbalance exists (churn rate <35% or >65%)
8. **Training**: Random Forest (production) + XGBoost (benchmark)
9. **Batch prediction**: Applies same transformations, handles inf/NaN robustly

---

## 9. SQL INTEGRATION

**File:** `src/sql_integration.py`  
**Database:** SQLite (`data/churn.db`)

The processed dataset is stored in a `customers` table. Eight business analytics SQL queries are executed:

1. **Churn Summary** — total churned, retained, churn rate %
2. **Churn by Contract** — churn rate per contract type
3. **Churn by Payment Method** — churn rate per payment method
4. **Revenue by Segment** — avg/total revenue for churned vs. retained
5. **Top Churn Segments** — Contract × InternetService combinations with highest churn
6. **Tenure Cohort Analysis** — churn rate by tenure bucket (0–12, 13–24, 25–48, 49+)
7. **Revenue at Risk** — total monthly revenue from churned customers
8. **High Risk Customers** — top 20 churned customers with above-average spending

---

## 10. EDA (Exploratory Data Analysis)

**File:** `src/eda.py`  
Generates 9 professional dark-themed visualizations:

1. Churn Distribution (pie + bar chart)
2. Tenure Analysis (histogram + boxplot by churn)
3. Contract Type Analysis (churn rate + customer count)
4. Monthly Charges Analysis (KDE density + violin plot)
5. Feature Correlation Heatmap
6. Churn by Demographics (gender, senior citizen, partner, dependents)
7. Internet Service & Payment Method churn rates
8. Monthly Charges vs. Tenure scatter plot (colored by churn)
9. Churn by Total Charges quartile

---

## 11. BUGS FOUND AND FIXED

1. **`IntCastingNaNError`** — `TotalCharges` column contained blank strings. Fix: `pd.to_numeric(errors='coerce')` + impute with `tenure × MonthlyCharges`.
2. **`ValueError: invalid error value`** — Used `pd.to_numeric(errors='ignore')` which is not a valid argument. Fix: changed to `errors='coerce'`.
3. **`StandardScaler` crash on `inf` values** — Some feature columns contained `inf` or `-inf` from division operations. Fix: globally replace `inf`/`-inf` with `NaN` and impute before scaling.
4. **Target column normalization** — The `normalize_target()` function now handles: NaN, inf, string-based Yes/No, numeric 0/1, float 0.0/1.0, and other common churn labels like "Exited", "Left", "Cancelled", "Inactive".

---

## 12. HOW TO RUN THE PROJECT

```bash
# Step 1: Navigate to project folder
cd churn_predicting

# Step 2: Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run the full training pipeline
python main.py
# This downloads data, preprocesses, trains models, generates EDA charts,
# stores in SQLite, saves models. Takes ~30 seconds.

# Step 5: Launch the dashboard
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

---

## 13. KEY TECHNICAL DECISIONS AND RATIONALE

| Decision | Why |
|----------|-----|
| Random Forest over XGBoost as production model | Simpler, more interpretable, similar performance, faster inference |
| SMOTE over random oversampling | Generates realistic synthetic samples instead of duplicating existing ones |
| StandardScaler over MinMaxScaler | Better for tree-based models and handles outliers more gracefully |
| 80/20 stratified split | Preserves class distribution; 20% is sufficient for reliable evaluation |
| Saving encoders/scaler/config | Ensures inference uses EXACTLY the same transformations as training (no training-serving skew) |
| Generic pipeline for dashboard | Allows users to upload ANY customer dataset, not just telecom |
| SQLite for analytics | Lightweight, zero-config, runs anywhere, perfect for portfolio projects |
| Composite RiskScore feature | Combines multiple signals into one interpretable score for business stakeholders |

---

## 14. QUICK REFERENCE — IMPORTANT NUMBERS

- Dataset size: **7,043 customers × 21 columns**
- Features after engineering: **~24 features**
- Churn rate: **~26.5%**
- Train/Test split: **80% / 20% (stratified)**
- Best model: **Random Forest**
- ROC-AUC: **83.81% (Test) / 83.62% (Cross-Validation)**
- Churn Recall: **70.70% (Test) / 70.43% (Cross-Validation)**
- Precision: **55.84%**
- Accuracy: **77.44%**
- F1-Score: **62.40%**
- Cross-validation AUC: **83.62% ± 0.008**
- Number of trees: **200**
- Max tree depth: **10**
- SMOTE k-neighbors: **5**
- Risk thresholds: High ≥ 65%, Medium ≥ 40%, Low < 40%

---

**You now have full context about the project. Ask me anything!**
