# 📘 Business Analytics System: AI-Driven Customer Churn Prediction - User Manual

Welcome to the **Business Analytics System: AI-Driven Customer Churn Prediction** platform.

---

## 💻 1. System Requirements & Prerequisites

To run this application on any computer (Windows, macOS, or Linux), ensure you have:

* **Python**: Version 3.9, 3.10, 3.11, or 3.12 installed. (Download from [python.org](https://www.python.org/downloads/))
* **Pip**: Python package installer (included automatically with standard Python installation).
* **RAM / Memory**: 4 GB minimum (8 GB recommended).
* **Web Browser**: Any modern browser (Google Chrome, Microsoft Edge, Mozilla Firefox, Safari, Brave).

---

## 📦 2. Required Libraries & Dependencies

All required Python libraries are listed in `requirements.txt`:

* **`streamlit`** (v1.29+) — Web Application UI Framework
* **`pandas`** & **`numpy`** — Data Manipulation & Analytics
* **`scikit-learn`** (v1.3+) — Machine Learning Models & Scalers
* **`xgboost`** (v2.0+) — Extreme Gradient Boosting Classifier
* **`imbalanced-learn`** — SMOTE Class Balancing
* **`plotly`** — Interactive Data Visualization & Line/Bar Charts
* **`openpyxl`** — Excel file reading (`.xlsx`, `.xls`)
* **`joblib`** — Model saving and loading

---

## 🚀 3. Step-by-Step Installation & Launch Guide

### **Step 1: Extract the ZIP File**
Extract `Customer_Churn_Prediction_System_Professional.zip` into any folder on your computer.

### **Step 2: Open Terminal / Command Prompt**
Open your Command Prompt (Windows), PowerShell, or Terminal (macOS/Linux) and navigate to the project directory:

```cmd
cd path/to/Customer_Churn_Prediction_System
```

### **Step 3: Install Required Dependencies**
Run the following command to install all necessary packages:

```cmd
pip install -r requirements.txt
```

*(Optional: If you prefer using a Python virtual environment:)*
```cmd
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### **Step 4: Launch the Dashboard**
Start the Streamlit application with the command:

```cmd
streamlit run dashboard/app.py
```

### **Step 5: Access in Web Browser**
The application will automatically launch in your browser. If not, open the URL:
👉 **`http://localhost:8501`**

---

## 📊 4. How to Use the Dashboard Features

The application is organized into 3 tabs:

### **Tab 1: 🚀 Upload & Predict**
1. **Upload Dataset**: Drag & drop or browse any customer dataset in `.csv` or `.xlsx` format (or test using the included `test.csv` file).
2. **Column Selection**: The system auto-detects Target and Customer ID columns. You can adjust them using dropdown selectors.
3. **Run Predictions**: Click **▶ Predict Churn on Uploaded Dataset**.
4. **Results Overview**:
   * Displays Total Customers, Predicted Churners, Churn Rate %, and Total Monthly Revenue at Risk.
   * View the **10% Binned Churn Probability Distribution** chart with distinct borders.
   * View individual customer predictions, risk levels (🔴 High, 🟡 Medium, 🟢 Low), and download predictions as CSV.
   * View the **6-7 line Executive Narrative Summary** analyzing root causes of churn.

---

### **Tab 2: 💼 Business Revenue & Risk Telemetry**
1. **Revenue Exposure**: View live metrics for Monthly Recurring Revenue (MRR) at Risk, Annualized Exposure (ARR), and Average Revenue Per User (ARPU).
2. **Interactive Retention Campaign ROI Simulator**:
   * Adjust sliders for **Offer Discount (%)** and **Target Campaign Acceptance Rate (%)**.
   * Live calculation of **Gross Recovered ARR**, **Campaign Offer Cost**, **Net Recovered ARR**, and **Expected Return on Investment (ROI %)**.

---

### **Tab 3: 🧪 Model Test & Epoch Progression**
1. **Model Accuracy & Confusion Matrix**:
   * Upload test data with ground-truth labels (or test on memory dataset).
   * Calculates overall **Test Accuracy %**, **Precision**, **Recall**, **F1-Score**.
   * Breaks down the **Confusion Matrix**: True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN).
   * Displays a **Side-by-Side Comparison Table** matching Actual vs. Predicted Churn.
2. **Epoch Training Progression**:
   * Adjust sliders for **Epoch Count (10-100)** and **Target Validation Limit %**.
   * Click **▶ Run Epoch Training Simulation** to simulate multi-epoch training convergence.
   * Renders interactive **Epoch vs. Accuracy (%)** and **Epoch vs. Cross-Entropy Loss** convergence curves.

---

## ❓ 5. Troubleshooting & FAQ

* **Q: Port 8501 is already in use?**
  * *Solution*: Run Streamlit on a different port:
    ```cmd
    streamlit run dashboard/app.py --server.port 8502
    ```
* **Q: ModuleNotFoundError when running Streamlit?**
  * *Solution*: Ensure you installed dependencies via `pip install -r requirements.txt` in the same Python environment.
* **Q: Optional Google Gemini AI Integration?**
  * *Solution*: Set your API key in environment variables:
    ```cmd
    set GEMINI_API_KEY=your_actual_api_key
    ```

---

## 📜 Project Authors & License
Built with Python, Scikit-Learn, XGBoost, and Streamlit for enterprise customer churn intelligence and revenue risk analytics.
