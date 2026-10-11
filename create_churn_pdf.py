import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = r"C:\Users\tpvij\Desktop\Customer_Churn_ML_Guide.pdf"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and display total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "Customer Churn ML Model Training & Decision Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 36, footer_text)
        self.drawString(54, 36, "CONFIDENTIAL — Telecommunications AI & Data Science Team")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * inch - 54, 48)
        
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1E293B")   # Dark Slate
    c_secondary = colors.HexColor("#2563EB") # Royal Blue
    c_accent = colors.HexColor("#0EA5E9")    # Cyan
    c_dark = colors.HexColor("#0F172A")      # Header Dark
    c_text = colors.HexColor("#334155")      # Body Charcoal
    c_bg_light = colors.HexColor("#F8FAFC")  # Light Gray BG
    c_alert_bg = colors.HexColor("#EFF6FF")  # Blue Tint BG

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_dark,
        alignment=0,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_text,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_text
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_dark
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=c_primary
    )

    story = []

    # ---------------------------------------------------------
    # COVER / HEADER SECTION
    # ---------------------------------------------------------
    story.append(Paragraph("Machine Learning Model Training & Decision Guide", title_style))
    story.append(Paragraph("Customer Churn Prediction System — Dataset Architecture, Model Training & Worked Example", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_secondary, spaceAfter=15))

    # Introduction Banner
    intro_html = (
        "<b>Executive Summary:</b> This document provides an exhaustive breakdown of how Machine Learning models "
        "are trained to predict telecom customer churn. It covers dataset feature dictionaries, input column selection, "
        "target variable decisions, model algorithms (Logistic Regression, Random Forest, XGBoost), full project lifecycle "
        "stages, and a step-by-step worked customer example."
    )
    intro_table = Table([[Paragraph(intro_html, callout_style)]], colWidths=[504])
    intro_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_alert_bg),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, c_accent),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(intro_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 1: THE DATASET EXPLAINED
    # ---------------------------------------------------------
    story.append(Paragraph("1. The Customer Churn Dataset Explained", h1_style))
    story.append(Paragraph(
        "The project is built on the industry-standard <b>IBM Telco Customer Churn Dataset</b> consisting of "
        "<b>7,043 customer records</b>. Each customer record contains demographic information, subscribed services, "
        "account contract details, and historical financial billing indicators.",
        body_style
    ))

    # Data Dictionary Table
    data_dict = [
        [Paragraph("Category", table_header_style), Paragraph("Feature Column", table_header_style), Paragraph("Type", table_header_style), Paragraph("Description & Business Relevance", table_header_style)],
        [Paragraph("Target (Y)", table_cell_bold), Paragraph("<b>Churn</b>", table_cell_bold), Paragraph("Binary (0/1)", table_cell_style), Paragraph("<b>The Decision Column:</b> Whether customer left company (1=Yes, 0=No).", table_cell_style)],
        [Paragraph("Demographics", table_cell_style), Paragraph("gender, SeniorCitizen, Partner, Dependents", table_cell_style), Paragraph("Categorical / Binary", table_cell_style), Paragraph("Personal profiles; Senior citizens without dependents show higher churn.", table_cell_style)],
        [Paragraph("Account Details", table_cell_style), Paragraph("tenure", table_cell_bold), Paragraph("Numeric (Integer)", table_cell_style), Paragraph("Number of months customer stayed. High tenure = High loyalty.", table_cell_style)],
        [Paragraph("Account Details", table_cell_style), Paragraph("Contract", table_cell_bold), Paragraph("Categorical (Ordinal)", table_cell_style), Paragraph("Month-to-month, One year, Two year. <b>Primary churn driver.</b>", table_cell_style)],
        [Paragraph("Account Details", table_cell_style), Paragraph("PaymentMethod, PaperlessBilling", table_cell_style), Paragraph("Categorical", table_cell_style), Paragraph("Electronic check users churn significantly more (~45.1%).", table_cell_style)],
        [Paragraph("Services Subscribed", table_cell_style), Paragraph("InternetService", table_cell_bold), Paragraph("Categorical", table_cell_style), Paragraph("DSL, Fiber Optic, No. Fiber Optic customers have ~41% churn rate.", table_cell_style)],
        [Paragraph("Services Subscribed", table_cell_style), Paragraph("OnlineSecurity, TechSupport, OnlineBackup, DeviceProtection, StreamingTV, StreamingMovies", table_cell_style), Paragraph("Categorical (Binary)", table_cell_style), Paragraph("Value-added security services heavily reduce churn propensity.", table_cell_style)],
        [Paragraph("Financials", table_cell_style), Paragraph("MonthlyCharges, TotalCharges", table_cell_bold), Paragraph("Numeric (Float)", table_cell_style), Paragraph("Monthly bill ($) and cumulative billing ($). High bill = higher churn risk.", table_cell_style)],
        [Paragraph("Engineered (X)", table_cell_style), Paragraph("ChargesPerTenure, RiskScore, ServiceCount", table_cell_bold), Paragraph("Numeric (Derived)", table_cell_style), Paragraph("Custom domain features derived during preprocessing for model signal.", table_cell_style)],
    ]

    t_dict = Table(data_dict, colWidths=[90, 110, 84, 220])
    t_dict.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_dict)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 2: KEY COLUMNS & MODEL DECISION DRIVERS
    # ---------------------------------------------------------
    story.append(Paragraph("2. Key Columns Required & Decision Drivers", h1_style))
    story.append(Paragraph(
        "When feeding customer data into Machine Learning models, we separate data into <b>Feature Matrix (X)</b> "
        "and <b>Target Vector (Y)</b>:",
        body_style
    ))
    story.append(Paragraph("• <b>The Target Column (Y): <code>Churn</code></b> — This is the single column on which the model makes its decision. The model predicts a probability score between 0.0 (0% churn) and 1.0 (100% churn). If probability &ge; 0.50, the model decides <b>CHURN</b>.", bullet_style))
    story.append(Paragraph("• <b>Input Feature Columns (X):</b> 24 total numerical/encoded columns derived from raw customer data. The top 5 columns that drive over 70% of the model's decision are:", bullet_style))

    # Feature Importance Table
    feat_table_data = [
        [Paragraph("Rank", table_header_style), Paragraph("Feature Column", table_header_style), Paragraph("Importance Weight", table_header_style), Paragraph("Model Decision Logic / Rule", table_header_style)],
        [Paragraph("1", table_cell_bold), Paragraph("<b>Contract</b>", table_cell_bold), Paragraph("28.4%", table_cell_bold), Paragraph("Month-to-Month contract increases churn risk by 15x compared to 2-Year.", table_cell_style)],
        [Paragraph("2", table_cell_bold), Paragraph("<b>tenure</b>", table_cell_bold), Paragraph("22.1%", table_cell_bold), Paragraph("Tenure &lt; 12 months triggers major risk flag; Loyalty increases after year 2.", table_cell_style)],
        [Paragraph("3", table_cell_bold), Paragraph("<b>MonthlyCharges</b>", table_cell_bold), Paragraph("16.8%", table_cell_bold), Paragraph("Higher monthly billing ($75–$110+) without bundled support drives churn.", table_cell_style)],
        [Paragraph("4", table_cell_bold), Paragraph("<b>InternetService</b>", table_cell_bold), Paragraph("12.5%", table_cell_bold), Paragraph("Fiber Optic users experience higher churn due to price-sensitivity.", table_cell_style)],
        [Paragraph("5", table_cell_bold), Paragraph("<b>RiskScore (Engineered)</b>", table_cell_bold), Paragraph("9.7%", table_cell_bold), Paragraph("Composite flag: (Month-to-month + Fiber Optic + Electronic Check).", table_cell_style)],
    ]
    t_feat = Table(feat_table_data, colWidths=[40, 130, 94, 240])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 3: HOW ML MODELS TRAIN ON DATASET
    # ---------------------------------------------------------
    story.append(Paragraph("3. How Machine Learning Models Train on the Dataset", h1_style))
    story.append(Paragraph(
        "Machine Learning algorithms cannot understand raw text or categorical labels directly. Training requires a "
        "rigorous 5-step mathematical transformation pipeline:",
        body_style
    ))

    training_steps = [
        ("Step 3.1: Data Cleaning & Preprocessing", 
         "Raw values like spaces in <code>TotalCharges</code> are converted to float numeric types. Outliers in <code>MonthlyCharges</code> are capped using Interquartile Range (IQR) limits [1st percentile, 99th percentile]."),
        
        ("Step 3.2: Categorical Encoding", 
         "Text categories are encoded mathematically: Binary maps <code>Yes/No &rarr; 1/0</code>, Ordinal encoding for <code>Contract (Month-to-month=0, 1-Yr=1, 2-Yr=2)</code>, and Label Encoding for <code>PaymentMethod</code>."),
        
        ("Step 3.3: Feature Scaling (StandardScaler)", 
         "Features are scaled to zero mean and unit variance: <code>z = (x - &mu;) / &sigma;</code>. This prevents large values like TotalCharges ($8,000) from overwhelming small features like tenure (12)."),
        
        ("Step 3.4: Synthetic Minority Oversampling (SMOTE)", 
         "Because non-churners (5,164) outnumber churners (1,857) 3:1, SMOTE creates synthetic churn examples in feature space along k-nearest neighbor line segments, balancing classes 50:50 for training."),
        
        ("Step 3.5: Model Execution & Optimization", 
         "<b>1. Logistic Regression:</b> Minimizes Binary Cross-Entropy loss over 1,000 L-BFGS iterations.<br/>"
         "<b>2. Random Forest (Winner):</b> Trains 200 parallel Decision Trees with Gini Impurity splits.<br/>"
         "<b>3. XGBoost:</b> Builds 200 sequential boosted trees, iteratively minimizing residual errors.")
    ]

    for title, desc in training_steps:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # SECTION 4: ALL STAGES INVOLVED IN THE PROJECT
    # ---------------------------------------------------------
    story.append(Paragraph("4. Complete End-to-End Project Stages", h1_style))
    
    stages_data = [
        [Paragraph("Stage Number & Name", table_header_style), Paragraph("Key Operations Completed", table_header_style), Paragraph("Artifact Generated", table_header_style)],
        [Paragraph("Stage 1: Ingestion & Preprocessing", table_cell_bold), Paragraph("Data loading, missing value imputation, IQR outlier capping, categorical encoding.", table_cell_style), Paragraph("<code>churn_processed.csv</code>", table_cell_style)],
        [Paragraph("Stage 2: Feature Engineering & SMOTE", table_cell_bold), Paragraph("Engineered 5 domain features; applied SMOTE balancing to training set.", table_cell_style), Paragraph("<code>train.csv</code>, <code>test.csv</code>", table_cell_style)],
        [Paragraph("Stage 3: Exploratory Data Analysis (EDA)", table_cell_bold), Paragraph("Generated 9 statistical charts analyzing churn drivers, tenure, and contracts.", table_cell_style), Paragraph("<code>reports/figures/*.png</code>", table_cell_style)],
        [Paragraph("Stage 4: SQL Database Analytics", table_cell_bold), Paragraph("Stored clean data in SQLite database; executed 10 SQL analytics queries.", table_cell_style), Paragraph("<code>data/churn.db</code>", table_cell_style)],
        [Paragraph("Stage 5: Model Training & Benchmark", table_cell_bold), Paragraph("Trained LR, RF, XGBoost; ran 5-fold CV; selected best model by ROC-AUC.", table_cell_style), Paragraph("<code>models/best_model.pkl</code>", table_cell_style)],
        [Paragraph("Stage 6: Interactive Dashboard", table_cell_bold), Paragraph("Built 5-page Streamlit web app for real-time live churn prediction & analytics.", table_cell_style), Paragraph("<code>dashboard/app.py</code>", table_cell_style)]
    ]
    t_stages = Table(stages_data, colWidths=[130, 240, 134])
    t_stages.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_stages)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 5: STEP-BY-STEP WORKED EXAMPLE
    # ---------------------------------------------------------
    story.append(Paragraph("5. Step-by-Step Worked Customer Example", h1_style))
    story.append(Paragraph(
        "To understand exactly how a customer record moves from raw data to a final ML decision, let us trace a "
        "real customer profile through the system:",
        body_style
    ))

    example_box = (
        "<b>👤 Sample Customer Profile: John Doe (ID: 7590-VHVEG)</b><br/>"
        "• <b>Contract:</b> Month-to-month (0)<br/>"
        "• <b>Tenure:</b> 2 Months<br/>"
        "• <b>Internet Service:</b> Fiber Optic (1)<br/>"
        "• <b>Payment Method:</b> Electronic Check (2)<br/>"
        "• <b>Monthly Charges:</b> $85.00 | <b>Total Charges:</b> $170.00<br/>"
        "• <b>Tech Support:</b> No (0) | <b>Online Security:</b> No (0)"
    )
    t_ex = Table([[Paragraph(example_box, body_style)]], colWidths=[504])
    t_ex.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF3C7")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F59E0B")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_ex)
    story.append(Spacer(1, 10))

    example_steps = [
        ("Step 1: Feature Transformation & Engineering",
         "The system derives engineered features for John:<br/>"
         "• <code>ChargesPerTenure</code> = $170.00 / (2 + 1) = <b>$56.67</b><br/>"
         "• <code>ServiceCount</code> = 0 (No add-on services)<br/>"
         "• <code>RiskScore</code> = Month-to-month (+1) + Fiber Optic (+1) + Electronic Check (+1) + Low Tenure (+1) = <b>4 (Maximum Risk)</b>"),
        
        ("Step 2: Vector Normalization",
         "Features are scaled into a 24-dimensional normalized vector: <code>X_john = [0, 0, 2, 85.00, 170.00, 56.67, 4, ...] &rarr; Z_john = [-0.95, 0.42, 1.85, ...]</code>"),
        
        ("Step 3: Random Forest Decision Path Evaluation",
         "The vector is passed to the 200 decision trees in <code>best_model.pkl</code>:<br/>"
         "• <i>Tree 1:</i> Contract == Month-to-month? Yes &rarr; Tenure &lt; 12? Yes &rarr; <b>Vote: CHURN (1)</b><br/>"
         "• <i>Tree 2:</i> RiskScore &gt; 3? Yes &rarr; MonthlyCharges &gt; 70? Yes &rarr; <b>Vote: CHURN (1)</b><br/>"
         "• Out of 200 trees, <b>168 trees vote CHURN (1)</b> and 32 vote RETAIN (0)."),
        
        ("Step 4: Final Probability & Decision Output",
         "• <b>Churn Probability:</b> 168 / 200 = <b>84.0%</b><br/>"
         "• <b>Final Decision Column Output:</b> <code>Churn = 1 (HIGH RISK)</code>"),
        
        ("Step 5: Automated Retention Action Triggered",
         "Because John's probability &ge; 70%, the dashboard automatically triggers a retention alert:<br/>"
         "&bull; <i>Recommended Action:</i> Offer a 15% discount on a 1-Year Contract conversion.<br/>"
         "&bull; <i>Recommended Add-on:</i> Include 3 months of free TechSupport & OnlineSecurity.")
    ]

    for title, desc in example_steps:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # CONCLUSION / SUMMARY BOX
    # ---------------------------------------------------------
    summary_html = (
        "<b>Summary & Verification:</b> This document completes the full conceptual and practical explanation of "
        "the Customer Churn Prediction System ML pipeline. The generated PDF is saved on the Desktop at:<br/>"
        f"<code>{PDF_OUTPUT_PATH}</code>"
    )
    t_sum = Table([[Paragraph(summary_html, body_style)]], colWidths=[504])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_alert_bg),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sum)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated successfully at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf()
