import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def set_cell_background(cell, hex_color):
    """Set the background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner margins (padding) of a table cell (in twentieths of a point, dxas)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    """Apply a clean light-grey horizontal border style to the table (no vertical borders)."""
    tblPr = table._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    
    # Top and bottom borders
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '4')
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), '94A3B8')
    borders.append(top)
    
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), '64748B')
    borders.append(bottom)
    
    # Inside horizontal borders
    insideH = OxmlElement('w:insideH')
    insideH.set(qn('w:val'), 'single')
    insideH.set(qn('w:sz'), '4')
    insideH.set(qn('w:space'), '0')
    insideH.set(qn('w:color'), 'CBD5E1')
    borders.append(insideH)
    
    # Clear vertical borders
    for border_name in ['left', 'right', 'insideV']:
        node = OxmlElement(f'w:{border_name}')
        node.set(qn('w:val'), 'none')
        borders.append(node)
        
    tblPr.append(borders)

def format_run(run, font_name="Calibri", size_pt=11, bold=False, italic=False, color_rgb=None):
    """Helper to apply formatting to a run."""
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb

def add_heading_1(doc, text):
    """Add a styled Heading 1 with custom colors and spacing."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    format_run(run, font_name="Arial", size_pt=18, bold=True, color_rgb=RGBColor(30, 41, 59)) # Slate 800
    # Add a thin bottom border to the paragraph XML
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12') # ~1.5 pt
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), '4F46E5') # Indigo 600
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def add_heading_2(doc, text):
    """Add a styled Heading 2."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    format_run(run, font_name="Arial", size_pt=14, bold=True, color_rgb=RGBColor(79, 70, 229)) # Indigo 600
    return p

def add_heading_3(doc, text):
    """Add a styled Heading 3."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    format_run(run, font_name="Arial", size_pt=12, bold=True, color_rgb=RGBColor(109, 40, 217)) # Violet 700
    return p

def add_body_text(doc, text, bold_prefix="", italic=False):
    """Add a styled body paragraph with standard line height and spacing."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_prefix = p.add_run(bold_prefix)
        format_run(r_prefix, font_name="Calibri", size_pt=11, bold=True, color_rgb=RGBColor(15, 23, 42))
    run = p.add_run(text)
    format_run(run, font_name="Calibri", size_pt=11, bold=False, italic=italic, color_rgb=RGBColor(51, 65, 85)) # Slate 700
    return p

def add_bullet_point(doc, text, bold_prefix=""):
    """Add a styled bullet list item."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_prefix = p.add_run(bold_prefix)
        format_run(r_prefix, font_name="Calibri", size_pt=11, bold=True, color_rgb=RGBColor(15, 23, 42))
    run = p.add_run(text)
    format_run(run, font_name="Calibri", size_pt=11, color_rgb=RGBColor(51, 65, 85))
    return p

def add_image_with_caption(doc, img_path, caption):
    """Insert an image centered with a styled caption below it."""
    if not os.path.exists(img_path):
        print(f"Warning: Image not found at {img_path}")
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.add_run().add_picture(img_path, width=Inches(5.5))
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(12)
    run_cap = p_cap.add_run(f"Figure: {caption}")
    format_run(run_cap, font_name="Calibri", size_pt=9.5, italic=True, color_rgb=RGBColor(100, 116, 139))

def add_callout_box(doc, text, title="BUSINESS NOTE"):
    """Add a styled callout box (single cell table with left border and background)."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_background(cell, "F8FAFC") # slate-50
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border of the cell
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '24') # ~3pt width
    left.set(qn('w:space'), '0')
    left.set(qn('w:color'), '4F46E5') # indigo border
    tcBorders.append(left)
    
    for side in ['top', 'bottom', 'right']:
        node = OxmlElement(f'w:{side}')
        node.set(qn('w:val'), 'none')
        tcBorders.append(node)
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"★ {title}\n")
    format_run(r_title, font_name="Arial", size_pt=10, bold=True, color_rgb=RGBColor(79, 70, 229))
    
    r_text = p.add_run(text)
    format_run(r_text, font_name="Calibri", size_pt=10, italic=True, color_rgb=RGBColor(71, 85, 105))
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6) # Spacing after table

def main():
    print("Initializing document...")
    doc = Document()
    
    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Set footer
    footer = sections[0].footer
    p_foot = footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_foot = p_foot.add_run("Customer Churn Prediction System | Page ")
    format_run(run_foot, font_name="Calibri", size_pt=9, color_rgb=RGBColor(148, 163, 184))
    # Note: Word page number fields are complex XML, this footer serves as a professional baseline placeholder
    
    # ==============================================================================
    # COVER PAGE
    # ==============================================================================
    print("Creating cover page...")
    for _ in range(3):
        doc.add_paragraph() # spacing
        
    # Accent indicator bar (styled table row)
    table_bar = doc.add_table(rows=1, cols=1)
    cell_bar = table_bar.cell(0, 0)
    set_cell_background(cell_bar, "4F46E5") # Indigo
    cell_bar.height = Inches(0.1)
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("Customer Churn Prediction & Business Intelligence System")
    format_run(run_title, font_name="Arial", size_pt=26, bold=True, color_rgb=RGBColor(15, 23, 42))
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(36)
    run_sub = p_sub.add_run("A Production-Grade End-to-End Machine Learning System with Structured SQL Analytics, Balanced Multi-Model Ensembles, and an Interactive Streamlit Dashboard Application")
    format_run(run_sub, font_name="Calibri", size_pt=13, italic=True, color_rgb=RGBColor(71, 85, 105))
    
    for _ in range(5):
        doc.add_paragraph()
        
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.line_spacing = 1.2
    
    r_meta = p_meta.add_run("PREPARED FOR:\t")
    format_run(r_meta, font_name="Calibri", size_pt=10, bold=True, color_rgb=RGBColor(100, 116, 139))
    r_meta_val = p_meta.add_run("Telecom Business Operations & Product Management Teams\n")
    format_run(r_meta_val, font_name="Calibri", size_pt=10, color_rgb=RGBColor(15, 23, 42))
    
    r_meta2 = p_meta.add_run("PREPARED BY:\t")
    format_run(r_meta2, font_name="Calibri", size_pt=10, bold=True, color_rgb=RGBColor(100, 116, 139))
    r_meta_val2 = p_meta.add_run("Senior Data Science & AI Architect Team\n")
    format_run(r_meta_val2, font_name="Calibri", size_pt=10, color_rgb=RGBColor(15, 23, 42))
    
    r_meta3 = p_meta.add_run("DATE:\t\t")
    format_run(r_meta3, font_name="Calibri", size_pt=10, bold=True, color_rgb=RGBColor(100, 116, 139))
    r_meta_val3 = p_meta.add_run("June 28, 2026\n")
    format_run(r_meta_val3, font_name="Calibri", size_pt=10, color_rgb=RGBColor(15, 23, 42))
    
    r_meta4 = p_meta.add_run("VERSION:\t\t")
    format_run(r_meta4, font_name="Calibri", size_pt=10, bold=True, color_rgb=RGBColor(100, 116, 139))
    r_meta_val4 = p_meta.add_run("1.0.0 (Production Release)")
    format_run(r_meta_val4, font_name="Calibri", size_pt=10, color_rgb=RGBColor(15, 23, 42))
    
    doc.add_page_break()

    # ==============================================================================
    # 1. EXECUTIVE SUMMARY
    # ==============================================================================
    print("Section 1...")
    add_heading_1(doc, "1. Executive Summary")
    
    add_body_text(doc, "In modern subscription-based businesses, particularly within the telecommunications sector, customer retention is one of the most critical factors influencing long-term profitability and enterprise value. Industry research shows that acquiring a new customer costs 5 to 7 times more than retaining an existing one. High churn rates (when customers terminate their contracts) directly reduce recurring revenues, increase acquisition costs, and depress customer lifetime value (CLV).")
    
    add_body_text(doc, "This technical report details the Customer Churn Prediction & Business Intelligence System, an end-to-end Python-based software package designed to identify churn-prone telecom customers, reveal key churn drivers, compute revenue-at-risk, and recommend proactive retention strategies. By combining production-grade machine learning workflows, a SQLite data warehousing layer, and an interactive Streamlit executive dashboard, this system equips decision-makers with the tools required to transform data into high-value operational strategies.")
    
    add_body_text(doc, "The analysis is conducted on the IBM Telco Customer Churn dataset, representing 7,043 telecom customers. Key highlights of the system's business and technical outcomes include:")
    
    add_bullet_point(doc, "Achieved an ROC-AUC score of 0.8381 and an F1-score of 0.6240 using a robust Random Forest ensemble model. The model is specifically tuned to favor Churn Recall (70.7%), ensuring that a high percentage of churn-prone customers are successfully intercepted before cancellation.", "Machine Learning Excellence: ")
    add_bullet_point(doc, "Identified month-to-month contracts (42.6% churn rate), Fiber Optic internet services, and Electronic Check payment methods as the highest risk factors in the dataset, prompting targeted retention operations.", "Key Operational Drivers: ")
    add_bullet_point(doc, "Successfully quantified $138,529 per month in revenue at risk, representing 30.4% of total customer revenue ($455,241) lost due to churn, establishing a clear financial baseline for customer-success interventions.", "Revenue-at-Risk Quantification: ")
    add_bullet_point(doc, "Developed a 5-page interactive dashboard ('ChurnGuard AI') featuring real-time customer risk assessment, KPI visualizations, and automated churn prevention recommendations.", "Decision Support Dashboard: ")
    
    add_callout_box(doc, 
                    "A 5% reduction in customer churn can increase company profitability by 25% to 95%. By prioritizing Churn Recall (identifying 70.7% of churners), this system allows marketing teams to target high-risk groups precisely, protecting monthly revenue and optimizing promotional budgets.", 
                    "OPERATIONAL OUTCOME")

    # ==============================================================================
    # 2. BUSINESS UNDERSTANDING & DATA SCHEMAS
    # ==============================================================================
    print("Section 2...")
    add_heading_1(doc, "2. Business Understanding & Data Schemas")
    
    add_body_text(doc, "To build an effective churn prediction model, it is vital to map raw data fields to concrete business interactions. Customer attributes are categorized into demographics, service plans, billing structures, and the target historical churn status. The system ingests 21 distinct customer attributes. Out of 7,043 initial records, data cleaning establishes a high-quality cohort of 7,021 unique customers with complete histories.")
    
    add_heading_2(doc, "2.1  Dataset Field Schema")
    add_body_text(doc, "The table below outlines the core fields contained in the raw dataset, clarifying their formats and business meanings:")
    
    # Table of Schema
    schema_fields = [
        ("gender", "Categorical (Male/Female)", "Gender of the customer, used for demographic segmentation."),
        ("SeniorCitizen", "Binary (0/1)", "Indicates if the customer is 65 years or older (senior)."),
        ("Partner", "Binary (Yes/No)", "Indicates if the customer has a partner/spouse."),
        ("Dependents", "Binary (Yes/No)", "Indicates if the customer has children or dependents."),
        ("tenure", "Numeric (Integer)", "Number of months the customer has subscribed to the service."),
        ("PhoneService", "Binary (Yes/No)", "Indicates if the customer has a landline telephone subscription."),
        ("MultipleLines", "Categorical (Yes/No/No phone)", "Whether the customer has multiple telephone lines."),
        ("InternetService", "Categorical (DSL/Fiber optic/No)", "Type of high-speed internet service subscribed."),
        ("OnlineSecurity", "Categorical (Yes/No/No internet)", "Whether online safety/security add-on is active."),
        ("OnlineBackup", "Categorical (Yes/No/No internet)", "Whether cloud backup add-on is active."),
        ("DeviceProtection", "Categorical (Yes/No/No internet)", "Whether equipment protection coverage is active."),
        ("TechSupport", "Categorical (Yes/No/No internet)", "Whether premium technical support is active."),
        ("StreamingTV", "Categorical (Yes/No/No internet)", "Whether customer streams television contents."),
        ("StreamingMovies", "Categorical (Yes/No/No internet)", "Whether customer streams movies over the network."),
        ("Contract", "Categorical (Month-to-month/1yr/2yr)", "The payment contract cycle and commitment length."),
        ("PaperlessBilling", "Binary (Yes/No)", "Indicates if the customer receives electronic invoices."),
        ("PaymentMethod", "Categorical", "Payment mechanism (Electronic check, Mailed check, Bank transfer, Credit card)."),
        ("MonthlyCharges", "Numeric (Float)", "The monthly recurring service charge amount in USD."),
        ("TotalCharges", "Numeric (Float/String)", "Total cumulative charges paid by the customer over their tenure."),
        ("Churn", "Target (Yes/No)", "Whether the customer cancelled their subscription (Target Variable).")
    ]
    
    tbl_schema = doc.add_table(rows=1, cols=3)
    tbl_schema.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_schema)
    
    hdr_cells = tbl_schema.rows[0].cells
    hdr_cells[0].text = "Field Name"
    hdr_cells[1].text = "Data Type & Format"
    hdr_cells[2].text = "Business Explanation"
    for cell in hdr_cells:
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        for p in cell.paragraphs:
            for r in p.runs:
                format_run(r, font_name="Arial", size_pt=9.5, bold=True, color_rgb=RGBColor(255, 255, 255))
                
    for field, dtype, desc in schema_fields:
        row_cells = tbl_schema.add_row().cells
        row_cells[0].text = field
        row_cells[1].text = dtype
        row_cells[2].text = desc
        
        # Style row text
        for i, cell in enumerate(row_cells):
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                is_bold = (i == 0)
                color = RGBColor(15, 23, 42) if is_bold else RGBColor(71, 85, 105)
                format_run(r, font_name="Calibri", size_pt=9, bold=is_bold, color_rgb=color)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ==============================================================================
    # 3. DATA PREPROCESSING PIPELINE
    # ==============================================================================
    print("Section 3...")
    add_heading_1(doc, "3. Data Preprocessing Pipeline")
    
    add_body_text(doc, "Before feeding data to machine learning models, the raw data must undergo a sequence of cleaning, normalization, and encoding steps. Raw telecom datasets are typically unstructured and contain missing fields, outliers, or inconsistent categorical variables. The system implements a robust, modular pipeline designed to clean and transform the dataset programmatically, saving the intermediate results for visual exploration.")
    
    add_heading_2(doc, "3.1  Data Cleaning & Imputation")
    add_body_text(doc, "The preprocessing pipeline performs several data-integrity actions:")
    add_bullet_point(doc, "The raw customerID is unique for each customer but contains no predictive weight. Removing it prevents overfitting on random identifiers.", "ID Exclusion: ")
    add_bullet_point(doc, "Duplicate customer records are identified and removed, resulting in 22 duplicates purged and leaving 7,021 unique observations.", "Duplicate Removal: ")
    add_bullet_point(doc, "The TotalCharges column is sometimes read as a string because new customers with a tenure of 0 have blank space characters (' ') instead of values. The pipeline converts these spaces to NaN and imputes them mathematically as tenure multiplied by MonthlyCharges (yielding $0.00).", "TotalCharges Formatting & Imputation: ")
    add_bullet_point(doc, "Any remaining numerical missing fields are filled with their respective column medians, and categorical columns are filled with their modes to prevent data loss.", "Logical Safe Imputation: ")
    
    add_heading_2(doc, "3.2  Outlier Capping (Winsorisation)")
    add_body_text(doc, "Outliers in continuous features like MonthlyCharges and TotalCharges can degrade the performance of distance-based models (such as Logistic Regression). The pipeline applies a Winsorisation method, capping outlier values at the 1st percentile (minimum threshold) and 99th percentile (maximum threshold). For instance, extreme TotalCharges values are capped, reducing noise while preserving the underlying distribution.")
    
    add_heading_2(doc, "3.3  Feature Encoding")
    add_body_text(doc, "Machine learning algorithms require numeric matrices. Categorical labels are encoded using the following structured approach:")
    add_bullet_point(doc, "Partner, Dependents, PhoneService, and PaperlessBilling are mapped directly to 0 (No) and 1 (Yes).", "Binary Mapping: ")
    add_bullet_point(doc, "For service add-on columns (e.g., OnlineSecurity, TechSupport, OnlineBackup), values such as 'No phone service' or 'No internet service' are conceptually equivalent to 'No'. They are encoded as 0, while active services are mapped to 1. This prevents a massive expansion of variables via one-hot encoding.", "Smart Service Encoding: ")
    add_bullet_point(doc, "Contract is ordinally encoded ('Month-to-month' = 0, 'One year' = 1, 'Two year' = 2) to capture the natural temporal hierarchy, where longer-term commitments are logically ordered.", "Ordinal Contract Mapping: ")
    add_bullet_point(doc, "Remaining nominal columns (gender, InternetService, PaymentMethod) are converted into distinct integer categories using a LabelEncoder, mapping gender ('Female' = 0, 'Male' = 1), internet service ('DSL' = 0, 'Fiber optic' = 1, 'No' = 2), and payment methods to compact representations.", "Label Encoding: ")
    
    add_heading_2(doc, "3.4  Feature Scaling & Train/Test Split")
    add_body_text(doc, "To prevent features with larger scales (like TotalCharges, which ranges up to $8,000) from dominating features with smaller scales (like tenure, ranging from 0 to 72), standard scaling is applied. The continuous columns (tenure, MonthlyCharges, TotalCharges) are scaled using standard normalization (StandardScaler):")
    
    # Standard formula block
    p_eq = doc.add_paragraph()
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq = p_eq.add_run("z = (x - μ) / σ")
    format_run(r_eq, font_name="Consolas", size_pt=12, bold=True, color_rgb=RGBColor(30, 41, 59))
    
    add_body_text(doc, "where μ represents the training mean and σ represents the training standard deviation. Scaling parameters are computed strictly on the training set and applied to the test set to prevent data leakage.")
    add_body_text(doc, "Finally, the data is split into training (80%) and test (20%) sets using a stratified split on the Churn target variable. Stratification guarantees that both the training and test sets maintain the exact same churn ratio (~26.45%), which is essential for consistent model evaluation.")

    # ==============================================================================
    # 4. ADVANCED FEATURE ENGINEERING & BALANCING
    # ==============================================================================
    print("Section 4...")
    add_heading_1(doc, "4. Advanced Feature Engineering & SMOTE")
    
    add_body_text(doc, "To boost model predictive performance, five domain-specific features were engineered from the cleaned dataset. These engineered features capture complex interactions that individual variables cannot describe, allowing linear and tree-based estimators to model non-linear boundaries.")
    
    add_heading_2(doc, "4.1  Engineered Features & Business Rationale")
    add_bullet_point(doc, "Calculated as MonthlyCharges / (tenure + 1). Business Rationale: Indicates customer intensity and average monthly spend per month of relationship. A high value suggests high billing intensity early in the relationship, which often correlates with high churn risk.", "ChargesPerTenure: ")
    add_bullet_point(doc, "The count of active services subscribed (out of OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies). Business Rationale: Customers who subscribe to multiple services are more integrated into the operator's ecosystem, creating higher switching costs and lowering churn probability.", "ServiceCount: ")
    add_bullet_point(doc, "A binary flag indicating if the customer's MonthlyCharges fall in the top quartile (>= $89.85). Business Rationale: High-value customers represent the largest revenue risk and should be flagged for white-glove support.", "IsHighValue: ")
    add_bullet_point(doc, "A binary flag indicating if tenure is greater than 24 months. Business Rationale: Customers who survive past 2 years are considered 'loyal' and exhibit distinct behavioral patterns compared to new subscribers.", "HasLoyalty: ")
    add_bullet_point(doc, "A multi-factor risk indicator. Calculated as: RiskScore = 0.4 * contract_risk + 0.3 * charges_norm + 0.3 * tenure_norm. contract_risk is higher for Month-to-Month contracts. charges_norm represents scaled spend, and tenure_norm represents the inverse of scaled tenure. Business Rationale: Combines contract commitment, pricing pressure, and customer maturity into a single value, representing a strong heuristic predictor.", "RiskScore: ")
    
    add_heading_2(doc, "4.2  Oversampling with SMOTE (Class Imbalance Correction)")
    add_body_text(doc, "The dataset has a 3:1 imbalance ratio (26.45% Churners vs. 73.55% Retainers). Fitting models on imbalanced sets causes them to predict the majority class (No Churn) accurately but fail to detect the minority class (Churn). To correct this, the system applies SMOTE (Synthetic Minority Over-sampling Technique) on the training set.")
    
    add_body_text(doc, "SMOTE generates synthetic examples of the minority class along the line segments joining k-nearest neighbors (k=5). This balances the training classes to exactly 50/50, ensuring that decision boundaries are not biased toward the majority class. The test set remains completely untouched (unbalanced) to reflect real-world distributions during evaluation.")
    
    add_callout_box(doc,
                    "SMOTE is applied ONLY to the training partition after the train-test split. Applying SMOTE to the entire dataset before splitting causes synthetic data leakage into the test set, producing artificially inflated accuracy scores that collapse in production.",
                    "METHODOLOGY WARNING")

    # ==============================================================================
    # 5. EXPLORATORY DATA ANALYSIS (EDA)
    # ==============================================================================
    print("Section 5...")
    add_heading_1(doc, "5. Exploratory Data Analysis (EDA) & Insights")
    
    add_body_text(doc, "Understanding data distributions and variables' relationships to churn is vital for business strategy. In this section, we analyze the 9 professional EDA figures generated by the pipeline and saved in reports/figures/.")
    
    add_heading_2(doc, "5.1  Visual Insights Analysis")
    
    # 1. Churn Distribution
    add_heading_3(doc, "Figure 1: Churn Distribution")
    add_body_text(doc, "This figure shows the overall customer class balance. The dataset consists of 73.55% (5,164) active, retained customers, and 26.45% (1,857) customers who have churned. This highlights the baseline churn rate of 26.45%, serving as the benchmark against which model metrics are evaluated.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "01_churn_distribution.png"), "Distribution of Churn Status (Pie & Bar Count)")
    
    # 2. Tenure Analysis
    add_heading_3(doc, "Figure 2: Tenure Analysis")
    add_body_text(doc, "The tenure histogram and box plots reveal a clear relationship: customers who churn are heavily clustered in the first 0 to 12 months. The churn curve is extremely steep at tenure = 1 month, suggesting a critical onboarding issue. The median tenure for churned customers is only 10 months, whereas the median tenure for retained customers is 38 months.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "02_tenure_analysis.png"), "Customer Tenure Distribution & Box Plot by Churn Status")
    
    # 3. Contract Type Analysis
    add_heading_3(doc, "Figure 3: Contract Type Analysis")
    add_body_text(doc, "Month-to-month contracts have an alarming churn rate of 42.6% (1,643 out of 3,853 customers). In stark contrast, one-year contracts experience 11.3% churn, and two-year contracts show an exceptionally low churn rate of 2.8% (48 out of 1,695 customers). This suggests that contract length is the single most powerful operational driver of retention.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "03_contract_analysis.png"), "Churn Rates and Customer Counts by Contract Type")
    
    # 4. Monthly Charges Analysis
    add_heading_3(doc, "Figure 4: Monthly Charges Analysis")
    add_body_text(doc, "The monthly charges density curve shows that churned customers are clustered around high monthly charges ($70–$100), whereas retained customers have a bimodal distribution with a large spike at lower monthly charges ($20). This indicates that higher price sensitivity is a major trigger for customer attrition.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "04_monthly_charges.png"), "Monthly Charges Density Histogram & Violin Plot by Churn Status")
    
    # 5. Correlation Heatmap
    add_heading_3(doc, "Figure 5: Correlation Heatmap")
    add_body_text(doc, "This heatmap calculates the linear correlations among all numeric features. The target variable Churn is positively correlated with MonthlyCharges, PaperlessBilling, and SeniorCitizen, and negatively correlated with tenure, Contract, and partner status. It also shows a strong positive correlation between TotalCharges and tenure, which is logically expected.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "05_correlation_heatmap.png"), "Pearson Correlation Heatmap of Cleaned Features")
    
    # 6. Churn by Demographics
    add_heading_3(doc, "Figure 6: Churn by Demographics")
    add_body_text(doc, "Analyzing demographics reveals that senior citizens have a significantly higher churn rate (41.7%) than non-seniors (23.6%). Additionally, customers without partners (33.0% churn) or dependents (31.3% churn) are much more likely to churn than those with partners (19.7% churn) or dependents (15.5% churn). Gender exhibits negligible impact, with Male and Female churn rates within 0.5% of each other.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "06_churn_demographics.png"), "Churn Rates Segmented by Demographic Attributes")
    
    # 7. Service & Payment Method Analysis
    add_heading_3(doc, "Figure 7: Service & Payment Method Analysis")
    add_body_text(doc, "Fiber optic internet service has a churn rate of 40.7%, which is much higher than DSL (19.0%) or no internet (7.4%). This suggests a potential service-reliability issue or high price friction on the fiber product. Additionally, customers using 'Electronic Check' as their payment method exhibit a 45.3% churn rate, while credit card or bank transfer users maintain a low churn rate (~15.0%).")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "07_service_payment.png"), "Churn Rates by Internet Service Type and Payment Method")
    
    # 8. Monthly Charges vs Tenure
    add_heading_3(doc, "Figure 8: Monthly Charges vs Tenure scatter")
    add_body_text(doc, "This scatter plot illustrates the distribution of customers across spend and tenure. Churned customers (red dots) are concentrated in the top-left section (short tenure, high monthly spend), confirming that customers paying high prices early on represent the most volatile subscriber segment.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "08_charges_vs_tenure.png"), "Scatter Distribution: Monthly Charges vs. Tenure by Churn")
    
    # 9. Churn by Total Charges Quartile
    add_heading_3(doc, "Figure 9: Churn by Total Charges Quartile")
    add_body_text(doc, "Dividing customers into quartiles based on cumulative spend shows that churn rate is highest in the lower-spend groups, primarily because those groups consist of new customers with short tenures. Low cumulative billing indicates early relationships, which are highly volatile.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "09_churn_by_total_charges.png"), "Churn Rate by Cumulative Total Charges Quartiles")

    # ==============================================================================
    # 6. SQL DATA WAREHOUSING & INTEGRATION
    # ==============================================================================
    print("Section 6...")
    add_heading_1(doc, "6. SQL Data Warehousing & Integration")
    
    add_body_text(doc, "To support production deployment and business intelligence workflows, the system stores the processed dataset in an relational SQLite database (located at data/churn.db). Storing dataset tables in SQL enables direct integration with business intelligence (BI) engines (e.g., Tableau, PowerBI) and allows database administrators (DBAs) to execute ad-hoc analysis in real-time.")
    
    add_body_text(doc, "Ten key analytics queries are defined in sql/analytics_queries.sql to quantify risk. The queries and their business value are summarized below:")
    
    # 10 SQL bullet points
    add_bullet_point(doc, "Computes the baseline churn rate across the entire active subscriber database. Yields 26.45% overall churn rate.", "1. Overall Churn Summary: ")
    add_bullet_point(doc, "Generates a prioritised mailing list of customers who have churned and had high monthly spend (greater than the database average of $64.80) to target with recovery campaigns.", "2. High-Risk Customer List: ")
    add_bullet_point(doc, "Ranks payment channels by churn rate, showing Electronic Checks as a high-risk payment method (45.3% churn).", "3. Churn by Payment Method: ")
    add_bullet_point(doc, "Exposes how contract length impacts churn (Month-to-month = 42.6%, One-year = 11.3%, Two-year = 2.8%), proving the value of multi-year contract conversions.", "4. Churn by Contract Type: ")
    add_bullet_point(doc, "Compares average monthly revenue (ARPU) and customer lifetime value (LTV) for churned vs. retained groups.", "5. Revenue Segment Comparison: ")
    add_bullet_point(doc, "Combines contract commitment and internet type, revealing that Month-to-Month Fiber Optic users represent the single most volatile segment (churn rate > 50%).", "6. Top Churn Segments: ")
    add_bullet_point(doc, "Summates the monthly charges of all churned customers, quantifying exactly how much recurring monthly revenue is lost ($138,529/month out of $455,241 total).", "7. Revenue at Risk: ")
    add_bullet_point(doc, "Groups tenure into cohorts (e.g., 0-12 months, 13-24 months), showing that the first year of onboarding represents the highest churn risk (47.4% churn rate).", "8. Tenure Cohort Analysis: ")
    add_bullet_point(doc, "Compares churn rates between older and younger customer demographics, highlighting a high churn rate (41.7%) among seniors.", "9. Senior Citizen Churn Analysis: ")
    add_bullet_point(doc, "Filters month-to-month contracts and electronic check payment methods to calculate high-risk monthly revenue ($243,158/month).", "10. High-Risk Month-to-Month and Electronic Check Cohort: ")

    # ==============================================================================
    # 7. MACHINE LEARNING MODEL PERFORMANCE
    # ==============================================================================
    print("Section 7...")
    add_heading_1(doc, "7. Machine Learning Model Performance")
    
    add_body_text(doc, "The core of the system consists of three machine learning algorithms trained, cross-validated, and compared on the balanced training partition:")
    add_bullet_point(doc, "Provides an interpretable linear baseline. Modeling coefficients represent log-odds multipliers, offering direct visibility into risk factors.", "1. Logistic Regression: ")
    add_bullet_point(doc, "An ensemble bagging model of decision trees. It handles non-linearities, features interactions, and is highly robust to overfitting.", "2. Random Forest: ")
    add_bullet_point(doc, "An advanced gradient boosting framework. Optimizes a structured loss function sequentially, typically yielding high accuracy.", "3. XGBoost Classifier: ")
    
    add_heading_2(doc, "7.1  Model Evaluation Metrics")
    add_body_text(doc, "We evaluate models using the test set (representing unseen data). Given the business objective of protecting revenue, the following metrics are tracked:")
    add_bullet_point(doc, "TP / (TP + FP) – of all predicted churners, how many actually churn. Higher precision avoids wasting promotional costs on customers who wouldn't have churned.", "Precision: ")
    add_bullet_point(doc, "TP / (TP + FN) – of all actual churners, how many did we successfully flag. Higher recall ensures we catch a large share of the revenue at risk.", "Recall (Sensitivity): ")
    add_bullet_point(doc, "Harmonic mean of Precision and Recall. Useful for finding a balance between the two metrics.", "F1-Score: ")
    add_bullet_point(doc, "Receiver Operating Characteristic Area Under Curve – measures the probability that the model will rank a randomly chosen churner higher than a randomly chosen non-churner. It serves as the primary metric for model comparison.", "ROC-AUC: ")
    
    add_heading_2(doc, "7.2  Evaluation Results Table")
    add_body_text(doc, "The table below presents the final test-set evaluation metrics for all three models:")
    
    tbl_models = doc.add_table(rows=4, cols=6)
    tbl_models.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_models)
    
    hdr_m = tbl_models.rows[0].cells
    hdr_m[0].text = "Model Name"
    hdr_m[1].text = "Accuracy"
    hdr_m[2].text = "Precision"
    hdr_m[3].text = "Recall"
    hdr_m[4].text = "F1-Score"
    hdr_m[5].text = "ROC-AUC"
    for cell in hdr_m:
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        for p in cell.paragraphs:
            for r in p.runs:
                format_run(r, font_name="Arial", size_pt=9.5, bold=True, color_rgb=RGBColor(255, 255, 255))
                
    model_data = [
        ("Logistic Regression", "75.52%", "52.81%", "70.70%", "60.46%", "0.8350"),
        ("Random Forest (Best)", "77.44%", "55.84%", "70.70%", "62.40%", "0.8381"),
        ("XGBoost Classifier", "73.59%", "50.09%", "76.08%", "60.41%", "0.8209")
    ]
    
    for name, acc, prec, rec, f1, auc in model_data:
        row_cells = tbl_models.add_row().cells
        row_cells[0].text = name
        row_cells[1].text = acc
        row_cells[2].text = prec
        row_cells[3].text = rec
        row_cells[4].text = f1
        row_cells[5].text = auc
        
        for i, cell in enumerate(row_cells):
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                is_best = ("Best" in name or "Random Forest" in name)
                color = RGBColor(79, 70, 229) if (is_best and i == 0) else (RGBColor(15, 23, 42) if is_best else RGBColor(71, 85, 105))
                format_run(r, font_name="Calibri", size_pt=9, bold=(is_best and i == 0), color_rgb=color)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    add_heading_2(doc, "7.3  Best Model Analysis (Random Forest)")
    add_body_text(doc, "Random Forest achieved the highest ROC-AUC (0.8381) and F1-score (0.6240) in testing. In customer retention, capturing true churners is critical, so we prioritize Churn Recall (70.7%) alongside Precision (55.84%). This means the model successfully detects 70.7% of the customers who are going to churn, with more than half of the flagged cohort representing true risk, allowing the business to act before cancellation.")
    
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "model_comparison.png"), "Model Metric Comparison Chart")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "roc_curves.png"), "ROC Curves Overlay for Trained Estimators")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "confusion_matrix_random_forest.png"), "Confusion Matrix for the Selected Random Forest Model")
    
    add_heading_2(doc, "7.4  Feature Importance Analysis")
    add_body_text(doc, "The Random Forest feature importances chart ranks variables by their predictive weight. The top predictor is RiskScore (0.1928), followed by ChargesPerTenure (0.1412), Contract Type (0.1228), MonthlyCharges (0.0852), and tenure (0.0806).")
    add_body_text(doc, "Notably, three out of the top five features (RiskScore, ChargesPerTenure, and HasLoyalty) are custom engineered. This demonstrates the value of feature engineering, as these derived variables capture non-linear behavioral traits that raw variables cannot model directly.")
    add_image_with_caption(doc, os.path.join(PROJECT_ROOT, "reports", "figures", "feature_importance_random_forest.png"), "Random Forest Feature Importances Chart")

    # ==============================================================================
    # 8. STREAMLIT INTERACTIVE DASHBOARD
    # ==============================================================================
    print("Section 8...")
    add_heading_1(doc, "8. Interactive Dashboard Application")
    
    add_body_text(doc, "To make these predictive models accessible to non-technical business teams, the system includes an interactive web dashboard developed in Streamlit (located in dashboard/app.py).")
    
    add_body_text(doc, "The dashboard features custom CSS styling to create a modern web interface. It includes CSS variables, a sleek dark mode theme, and rounded borders. Key metrics (churn rate, monthly revenue, revenue at risk) are highlighted in card components with micro-animations.")
    
    add_body_text(doc, "The application is structured into five functional pages, accessible via the sidebar navigation:")
    add_bullet_point(doc, "Provides a high-level overview of the business. Displays KPIs for total subscribers, churn rate, monthly revenue, and monthly revenue at risk, alongside interactive charts showing churn drivers.", "1. Home & KPIs: ")
    add_bullet_point(doc, "A page where sales or customer service agents can input details for a single customer (tenure, monthly spend, contract type, services, etc.) and generate a real-time churn prediction, probability gauge, and customized retention recommendations.", "2. Predict Churn: ")
    add_bullet_point(doc, "Displays the 9 publication-grade EDA charts alongside interactive Plotly graphs, allowing teams to explore relationships in the data dynamically.", "3. EDA & Insights: ")
    add_bullet_point(doc, "Compares model metrics, displays ROC curves, and includes a radar chart to help stakeholders understand model strengths and weaknesses.", "4. Model Performance: ")
    add_bullet_point(doc, "An interactive data table where users can filter, sort, search, and download the preprocessed subscriber dataset.", "5. Data Explorer: ")
    
    add_callout_box(doc,
                    "The Predict Churn page features custom risk thresholds: probabilities >= 65% are flagged as 'High Risk' (red card), between 40% and 65% are 'Medium Risk' (orange card), and below 40% are 'Low Risk' (green card). Recommendations adapt dynamically based on the customer's profile (e.g., suggesting auto-pay for electronic check users).",
                    "DASHBOARD LOGIC")

    # ==============================================================================
    # 9. EXECUTION FLOW & SYSTEM ARCHITECTURE
    # ==============================================================================
    print("Section 9...")
    add_heading_1(doc, "9. System Architecture & Execution Flow")
    
    add_body_text(doc, "The Customer Churn Prediction System is structured as a modular pipeline, allowing each phase of the process to be developed, debugged, and run independently. The diagram below illustrates the system architecture and flow of data:")
    
    # Text-based flow diagram
    p_flow = doc.add_paragraph()
    p_flow.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_flow.paragraph_format.left_indent = Inches(0.5)
    
    flow_steps = [
        "1. Raw Dataset (URL / Synthetic Generator) → data/raw/telco_churn_raw.csv",
        "2. Preprocessing Script (src/preprocessing.py) → Cleans, encodes, and splits data",
        "3. Feature Engineering (src/feature_engineering.py) → Adds 5 features and applies SMOTE",
        "4. SQL Database (src/sql_integration.py) → Stores processed data in data/churn.db",
        "5. Model Training (src/train_model.py) → Fits LR, RF, XGB, selects best model, saves to models/",
        "6. Evaluation Outputs → Generates plots in reports/figures/",
        "7. Master Runner (main.py) → Orchestrates steps 1-6 sequentially",
        "8. Streamlit App (dashboard/app.py) → Runs the interactive user interface"
    ]
    for step in flow_steps:
        r_step = p_flow.add_run(f" {step}\n")
        format_run(r_step, font_name="Consolas", size_pt=9.5, color_rgb=RGBColor(30, 41, 59))
        
    add_body_text(doc, "The master pipeline runner (main.py) orchestrates the entire workflow. Run 'python main.py' to rebuild the data folders, train models, save serialized artifacts, and generate evaluation plots from scratch. This guarantees consistency across the system.")

    # ==============================================================================
    # 10. BUSINESS RECOMMENDATIONS & RETENTION STRATEGY
    # ==============================================================================
    print("Section 10...")
    add_heading_1(doc, "10. Business Recommendations & Retention Strategy")
    
    add_body_text(doc, "Exploratory Data Analysis and SQL analytics provide actionable operational recommendations for reducing churn and protecting recurring monthly revenue:")
    
    add_heading_2(doc, "10.1  Strategic Initiatives")
    
    add_body_text(doc, "Month-to-month contracts have a 42.6% churn rate. The business should design campaigns to migrate month-to-month users to 1-year or 2-year contracts. For example, offer a small discount (e.g., 5-10% off monthly bills) in exchange for a 12-month commitment. The data proves that two-year contracts have an exceptionally low churn rate of 2.8%, making this transition highly effective.", bold_prefix="1. Contract Migration Campaigns: ")
    
    add_body_text(doc, "Electronic check users have a 45.3% churn rate, while Credit Card or Bank Transfer (auto-pay) users remain under 16% churn. Marketing teams should encourage auto-pay setup by offering a one-time credit (e.g., $10) or account reward points. Auto-pay reduces billing friction and prevents churn caused by expired cards or payment failures.", bold_prefix="2. Automated Payment Promotions: ")
    
    add_body_text(doc, "Fiber optic customers churn at a rate of 40.7%, which is much higher than DSL users (19.0%). Since fiber is generally a superior technology, this high churn suggests potential technical service issues, customer support friction, or uncompetitive pricing. Operations teams should audit fiber connection quality, evaluate pricing strategies, and set up a post-installation support check-in.", bold_prefix="3. Fiber Optic Service Audit: ")
    
    add_body_text(doc, "Customer churn is heavily concentrated in the first year of tenure, peaking at tenure = 1 month. Customer Success teams should implement an automated onboarding sequence, sending helpful guides, usage tips, and technical checks at day 7, 30, and 90 to help new subscribers adopt the service early on.", bold_prefix="4. Targeted Early Onboarding: ")
    
    add_body_text(doc, "Customers who subscribe to multiple services (OnlineSecurity, TechSupport, etc.) show low churn rates. Customer success managers should design bundle cross-selling campaigns (e.g., 'Add Online Security for just $3/month') to integrate customers further into the service ecosystem, increasing switching costs.", bold_prefix="5. Add-On Bundle Cross-Selling: ")

    # ==============================================================================
    # 11. TECHNICAL SETUP & VERIFICATION
    # ==============================================================================
    print("Section 11...")
    add_heading_1(doc, "11. Technical Setup & Verification")
    
    add_body_text(doc, "To verify the codebase and deploy the system, follow these setup and execution steps:")
    
    add_heading_2(doc, "11.1  Installation & Prerequisites")
    add_body_text(doc, "The system requires Python 3.9+ and pip. Follow these steps to set up a local environment:")
    
    p_code = doc.add_paragraph()
    p_code.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_code.paragraph_format.left_indent = Inches(0.5)
    code_lines = [
        "# 1. Create a virtual environment",
        "python -m venv venv",
        "venv\\Scripts\\activate  # Windows",
        "# source venv/bin/activate  # Linux/Mac",
        "",
        "# 2. Install dependencies",
        "pip install -r requirements.txt"
    ]
    for line in code_lines:
        r_line = p_code.add_run(line + "\n")
        format_run(r_line, font_name="Consolas", size_pt=9.5, color_rgb=RGBColor(51, 65, 85))
        
    add_heading_2(doc, "11.2  Pipeline Execution")
    add_body_text(doc, "To run the end-to-end data preparation, feature engineering, SQL storage, model training, and plot generation pipeline, execute the main script:")
    
    p_code2 = doc.add_paragraph()
    p_code2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_code2.paragraph_format.left_indent = Inches(0.5)
    r_code2 = p_code2.add_run("python main.py\n")
    format_run(r_code2, font_name="Consolas", size_pt=9.5, color_rgb=RGBColor(30, 41, 59))
    
    add_heading_2(doc, "11.3  Launching the Dashboard")
    add_body_text(doc, "Once the pipeline completes and generates model files, start the Streamlit web dashboard:")
    
    p_code3 = doc.add_paragraph()
    p_code3.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_code3.paragraph_format.left_indent = Inches(0.5)
    r_code3 = p_code3.add_run("streamlit run dashboard/app.py\n")
    format_run(r_code3, font_name="Consolas", size_pt=9.5, color_rgb=RGBColor(30, 41, 59))

    # ==============================================================================
    # 12. FUTURE ROADMAP
    # ==============================================================================
    print("Section 12...")
    add_heading_1(doc, "12. Future Product Roadmap")
    
    add_body_text(doc, "To scale this customer churn prediction system into a production-grade enterprise application, the following updates are planned:")
    
    add_bullet_point(doc, "Build a real-time prediction microservice using FastAPI, enabling CRM systems (e.g., Salesforce, HubSpot) to request customer risk scores programmatically during support calls.", "FastAPI REST API: ")
    add_bullet_point(doc, "Integrate MLflow to log runs, track hyperparameters, and manage versions, enabling continuous training and deployment.", "MLflow Experiment Tracking: ")
    add_bullet_point(doc, "Deploy SHAP (SHapley Additive exPlanations) in the dashboard, giving customer success teams clear explanations of the specific features driving individual risk scores.", "SHAP Explainability: ")
    add_bullet_point(doc, "Migrate SQLite to PostgreSQL to scale database operations, handle high concurrent queries, and integrate with production data warehouses.", "Enterprise PostgreSQL Migration: ")
    add_bullet_point(doc, "Package the system, Streamlit dashboard, and SQLite database into Docker containers to guarantee consistent deployment across local, staging, and production environments.", "Docker Containerisation: ")
    add_bullet_point(doc, "Create a CI/CD workflow in GitHub Actions to run unit tests, check code quality, and automate deployments on commit.", "Automated CI/CD Pipeline: ")

    # Save Document
    report_path = os.path.join(PROJECT_ROOT, "Customer_Churn_Prediction_System_Report.docx")
    print(f"Saving document to: {report_path}")
    doc.save(report_path)
    print("Document saved successfully!")

if __name__ == "__main__":
    main()
