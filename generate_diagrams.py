import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('reports/figures', exist_ok=True)

# 1. ARCHITECTURE DIAGRAM
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.axis('off')

def draw_box(ax, x, y, w, h, title, subtitle, color, text_color='white'):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.05",
                                 linewidth=1.5, edgecolor='#1E3A8A', facecolor=color)
    ax.add_patch(box)
    ax.text(x + w/2, y + h*0.65, title, ha='center', va='center', fontsize=11, fontweight='bold', color=text_color)
    ax.text(x + w/2, y + h*0.3, subtitle, ha='center', va='center', fontsize=8.5, color=text_color)

# Boxes
draw_box(ax, 0.05, 0.65, 0.22, 0.25, "1. Data Ingestion", "IBM Telco Dataset\n(7,043 Records, 21 Features)", "#1E40AF")
draw_box(ax, 0.38, 0.65, 0.24, 0.25, "2. Preprocessing & FE", "Missing Value Clean\nEncoding & Outliers\nSMOTE Resampling", "#2563EB")
draw_box(ax, 0.73, 0.65, 0.22, 0.25, "3. ML Model Engine", "Logistic Regression\nRandom Forest (Best)\nXGBoost Classifier", "#1D4ED8")

draw_box(ax, 0.15, 0.15, 0.30, 0.25, "4. SQL Analytics Database", "SQLite (churn.db)\nCohort & Risk Queries\nCustomer Segments", "#047857")
draw_box(ax, 0.55, 0.15, 0.30, 0.25, "5. Interactive Dashboard", "Streamlit Web UI\nLive Churn Predictor\nExecutive BI Reports", "#B91C1C")

# Arrows
def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(facecolor='#1E293B', edgecolor='#1E293B', width=2, headwidth=8))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.03, label, ha='center', fontsize=8.5, fontweight='bold', color='#1E293B')

draw_arrow(ax, 0.27, 0.775, 0.38, 0.775, "Raw CSV")
draw_arrow(ax, 0.62, 0.775, 0.73, 0.775, "Features & SMOTE")
draw_arrow(ax, 0.50, 0.65, 0.30, 0.40, "Processed Data")
draw_arrow(ax, 0.84, 0.65, 0.70, 0.40, "Trained Model")
draw_arrow(ax, 0.45, 0.275, 0.55, 0.275, "SQL Insights")

plt.title("System Architecture: End-to-End Customer Churn Prediction & BI System", fontsize=14, fontweight='bold', pad=15, color='#0F172A')
plt.tight_layout()
plt.savefig('reports/figures/system_architecture_diagram.png', bbox_inches='tight')
plt.close()

# 2. ER DIAGRAM
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.axis('off')

# Entity 1: CUSTOMER
draw_box(ax, 0.05, 0.55, 0.25, 0.38, "CUSTOMER", "PK: customer_id\ngender, SeniorCitizen\nPartner, Dependents\ntenure", "#1E3A8A")

# Entity 2: SERVICES
draw_box(ax, 0.38, 0.55, 0.25, 0.38, "SERVICES", "PK: service_id\nFK: customer_id\nPhoneService, MultipleLines\nInternetService, OnlineSecurity\nTechSupport, Streaming", "#0D9488")

# Entity 3: BILLING & CONTRACT
draw_box(ax, 0.70, 0.55, 0.25, 0.38, "BILLING & CONTRACT", "PK: billing_id\nFK: customer_id\nContract, PaperlessBilling\nPaymentMethod\nMonthlyCharges, TotalCharges", "#D97706")

# Entity 4: CHURN PREDICTION
draw_box(ax, 0.38, 0.05, 0.25, 0.38, "CHURN_PREDICTION", "PK: prediction_id\nFK: customer_id\nChurn_Actual, Churn_Prob\nRisk_Score, Prediction_Date\nModel_Used", "#DC2626")

# Connectors
draw_arrow(ax, 0.30, 0.74, 0.38, 0.74, "1 : 1")
draw_arrow(ax, 0.63, 0.74, 0.70, 0.74, "1 : 1")
draw_arrow(ax, 0.175, 0.55, 0.38, 0.24, "1 : N")
draw_arrow(ax, 0.825, 0.55, 0.63, 0.24, "1 : 1")

plt.title("Entity-Relationship (ER) Diagram: Telecom Churn Analytics Schema", fontsize=14, fontweight='bold', pad=15, color='#0F172A')
plt.tight_layout()
plt.savefig('reports/figures/er_diagram.png', bbox_inches='tight')
plt.close()

# 3. DFD LEVEL 0 & LEVEL 1
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
ax1.axis('off')
ax2.axis('off')

# DFD Level 0 (Context Level)
ax1.set_title("DFD Level 0 (Context Diagram)", fontsize=12, fontweight='bold', color='#0F172A')
draw_box(ax1, 0.05, 0.38, 0.25, 0.25, "User / Analyst", "Input Data / Queries", "#334155")
draw_box(ax1, 0.38, 0.32, 0.26, 0.38, "0.0\nCustomer Churn\nPrediction System", "End-to-End Processing\n& BI Inference", "#2563EB")
draw_box(ax1, 0.72, 0.38, 0.25, 0.25, "Management / CRM", "Retention Actions\n& Risk Alerts", "#059669")

draw_arrow(ax1, 0.30, 0.55, 0.38, 0.55, "Customer Data")
draw_arrow(ax1, 0.38, 0.45, 0.30, 0.45, "Results / Plots")
draw_arrow(ax1, 0.64, 0.51, 0.72, 0.51, "Risk Report")

# DFD Level 1
ax2.set_title("DFD Level 1 (Functional Decomposition)", fontsize=12, fontweight='bold', color='#0F172A')
draw_box(ax2, 0.05, 0.70, 0.26, 0.22, "1.0 Preprocessing", "Clean, Encode & Scale", "#1E40AF")
draw_box(ax2, 0.55, 0.70, 0.26, 0.22, "2.0 Feature Engine", "SMOTE & Risk Scores", "#2563EB")
draw_box(ax2, 0.05, 0.15, 0.26, 0.22, "3.0 Model Training", "RF, XGB, Evaluation", "#D97706")
draw_box(ax2, 0.55, 0.15, 0.26, 0.22, "4.0 BI Dashboard", "SQL Analytics & Alerts", "#059669")

draw_arrow(ax2, 0.31, 0.81, 0.55, 0.81, "Clean Data")
draw_arrow(ax2, 0.68, 0.70, 0.18, 0.37, "Balanced Set")
draw_arrow(ax2, 0.31, 0.26, 0.55, 0.26, "Trained Model")

plt.tight_layout()
plt.savefig('reports/figures/dfd_diagram.png', bbox_inches='tight')
plt.close()

# 4. UML USE CASE & CLASS DIAGRAM
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
ax1.axis('off')
ax2.axis('off')

# Use Case Diagram
ax1.set_title("UML Use Case Diagram", fontsize=12, fontweight='bold', color='#0F172A')
draw_box(ax1, 0.02, 0.35, 0.22, 0.32, "Actor\n(Telecom Analyst /\nRetention Manager)", "Interacts with System", "#475569")
draw_box(ax1, 0.40, 0.72, 0.45, 0.20, "UC1: Upload & Preprocess Data", "Clean, encode & validate dataset", "#1E3A8A")
draw_box(ax1, 0.40, 0.48, 0.45, 0.20, "UC2: Train & Evaluate ML Models", "RF, XGBoost, LR with SMOTE", "#2563EB")
draw_box(ax1, 0.40, 0.24, 0.45, 0.20, "UC3: Predict Individual Churn", "Real-time probability & risk score", "#D97706")
draw_box(ax1, 0.40, 0.01, 0.45, 0.20, "UC4: Query SQL Cohort BI", "Filter high-risk customer segments", "#059669")

draw_arrow(ax1, 0.24, 0.55, 0.40, 0.82)
draw_arrow(ax1, 0.24, 0.52, 0.40, 0.58)
draw_arrow(ax1, 0.24, 0.48, 0.40, 0.34)
draw_arrow(ax1, 0.24, 0.45, 0.40, 0.11)

# Class Diagram
ax2.set_title("UML Class Diagram", fontsize=12, fontweight='bold', color='#0F172A')
draw_box(ax2, 0.05, 0.55, 0.40, 0.38, "DataLoader & Preprocessor", "+ load_data(): DataFrame\n+ clean_data(): DataFrame\n+ encode_features(): DataFrame\n+ scale_data(): tuple", "#1E3A8A")
draw_box(ax2, 0.55, 0.55, 0.40, 0.38, "ChurnModelTrainer", "+ apply_smote(): tuple\n+ train_random_forest(): Model\n+ train_xgboost(): Model\n+ evaluate_model(): dict", "#2563EB")
draw_box(ax2, 0.05, 0.05, 0.40, 0.38, "SQLAnalyticsEngine", "+ create_database(): void\n+ execute_cohort_query(): Table\n+ get_revenue_at_risk(): float", "#0D9488")
draw_box(ax2, 0.55, 0.05, 0.40, 0.38, "DashboardApp", "+ render_overview(): void\n+ render_predictor(): void\n+ render_sql_studio(): void\n+ export_report(): File", "#D97706")

draw_arrow(ax2, 0.45, 0.74, 0.55, 0.74)
draw_arrow(ax2, 0.25, 0.55, 0.25, 0.43)
draw_arrow(ax2, 0.75, 0.55, 0.75, 0.43)

plt.tight_layout()
plt.savefig('reports/figures/uml_diagram.png', bbox_inches='tight')
plt.close()

print("All diagrams generated successfully in reports/figures/")
