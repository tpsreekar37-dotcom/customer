# Business Analytics System: AI-Driven Customer Churn Prediction

> **A production-grade, end-to-end Machine Learning System** to predict customer churn, calculate business revenue exposure (MRR/ARR at risk), simulate retention campaign ROI, and generate AI strategic insights via Gemini AI.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3-orange?logo=scikitlearn)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red?logo=streamlit)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-Google_DeepMind-purple)

---

## 📌 Business Overview & Features

In subscription and telecom businesses, **acquiring a new customer costs 5–7× more than retaining an existing one**. Customer churn directly erodes recurring revenue and enterprise valuation.

### Key Capabilities Built:

1. **🚀 Batch Dataset Upload & ML Prediction Engine**:
   - Upload any custom CSV or Excel dataset (`test.csv`, `dataset.xlsx`).
   - Automated target and feature column detection.
   - Computes instant ML predictions, individual churn probability percentages, and risk tiers (High / Medium / Low).
   - Generates separated 10% binned churn probability distribution bar charts with border outlines and gap spacing.

2. **💼 Business Revenue & Risk Telemetry System**:
   - **Monthly Revenue at Risk (MRR)** and **Annualized Revenue Exposure (ARR)** calculations (`MRR × 12`).
   - Average Revenue Per User (ARPU) comparison between churners and active customers.
   - Interactive **Retention Campaign ROI Simulator**: Adjust contract upgrade discount percentages (e.g., 15%) and target acceptance rates (e.g., 45%) to project net recovered ARR and campaign ROI!

3. **🧠 Advanced Gemini AI Churn Evaluation**:
   - Integrated Google Gemini AI API to evaluate dataset characteristics and ML prediction scores.
   - Generates detailed, multi-paragraph strategic executive summaries and answers custom business questions.

4. **📄 Professional Executive Summary Generator**:
   - Automated 6-7 line narrative summary explaining key root causes driving defection (Month-to-month contracts, lack of tech support, fiber optic friction).

---

## ⚙️ Quick Start Guide

### Running the Dashboard:

```cmd
cd C:\Users\tpvij\Desktop\Customer_Churn_Prediction_System
streamlit run dashboard/app.py
```

Open your browser at: **`http://localhost:8501`**

---

## 📁 Project Structure

```
Customer_Churn_Prediction_System/
│
├── data/
│   ├── raw/                    ← Raw dataset
│   └── processed/              ← Cleaned & processed data
│
├── dashboard/
│   └── app.py                  ← Upgraded Streamlit Enterprise Dashboard
│
├── src/
│   ├── predict.py              ← Model inference engine
│   ├── generic_pipeline.py     ← Dynamic ML pipeline for uploaded datasets
│   ├── train_model.py          ← Random Forest & XGBoost trainers
│   ├── preprocessing.py        ← Data cleaning & encoding
│   └── utils.py                ← Project constants & utilities
│
├── models/
│   ├── best_model.pkl          ← Trained production model
│   ├── scaler.pkl              ← Scaler transform
│   └── feature_config.json     ← Saved feature configuration
│
├── test.csv                    ← Sample test dataset for quick upload
├── requirements.txt            ← Project dependencies
└── README.md                   ← Documentation
```

---

## ⚡ How to Test with Uploaded Dataset

1. Launch the app (`http://localhost:8501`).
2. In the **Upload & Predict** tab, upload `test.csv` (located on Desktop or project root).
3. Click **"Predict Churn on Uploaded Dataset"**.
4. View predicted risk scores, probability distributions, data table, and download results as CSV.
5. Switch to **Business Revenue & Risk Telemetry** to model financial exposure and simulate retention offer ROIs!

---

## 📝 License

MIT License — Built for professional enterprise demonstration.
