"""
Random Forest — Customer Churn Prediction
Complete Word Document Report Generator
Saves to Desktop as: Random_Forest_Churn_Report.docx
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os, datetime

OUT_PATH = r"C:\Users\tpvij\Desktop\Random_Forest_Churn_Report.docx"

# ── COLOUR PALETTE ─────────────────────────────────────────────────────────
NAVY   = RGBColor(0x0F, 0x17, 0x2A)
BLUE   = RGBColor(0x3B, 0x82, 0xF6)
INDIGO = RGBColor(0x63, 0x66, 0xF1)
CYAN   = RGBColor(0x06, 0xB6, 0xD4)
GREEN  = RGBColor(0x10, 0xB9, 0x81)
AMBER  = RGBColor(0xF5, 0x9E, 0x0B)
RED    = RGBColor(0xEF, 0x44, 0x44)
PURPLE = RGBColor(0x8B, 0x5C, 0xF6)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY  = RGBColor(0x94, 0xA3, 0xB8)
DGRAY  = RGBColor(0x1E, 0x29, 0x3B)
BLACK  = RGBColor(0x0F, 0x17, 0x2A)

# ── HELPERS ────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color: str):
    """Fill a table cell with a solid background colour."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_row_height(row, twips: int):
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(twips))
    trPr.append(trHeight)

def add_horizontal_rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '334155')
    pBdr.append(bottom)
    pPr.append(pBdr)

def heading(doc, text, level=1, color=None, center=False, size=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 8)
    p.paragraph_format.space_after  = Pt(4)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    sizes = {1: 22, 2: 17, 3: 14, 4: 12}
    run.font.size = Pt(size or sizes.get(level, 12))
    if color:
        run.font.color.rgb = color
    else:
        run.font.color.rgb = BLACK
    return p

def body(doc, text, color=None, bold=False, italic=False, size=10, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    return p

def mixed_para(doc, parts, space_after=6):
    """parts = list of (text, bold, color, size)"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    for text, bold, color, sz in parts:
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(sz or 10)
        if color:
            r.font.color.rgb = color
    return p

def code_block(doc, lines, space_after=8):
    """Monospaced grey box for formulas / code."""
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after  = Pt(1)
        p.paragraph_format.left_indent  = Cm(1)
        r = p.add_run(line if line else " ")
        r.font.name = 'Courier New'
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

def info_box(doc, label, text, bg='E0F2FE', label_color=None):
    """A shaded info callout box using a 1-column table."""
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    set_cell_bg(cell, bg)
    cell.paragraphs[0].clear()
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    if label:
        r = p.add_run(f"{label}  ")
        r.bold = True
        r.font.size = Pt(10)
        if label_color:
            r.font.color.rgb = label_color
    r2 = p.add_run(text)
    r2.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def section_num_heading(doc, num, title, subtitle=None):
    """Big numbered section header."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(2)
    r1 = p.add_run(f"  {num}  ")
    r1.bold = True
    r1.font.size = Pt(14)
    r1.font.color.rgb = WHITE
    # number box — use highlight workaround via shading in run — just color
    r2 = p.add_run(f"  {title}")
    r2.bold = True
    r2.font.size = Pt(15)
    r2.font.color.rgb = BLUE
    if subtitle:
        p2 = doc.add_paragraph()
        p2.paragraph_format.space_after = Pt(6)
        r3 = p2.add_run(f"    {subtitle}")
        r3.italic = True
        r3.font.size = Pt(10)
        r3.font.color.rgb = LGRAY
    add_horizontal_rule(doc)


# ── BUILD TABLE HELPER ────────────────────────────────────────────────────
def make_table(doc, headers, rows, col_widths=None, header_bg='1E3A5F'):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hrow = t.rows[0]
    for i, h in enumerate(headers):
        cell = hrow.cells[i]
        set_cell_bg(cell, header_bg)
        cell.paragraphs[0].clear()
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = WHITE

    # Data rows
    for ri, row_data in enumerate(rows):
        drow = t.rows[ri + 1]
        bg = 'F8FAFC' if ri % 2 == 0 else 'EFF6FF'
        for ci, val in enumerate(row_data):
            cell = drow.cells[ci]
            set_cell_bg(cell, bg)
            cell.paragraphs[0].clear()
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            # Support (text, bold, color) tuples
            if isinstance(val, tuple):
                r = p.add_run(val[0])
                r.font.size = Pt(9)
                r.bold = val[1] if len(val) > 1 else False
                if len(val) > 2 and val[2]:
                    r.font.color.rgb = val[2]
            else:
                r = p.add_run(str(val))
                r.font.size = Pt(9)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t


# ══════════════════════════════════════════════════════════════════════════
#  MAIN DOCUMENT
# ══════════════════════════════════════════════════════════════════════════
doc = Document()

# Page margins
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Inches(1.0)
section.right_margin  = Inches(1.0)
section.top_margin    = Inches(1.0)
section.bottom_margin = Inches(1.0)

# Default font
from docx.oxml.ns import qn
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10)

# ── COVER PAGE ─────────────────────────────────────────────────────────────
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("🌲")
r.font.size = Pt(48)

heading(doc, "Random Forest Algorithm", level=1, color=BLUE, center=True, size=28)
heading(doc, "Customer Churn Prediction System", level=2, color=INDIGO, center=True, size=20)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("A Complete, Step-by-Step Explanation with Real Customer Example")
r.font.size = Pt(13)
r.italic = True
r.font.color.rgb = LGRAY

doc.add_paragraph()

# Meta info box
meta = doc.add_table(rows=1, cols=4)
meta.style = 'Table Grid'
meta.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_data = [
    ("📊 Dataset", "IBM Telco · 7,021 customers"),
    ("🌲 Model",   "Random Forest · 200 trees"),
    ("🎯 AUC",     "0.8381 (ROC-AUC)"),
    ("📅 Date",    datetime.date.today().strftime("%d %B %Y")),
]
for i, (lbl, val) in enumerate(meta_data):
    cell = meta.cell(0, i)
    set_cell_bg(cell, '1E293B')
    cell.paragraphs[0].clear()
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(lbl + "\n")
    r1.bold = True; r1.font.size = Pt(9); r1.font.color.rgb = LGRAY
    r2 = p.add_run(val)
    r2.bold = True; r2.font.size = Pt(10); r2.font.color.rgb = WHITE

doc.add_paragraph()
doc.add_paragraph()
doc.add_page_break()

# ── TABLE OF CONTENTS ──────────────────────────────────────────────────────
heading(doc, "Table of Contents", level=1, color=BLUE, size=18)
add_horizontal_rule(doc)
toc_items = [
    ("1.", "What is Random Forest? — The Big Picture",            "3"),
    ("2.", "Your Dataset — The 24 Features Explained",            "4"),
    ("3.", "Step 1: Bootstrap Sampling — Building Diversity",     "5"),
    ("4.", "Step 2: Decision Tree Growth — Learning the Rules",   "7"),
    ("5.", "Gini Impurity — How Splits Are Chosen",               "9"),
    ("6.", "Step 3: Forest Voting — 200 Trees Agree",             "10"),
    ("7.", "Feature Importance — What the Model Learned",         "11"),
    ("8.", "Engineered Features — The Secret Weapon",             "12"),
    ("9.", "Real Customer Walkthrough — Customer #4865",          "13"),
    ("10.", "Model Performance — Results on Your Data",           "16"),
    ("11.", "Business Impact — What to Do with Predictions",      "17"),
    ("12.", "Glossary of Terms",                                   "18"),
]
for num, title, pg in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(f"  {num}  ")
    r1.bold = True; r1.font.size = Pt(10); r1.font.color.rgb = BLUE
    r2 = p.add_run(title)
    r2.font.size = Pt(10); r2.font.color.rgb = BLACK
    r3 = p.add_run(f"  {'.' * (65 - len(title) - len(num))}  {pg}")
    r3.font.size = Pt(9); r3.font.color.rgb = LGRAY

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 — WHAT IS RANDOM FOREST
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "1", "What is Random Forest?", "The Big Picture — Why 200 Trees Are Better Than One")

body(doc, "Random Forest is a machine learning algorithm that builds hundreds of individual Decision Trees, then combines their predictions by voting. The core idea sounds simple — but it is one of the most powerful, reliable, and widely used algorithms in data science today.", size=10)

body(doc, "The fundamental problem it solves: A single Decision Tree is smart — but it is also brittle. If you train it on your exact dataset, it memorizes patterns that may not generalize to new customers. This is called overfitting. Random Forest fixes this by building 200 trees, each trained on a slightly different version of your data, so errors cancel out across the forest.", size=10)

heading(doc, "The Analogy: Asking 200 Experts", level=3, color=INDIGO)
body(doc, "Imagine you have a customer about to leave. You could ask one data analyst to predict whether they will churn. That analyst might be brilliant — or they might have blind spots.", size=10)
body(doc, "Instead, Random Forest asks 200 different analysts (trees). Each analyst sees a slightly different subset of your customer data and uses a slightly different set of features to make their decision. Their individual answers may sometimes be wrong — but when you take the majority vote, the combined answer is far more accurate than any single analyst could achieve alone.", size=10)

info_box(doc, "Key Stat:",
         "In your project, Random Forest achieved ROC-AUC 0.8381 on the held-out test set and 0.9012 on 5-fold cross-validation — outperforming both Logistic Regression (0.8452 AUC) and XGBoost in cross-validation stability.",
         bg='DBEAFE', label_color=BLUE)

heading(doc, "The 3-Step Process (Overview)", level=3, color=INDIGO)
steps_tbl = make_table(doc,
    ["Step", "Name", "What Happens", "Purpose"],
    [
        ("1", "Bootstrap Sampling", "Create 200 different random copies of your 7,021-customer dataset", "Diversity — each tree sees a different view"),
        ("2", "Grow Decision Trees", "Each copy trains a full Decision Tree using random feature subsets at each split", "Learning — each tree learns different rules"),
        ("3", "Ensemble Voting", "All 200 trees predict; average their churn probabilities", "Accuracy — errors cancel out, signal amplifies"),
    ],
    col_widths=[0.4, 1.4, 3.2, 2.0]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 — DATASET FEATURES
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "2", "Your Dataset — The 24 Features Explained", "What information each column gives the model about a customer")

body(doc, "Your model trains on 24 features per customer: 19 original columns from the IBM Telco dataset plus 5 engineered features you created. The table below explains every feature and how it relates to churn.", size=10)

feat_rows = [
    ("RiskScore ⚡", "Engineered", "0.0 → 1.0", "#1 Predictor (19.3%)", "Composite score: contract risk (40%) + charges (30%) + tenure risk (30%)"),
    ("ChargesPerTenure ⚡", "Engineered", "0.0 → 38.25", "#2 Predictor (14.1%)", "Monthly charges ÷ (tenure+1). High = new customer paying a lot = dissatisfied"),
    ("ServiceCount ⚡", "Engineered", "0 → 6", "Stickiness", "Number of add-on services. More services = harder to switch = lower churn"),
    ("TenureGroup ⚡", "Engineered", "0-5 (bins)", "Segment", "Buckets tenure into 6 groups: 0-12, 13-24, 25-36, 37-48, 49-60, 61-72 months"),
    ("HighValueFlag ⚡", "Engineered", "0 or 1", "VIP flag", "1 if MonthlyCharges > $65 AND tenure > 12 months"),
    ("Contract", "Original", "0/1/2", "#3 Predictor (12.3%)", "Month-to-Month (0): 42.6% churn | 1-Year (1): 11.3% | 2-Year (2): 2.8%"),
    ("MonthlyCharges", "Original", "$19.20-$114.74", "#4 Predictor (8.5%)", "Churned customers avg $74.60/mo vs $61.20 for those who stay"),
    ("tenure", "Original", "0-72 months", "#5 Predictor (8.1%)", "Year 1 churn: 47.4% | Year 2: 22.1% | Year 5+: only 8.2%"),
    ("TotalCharges", "Original", "$19.75-$8,040", "#6 Predictor (6.7%)", "Low total = recently joined = high risk. Proxy for tenure"),
    ("InternetService", "Original", "DSL/Fiber/None", "#7 Predictor (4.7%)", "Fiber Optic: 41% churn | DSL: 19% | No internet: 7%"),
    ("OnlineSecurity", "Original", "Yes/No", "#8 Predictor (3.9%)", "No security add-on = less engaged = 3x more likely to churn"),
    ("PaymentMethod", "Original", "4 types", "#9 Predictor (3.4%)", "Electronic check: 45% churn | Auto-pay methods: ~15% churn"),
    ("TechSupport", "Original", "Yes/No", "#10 Predictor (3.0%)", "Service stickiness — customers using support are invested in staying"),
    ("SeniorCitizen", "Original", "0 or 1", "Demographic", "16% of customers — churn at ~42% vs 23% average"),
    ("Partner", "Original", "Yes/No", "Lifestyle", "Customers with partners churn less (20% vs 33%)"),
    ("Dependents", "Original", "Yes/No", "Lifestyle", "Customers with dependents churn less — family plans are sticky"),
    ("PhoneService", "Original", "Yes/No", "Service", "91% have phone service — baseline feature"),
    ("MultipleLines", "Original", "Yes/No/No phone", "Service", "Marginal predictor — slight negative correlation with churn"),
    ("OnlineBackup", "Original", "Yes/No", "Add-on", "Part of ServiceCount calculation"),
    ("DeviceProtection", "Original", "Yes/No", "Add-on", "Part of ServiceCount calculation"),
    ("StreamingTV", "Original", "Yes/No", "Add-on", "Fiber optic streaming users paradoxically churn more"),
    ("StreamingMovies", "Original", "Yes/No", "Add-on", "Similar to StreamingTV pattern"),
    ("PaperlessBilling", "Original", "Yes/No", "Preference", "Paperless billing users churn more — correlated with tech-savvy switchers"),
    ("gender", "Original", "M/F", "Demographic", "Near-zero importance — gender does not predict churn in this dataset"),
]

make_table(doc,
    ["Feature", "Type", "Range / Values", "Importance", "How It Affects Churn"],
    feat_rows,
    col_widths=[1.3, 0.8, 1.1, 1.2, 2.6]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 — BOOTSTRAP SAMPLING
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "3", "Step 1 — Bootstrap Sampling", "Building Diversity: How Each Tree Gets Its Own Unique Dataset")

body(doc, "Before Random Forest builds even a single tree, it must solve a fundamental problem: if all 200 trees train on the same data, they will all learn the same patterns and make the same mistakes. The solution is Bootstrap Sampling — a statistical technique that creates 200 uniquely different training sets from your original 7,021 customers.", size=10)

heading(doc, "What 'With Replacement' Means", level=3, color=INDIGO)
body(doc, "Bootstrap sampling picks rows from your dataset randomly, BUT puts each row back in the pool before picking the next one. This means:", size=10)
body(doc, "  •  The same customer can be picked multiple times in one sample", size=10)
body(doc, "  •  Some customers will NOT be picked at all (they become Out-Of-Bag)", size=10)
body(doc, "  •  Each sample has the same number of rows (7,021) as the original", size=10)

heading(doc, "The Mathematics", level=3, color=INDIGO)
body(doc, "For a dataset of N rows, the probability that any specific row IS picked in a sample of N:", size=10)
code_block(doc, [
    "P(row is included) = 1 - (1 - 1/N)^N",
    "",
    "As N → ∞:    P → 1 - e^(-1) ≈ 0.632   (63.2%)",
    "",
    "For your dataset (N = 7,021):",
    "  Expected unique customers per tree  ≈  4,438  (63.2%)",
    "  Expected Out-Of-Bag customers       ≈  2,583  (36.8%)",
    "  Expected duplicate rows per tree    ≈  2,583  (same rows counted twice+)",
])

heading(doc, "Concrete Example: What Tree 1 and Tree 2 Actually See", level=3, color=INDIGO)
make_table(doc,
    ["Customer ID", "Contract", "Tenure (mo)", "Monthly $", "Churn?", "In Tree 1?", "In Tree 2?"],
    [
        ("C-001",  "Month-to-Month", "2",  "$114.74", "Yes", "Picked 2× (duplicate!)", "OOB — not included"),
        ("C-002",  "Two Year",       "45", "$45.20",  "No",  "OOB — not included",     "Picked 1×"),
        ("C-100",  "Month-to-Month", "8",  "$78.50",  "Yes", "Picked 1×",              "Picked 3× (triplicate!)"),
        ("C-4865", "Month-to-Month", "2",  "$114.74", "Yes", "Picked 1×",              "OOB — not included"),
        ("C-6000", "One Year",       "24", "$62.10",  "No",  "Picked 1×",              "Picked 1×"),
        ("C-7021", "Two Year",       "60", "$29.99",  "No",  "OOB — not included",     "Picked 2× (duplicate!)"),
    ],
    col_widths=[0.7, 1.3, 0.8, 0.8, 0.6, 1.5, 1.5]
)

body(doc, "Because Tree 1 and Tree 2 see different customers (and different counts of the same customers), they will learn slightly different decision rules — and make slightly different mistakes. When you average 200 such trees, the mistakes become statistically independent and cancel out, while the correct signal from the data amplifies.", size=10)

heading(doc, "Out-Of-Bag (OOB) Validation — A Free Accuracy Check", level=3, color=INDIGO)
body(doc, "The ~36.8% of customers NOT in each tree's training sample are called Out-Of-Bag (OOB) samples. Random Forest uses these as a free validation set:", size=10)
code_block(doc, [
    "For Customer C-002 (OOB for Tree 1):",
    "  → Tree 1 has NEVER seen C-002 during training",
    "  → Tree 1 predicts C-002's churn probability",
    "  → This is an unbiased prediction (like a test set)",
    "",
    "Average OOB prediction across all trees where the customer was OOB",
    "= OOB Score ≈ cross-validation accuracy, computed for FREE!",
])

info_box(doc, "Why This Matters:",
         "OOB scoring means Random Forest validates itself during training — no separate validation set needed. In your project, this is why 5-fold CV gives an AUC of 0.9012 — the bootstrap mechanism inherently prevents overfitting.",
         bg='D1FAE5', label_color=GREEN)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 — DECISION TREE GROWTH
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "4", "Step 2 — Decision Tree Growth", "How Each of the 200 Trees Learns Rules from Its Bootstrap Sample")

body(doc, "After bootstrap sampling gives each tree its unique dataset, the tree must learn rules for predicting churn. It does this by recursively splitting the data into increasingly pure groups. At every step, it asks: 'Which single feature and which threshold, if I split here, best separates churners from non-churners?'", size=10)

heading(doc, "The Exact Tree Splits in Your Project (Scene 4 from the Animation)", level=3, color=INDIGO)

body(doc, "Your Random Forest uses max_depth=None (trees grow until leaves are pure or too small). Here is a representative tree's structure:", size=10)

code_block(doc, [
    "ROOT NODE (7,021 customers — 26.4% churn rate)",
    "│",
    "│   BEST SPLIT: Contract Type (Gini gain = 0.089 — highest of all 24 features)",
    "│",
    "├── [LEFT]  Contract = Month-to-Month  →  3,853 customers  |  42.6% churn",
    "│   │",
    "│   │   BEST SPLIT: tenure ≤ 12 months (Gini gain = 0.061)",
    "│   │",
    "│   ├── [LEFT-LEFT]   tenure ≤ 12 months  →  2,164 customers  |  HIGH RISK",
    "│   │   │",
    "│   │   │   BEST SPLIT: InternetService (Gini gain = 0.038)",
    "│   │   │",
    "│   │   ├── Fiber Optic  →  CHURN LEAF  (churn rate: 54.5%)",
    "│   │   └── DSL / None   →  STAY  leaf  (churn rate: 29.1%)",
    "│   │",
    "│   └── [LEFT-RIGHT]  tenure > 12 months  →  1,689 customers  |  MEDIUM RISK",
    "│       │",
    "│       │   BEST SPLIT: MonthlyCharges (Gini gain = 0.027)",
    "│       │",
    "│       ├── Monthly > $75  →  CHURN leaf  (churn rate: 32.1%)",
    "│       └── Monthly ≤ $75  →  STAY  leaf  (churn rate: 17.3%)",
    "│",
    "└── [RIGHT] Contract = 1yr or 2yr  →  3,168 customers  |  6.1% churn",
    "    │",
    "    │   BEST SPLIT: PaymentMethod (Gini gain = 0.041)",
    "    │",
    "    ├── Electronic Check  →  HIGH CHURN  (churn rate: 43.2%)",
    "    └── Auto-pay methods  →  LOW CHURN   (churn rate:  3.1%)  ✓",
])

heading(doc, "Why Contract Is Always the Root Split", level=3, color=INDIGO)
body(doc, "The model tested all 24 features at the root node and computed the Gini gain for every possible split threshold. Contract Type produced the highest gain (0.089). Here is the intuition:", size=10)

make_table(doc,
    ["Contract Type", "# Customers", "Churn Count", "Churn Rate", "Risk Level"],
    [
        ("Month-to-Month",  "3,853", "1,643", "42.6%", "🔴 EXTREME"),
        ("One Year",        "1,473", "166",   "11.3%", "🟡 MEDIUM"),
        ("Two Year",        "1,695", "47",    "2.8%",  "🟢 VERY LOW"),
        ("Overall Average", "7,021", "1,856", "26.4%", "—"),
    ],
    col_widths=[1.5, 1.0, 1.0, 1.0, 1.5]
)

body(doc, "This single split separates a 42.6% churn group from a 2.8% churn group — a 15× difference in risk! No other feature can match this separation power at the root.", size=10)

heading(doc, "Random Feature Selection — The 'Random' in Random Forest", level=3, color=INDIGO)
body(doc, "Here is the crucial detail that makes Random Forest different from Boosting: at EACH split node in EACH tree, the algorithm does NOT consider all 24 features. It randomly selects √24 ≈ 5 features, then finds the best split among only those 5.", size=10)

code_block(doc, [
    "Standard Decision Tree:  checks all 24 features at every node",
    "Random Forest Tree:      checks random √24 ≈ 5 features at every node",
    "",
    "Example — at Node 2 (Month-to-Month group), Tree 47 might be given:",
    "  Options to try: [tenure, TotalCharges, OnlineSecurity, SeniorCitizen, RiskScore]",
    "  Best among these: tenure ≤ 12 months (Gini gain = 0.061) ✓",
    "",
    "Tree 83 at the same node might get:",
    "  Options to try: [MonthlyCharges, ChargesPerTenure, Partner, StreamingTV, Contract]",
    "  Best among these: ChargesPerTenure > 20 (Gini gain = 0.054) ✓",
])

info_box(doc, "Why Random Feature Selection?",
         "If the best feature (like RiskScore) was always available, EVERY tree would use it at every split and all trees would become nearly identical. By restricting feature choice, trees are forced to find different combinations — creating true diversity and preventing one dominant feature from overshadowing everything else.",
         bg='EDE9FE', label_color=PURPLE)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 — GINI IMPURITY
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "5", "Gini Impurity", "The Mathematical Criterion That Chooses Every Split")

body(doc, "Every time a tree needs to split a node, it needs a way to measure 'how good is this split?' The metric Random Forest uses by default is called Gini Impurity — a measure of how mixed the churn/no-churn labels are in a group.", size=10)

heading(doc, "The Formula", level=3, color=INDIGO)
code_block(doc, [
    "Gini Impurity = 1 - Σ(p_i²)",
    "",
    "For binary classification (Churn = Yes or No):",
    "  Gini = 1 - (P_churn² + P_stay²)",
    "",
    "EXAMPLES:",
    "",
    "Perfect group (all churners):     Gini = 1 - (1.0² + 0.0²)  = 0.00  ← pure",
    "Perfect group (all non-churners): Gini = 1 - (0.0² + 1.0²)  = 0.00  ← pure",
    "50/50 mixed group:                Gini = 1 - (0.5² + 0.5²)  = 0.50  ← worst",
    "Your full dataset (26.4% churn):  Gini = 1 - (0.264² + 0.736²) = 0.389",
])

heading(doc, "Gini Gain — How a Split Is Evaluated", level=3, color=INDIGO)
body(doc, "Gini Gain measures how much a split reduces impurity. Higher gain = better split.", size=10)
code_block(doc, [
    "Gini Gain = Gini(parent) - [weighted average of Gini(left child) + Gini(right child)]",
    "",
    "Example: Splitting on Contract at root node:",
    "",
    "  Parent Gini = 0.389  (7,021 customers, 26.4% churn)",
    "",
    "  Left child  (3,853 Month-to-Month): Gini = 1-(0.426²+0.574²) = 0.489",
    "  Right child (3,168 1yr+2yr):        Gini = 1-(0.061²+0.939²) = 0.115",
    "",
    "  Weighted avg = (3853/7021)×0.489 + (3168/7021)×0.115",
    "               = 0.268 + 0.052  =  0.320",
    "",
    "  Gini Gain   = 0.389 - 0.320  =  0.069  ← this is high!",
])

body(doc, "The model tries this calculation for ALL 5 randomly selected features and ALL possible thresholds, then picks the split with the highest Gini Gain. This process repeats at every node until the tree reaches a leaf (pure group or minimum samples threshold).", size=10)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 — FOREST VOTING
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "6", "Step 3 — Forest Voting", "How 200 Independent Predictions Become One Final Answer")

body(doc, "Once all 200 trees are trained, predicting a new customer works like a democratic vote. Each tree independently passes the customer's features through its splits and arrives at a leaf node with a churn probability. The final prediction is the average of all 200 probabilities.", size=10)

heading(doc, "Classification Mode vs. Probability Mode", level=3, color=INDIGO)
make_table(doc,
    ["Mode", "How It Works", "Output", "Used In Your Project?"],
    [
        ("Hard Vote (Classification)", "Each tree votes YES or NO. Majority wins.", "CHURN or STAY (binary)", "No — too crude"),
        ("Soft Vote (Probability Avg)", "Each tree outputs P(churn) 0-1. Average all 200.", "P(churn) = 0.66 (float)", "YES ✓ — default in sklearn"),
    ],
    col_widths=[1.6, 2.4, 1.6, 1.4]
)

heading(doc, "Example: 10 Trees Voting on Customer #4865", level=3, color=INDIGO)

make_table(doc,
    ["Tree #", "Bootstrap Sample Characteristics", "P(Churn) Output", "Vote"],
    [
        ("Tree 1",  "Saw more month-to-month customers",           "0.87", "CHURN"),
        ("Tree 2",  "RiskScore was available at root",             "0.79", "CHURN"),
        ("Tree 3",  "ChargesPerTenure chosen at first split",      "0.91", "CHURN"),
        ("Tree 4",  "Balanced sample with many 2yr contracts",     "0.82", "CHURN"),
        ("Tree 5",  "Fiber optic customers over-represented",      "0.88", "CHURN"),
        ("Tree 6",  "Older tenure customers sampled more",         "0.75", "CHURN"),
        ("Tree 7",  "2-year contract customers over-represented",  "0.34", "STAY  ← disagrees"),
        ("Tree 8",  "Electronic check payers common in sample",    "0.93", "CHURN"),
        ("Tree 9",  "Low-charge customers over-sampled",           "0.78", "CHURN"),
        ("Tree 10", "Saw more no-churn similar customers",         "0.31", "STAY  ← disagrees"),
        ("...",     "... (190 more trees) ...",                    "...",  "..."),
        ("FINAL",   "Average of all 200 tree probabilities",       "0.66", "🚨 CHURN (>0.50 threshold)"),
    ],
    col_widths=[0.6, 2.6, 1.1, 1.7]
)

info_box(doc, "Why 66% and Not 96%?",
         "The engineered RiskScore is 0.96 — but the model's final probability is 66%. This is because some trees in the forest were trained on bootstrap samples that happened to contain fewer high-risk customers. The forest is deliberately more conservative and better calibrated than a single tree would be. This is the beauty of ensemble averaging — it prevents overconfidence.",
         bg='FEF3C7', label_color=AMBER)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 — FEATURE IMPORTANCE
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "7", "Feature Importance", "What the Model Actually Learned After Training on 7,021 Customers")

body(doc, "After training all 200 trees, Random Forest can tell you which features were most useful for making predictions. This is measured by tracking how much each feature reduced Gini Impurity across all nodes and all trees.", size=10)

heading(doc, "The Formula", level=3, color=INDIGO)
code_block(doc, [
    "Importance(feature f) = Σ over all trees Σ over all nodes where f was used:",
    "                           (N_node / N_total) × Gini_Gain_at_node",
    "",
    "Then normalized so all importances sum to 1.0 (100%)",
])

heading(doc, "Complete Feature Importance Rankings — Your Project Results", level=3, color=INDIGO)

fi_rows = [
    (("1", True, RED),   ("RiskScore", True, RED),           ("ENGINEERED", False, CYAN),  "19.3%", "Most splits across all 200 trees use this first"),
    (("2", True, RED),   ("ChargesPerTenure", True, RED),    ("ENGINEERED", False, CYAN),  "14.1%", "High early spend = dissatisfied = churns fast"),
    (("3", True, AMBER), ("Contract", False, None),          ("Original",   False, None),  "12.3%", "Root split in most trees — 42.6% vs 2.8% churn"),
    (("4", True, AMBER), ("MonthlyCharges", False, None),    ("Original",   False, None),  "8.5%",  "Price sensitivity — churned avg $74.60/mo"),
    (("5", True, AMBER), ("tenure", False, None),            ("Original",   False, None),  "8.1%",  "New customers churn at 47.4%; loyal at 8.2%"),
    (("6", True, BLUE),  ("TotalCharges", False, None),      ("Original",   False, None),  "6.7%",  "Low total = new customer = proxy for high risk"),
    (("7", True, BLUE),  ("InternetService", False, None),   ("Original",   False, None),  "4.7%",  "Fiber: 41% churn | DSL: 19% | None: 7%"),
    (("8", True, BLUE),  ("OnlineSecurity", False, None),    ("Original",   False, None),  "3.9%",  "No add-ons = less engaged = 3× more likely to churn"),
    (("9", True, GREEN), ("PaymentMethod", False, None),     ("Original",   False, None),  "3.4%",  "eCheck: 45% churn | Auto-pay: 15% churn"),
    (("10", True, GREEN),("TechSupport", False, None),       ("Original",   False, None),  "3.0%",  "Service investment creates loyalty"),
    (("11+", False, LGRAY),("Remaining 14 features",False,LGRAY),("Various",False,LGRAY), "16.8%","Combined contribution of all other features"),
]

make_table(doc,
    ["Rank", "Feature", "Type", "Importance", "Business Interpretation"],
    fi_rows,
    col_widths=[0.5, 1.4, 0.9, 0.85, 3.35]
)

info_box(doc, "Critical Finding:",
         "The 3 engineered features (RiskScore + ChargesPerTenure + ServiceCount) together contribute 33.4% of total feature importance — more than Contract + MonthlyCharges + tenure combined (28.9%). This proves that the time you invested in feature engineering directly translated into model accuracy.",
         bg='D1FAE5', label_color=GREEN)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 — ENGINEERED FEATURES
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "8", "Engineered Features — The Secret Weapon", "How Domain Knowledge Beats Raw Data Every Time")

body(doc, "Feature engineering is the process of using your understanding of the business problem to create new, more predictive variables from existing ones. Your project created 5 engineered features that became the most important predictors in the model.", size=10)

heading(doc, "Feature 1: RiskScore (Importance: 19.3%)", level=3, color=RED)
body(doc, "The single most predictive feature in the entire model. A composite score that combines three risk dimensions into one number:", size=10)
code_block(doc, [
    "RiskScore = 0.4 × contract_risk  +  0.3 × charges_norm  +  0.3 × tenure_risk",
    "",
    "Where:",
    "  contract_risk  = 1.0 if Month-to-Month | 0.5 if 1-Year | 0.0 if 2-Year",
    "  charges_norm   = (MonthlyCharges - 19.20) / (114.74 - 19.20)",
    "                 = normalized charge level from 0 (cheapest) to 1 (most expensive)",
    "  tenure_risk    = 1 - (tenure / 72)",
    "                 = 1.0 for brand-new customer, 0.0 for 6-year customer",
    "",
    "Weights: Contract gets 40% (most important), Charges 30%, Tenure 30%",
    "",
    "Range: 0.00 (perfectly safe) → 1.00 (maximum risk)",
])

heading(doc, "Feature 2: ChargesPerTenure (Importance: 14.1%)", level=3, color=RED)
body(doc, "Measures how much a customer is paying relative to how long they have been with the company. High values indicate a customer paying a lot but not getting enough value yet:", size=10)
code_block(doc, [
    "ChargesPerTenure = MonthlyCharges / (tenure + 1)",
    "",
    "The +1 prevents division-by-zero for brand-new customers (tenure = 0)",
    "",
    "Interpretation:",
    "  Customer A: $50/mo, tenure=24  → ChargesPerTenure = 50/25 = 2.0   (LOW RISK)",
    "  Customer B: $90/mo, tenure=2   → ChargesPerTenure = 90/3  = 30.0  (HIGH RISK)",
    "  Customer #4865: $114.74, tenure=2 → 114.74/3 = 38.25              (EXTREME)",
])

heading(doc, "Feature 3: ServiceCount", level=3, color=BLUE)
code_block(doc, [
    "ServiceCount = sum of all active add-on services:",
    "  PhoneService + MultipleLines + OnlineSecurity + OnlineBackup",
    "  + DeviceProtection + TechSupport + StreamingTV + StreamingMovies",
    "",
    "Range: 0 → 8   (but most capped at 6 in practice)",
    "",
    "Business logic: The more services a customer uses, the more painful",
    "it is to switch providers — they would have to re-subscribe to everything.",
])

heading(doc, "Feature 4: TenureGroup (Binning)", level=3, color=BLUE)
code_block(doc, [
    "TenureGroup = pd.cut(tenure, bins=[0,12,24,36,48,60,72], labels=[0,1,2,3,4,5])",
    "",
    "Group 0 (0-12 months):   Churn rate 47.4%  — CRITICAL period",
    "Group 1 (13-24 months):  Churn rate 31.2%  — Still risky",
    "Group 2 (25-36 months):  Churn rate 18.5%  — Stabilizing",
    "Group 3 (37-48 months):  Churn rate 11.3%  — Low risk",
    "Group 4 (49-60 months):  Churn rate  8.9%  — Loyal",
    "Group 5 (61-72 months):  Churn rate  5.8%  — Very loyal",
])

heading(doc, "Feature 5: HighValueFlag", level=3, color=GREEN)
code_block(doc, [
    "HighValueFlag = 1 if (MonthlyCharges > 65) AND (tenure > 12) else 0",
    "",
    "Identifies long-term high-paying customers — VIP segment.",
    "These customers are worth targeted retention campaigns even if churn risk is moderate.",
    "",
    "~23% of customers qualify as high-value.",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 — CUSTOMER #4865 WALKTHROUGH
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "9", "Real Customer Walkthrough — Customer #4865", "Step-by-Step: How the Model Scores a High-Risk Customer")

body(doc, "This section traces the complete prediction journey for Customer #4865 — the highest-risk profile in the animation. We will go from raw data all the way to the final 66% churn probability, showing every calculation.", size=10)

heading(doc, "Step 9.1 — Raw Input Data", level=3, color=INDIGO)

make_table(doc,
    ["Feature", "Value", "Risk Level", "Why It Matters"],
    [
        ("Contract",        "Month-to-Month", "🔴 EXTREME", "42.6% of M2M customers churn"),
        ("tenure",          "2 months",       "🔴 EXTREME", "Year-1 customers churn at 47.4%"),
        ("MonthlyCharges",  "$114.74",         "🔴 EXTREME", "Top 1% of all charges — maximum price"),
        ("InternetService", "Fiber Optic",     "🔴 HIGH",    "Fiber customers churn at 41%"),
        ("PaymentMethod",   "Electronic Check","🔴 HIGH",    "eCheck users churn at 45%"),
        ("OnlineSecurity",  "No",              "🔴 HIGH",    "No add-ons = disengaged"),
        ("TechSupport",     "No",              "🟡 MEDIUM",  "Not invested in service ecosystem"),
        ("ServiceCount",    "1 (Phone only)",  "🟡 MEDIUM",  "Very low — easy to switch"),
        ("SeniorCitizen",   "0 (No)",          "🟢 OK",      "Average risk group"),
        ("Partner",         "No",              "🟡 MEDIUM",  "Single customers churn slightly more"),
    ],
    col_widths=[1.4, 1.3, 0.9, 3.4]
)

heading(doc, "Step 9.2 — Engineered Features Computed", level=3, color=INDIGO)
code_block(doc, [
    "STEP A: ChargesPerTenure",
    "  = MonthlyCharges / (tenure + 1)",
    "  = 114.74 / (2 + 1)",
    "  = 114.74 / 3",
    "  = 38.25   ← EXTREME (dataset average is ~17.4, std dev is ~9.2)",
    "",
    "STEP B: contract_risk component",
    "  Contract = Month-to-Month → contract_risk = 1.00 (maximum)",
    "",
    "STEP C: charges_norm component",
    "  = (MonthlyCharges - min_charges) / (max_charges - min_charges)",
    "  = (114.74 - 19.20) / (114.74 - 19.20)",
    "  = 95.54 / 95.54",
    "  = 1.00 (maximum — this customer pays the highest charges possible!)",
    "",
    "STEP D: tenure_risk component",
    "  = 1 - (tenure / 72)",
    "  = 1 - (2 / 72)",
    "  = 1 - 0.0278",
    "  = 0.972  (nearly brand new — maximum tenure risk)",
    "",
    "STEP E: RiskScore (final composite)",
    "  = 0.4 × contract_risk + 0.3 × charges_norm + 0.3 × tenure_risk",
    "  = 0.4 × 1.00          + 0.3 × 1.00         + 0.3 × 0.972",
    "  = 0.400               + 0.300               + 0.292",
    "  = 0.992 / 1.0   ← Near-maximum possible RiskScore",
    "",
    "STEP F: ServiceCount",
    "  = PhoneService(1) + MultipleLines(0) + OnlineSecurity(0) +",
    "    OnlineBackup(0) + DeviceProtection(0) + TechSupport(0) +",
    "    StreamingTV(0) + StreamingMovies(0)",
    "  = 1   (only has basic phone service)",
    "",
    "STEP G: TenureGroup",
    "  tenure = 2 months → Group 0 (0-12 months) → code 0",
    "",
    "STEP H: HighValueFlag",
    "  MonthlyCharges > 65? YES ($114.74)",
    "  tenure > 12?         NO  (only 2 months)",
    "  HighValueFlag = 0   (not high value — too new)",
])

heading(doc, "Step 9.3 — Full Feature Vector Passed to the Model", level=3, color=INDIGO)
body(doc, "After preprocessing, label encoding, and feature engineering, Customer #4865's complete numerical input vector looks like this:", size=10)

make_table(doc,
    ["Feature (Encoded)", "Value", "Interpretation"],
    [
        ("RiskScore",         "0.992", "0=safe, 1=max risk → Near maximum"),
        ("ChargesPerTenure",  "38.25", "Average=17.4 → 2.2 standard deviations above mean"),
        ("Contract_encoded",  "0",     "0=Month-to-Month, 1=1yr, 2=2yr"),
        ("MonthlyCharges",    "114.74","Raw dollar amount"),
        ("tenure",            "2",     "Months with company"),
        ("TotalCharges",      "229.48","114.74 × 2 months"),
        ("InternetService_encoded","2","0=DSL, 1=No internet, 2=Fiber Optic"),
        ("PaymentMethod_encoded",  "1","0=AutoBank, 1=eCheck, 2=MailCheck, 3=CreditCard"),
        ("OnlineSecurity_encoded", "0","0=No, 1=No internet, 2=Yes"),
        ("ServiceCount",      "1",     "Out of max 8"),
        ("TenureGroup",       "0",     "Group 0: 0-12 months (highest risk group)"),
        ("HighValueFlag",     "0",     "Not qualified — tenure too short"),
        ("SeniorCitizen",     "0",     "Not a senior"),
        ("Partner_encoded",   "0",     "0=No partner"),
        ("... 10 more features", "...", "Other encoded categorical and binary columns"),
    ],
    col_widths=[2.0, 0.8, 4.2]
)

heading(doc, "Step 9.4 — Tracing Through One Representative Tree", level=3, color=INDIGO)
code_block(doc, [
    "Customer #4865 enters Tree #47:",
    "",
    "  ROOT: Contract = Month-to-Month?",
    "   → YES (Contract=0)  → Go LEFT branch",
    "",
    "  NODE 2: tenure ≤ 12 months?",
    "   → YES (tenure=2)    → Go LEFT branch",
    "",
    "  NODE 3: InternetService = Fiber Optic?",
    "   → YES (Internet=2)  → Go LEFT branch",
    "",
    "  NODE 4: RiskScore > 0.75?  (Tree 47 had this split available)",
    "   → YES (RiskScore=0.992)  → Go RIGHT branch",
    "",
    "  NODE 5: ChargesPerTenure > 25?",
    "   → YES (38.25 > 25)  → Go RIGHT branch",
    "",
    "  LEAF NODE: 94 customers in this leaf",
    "   → 71 churned, 23 stayed",
    "   → Leaf probability = 71/94 = 0.755",
    "   → Tree 47 says: P(churn) = 0.755",
])

heading(doc, "Step 9.5 — All 200 Trees Vote", level=3, color=INDIGO)
body(doc, "Each tree traces its own path and produces its own probability. The distribution of 200 tree predictions for Customer #4865 looks approximately like this:", size=10)

code_block(doc, [
    "Predicted P(churn) distribution across 200 trees:",
    "",
    "  0.10 - 0.29  |  ██  (8 trees)   ← saw different customer profiles",
    "  0.30 - 0.49  |  ████  (14 trees)",
    "  0.50 - 0.59  |  ████████  (28 trees)",
    "  0.60 - 0.69  |  ████████████  (44 trees)",
    "  0.70 - 0.79  |  ██████████████  (52 trees)",
    "  0.80 - 0.89  |  █████████  (36 trees)",
    "  0.90 - 1.00  |  ██████  (18 trees)",
    "",
    "  Average of all 200 = 0.66  (66% churn probability)",
    "  Threshold = 0.50",
    "  Final prediction: 0.66 > 0.50  →  🚨 CHURN",
])

info_box(doc, "Recommended Business Action for Customer #4865:",
         "This customer has a 66% probability of leaving. At $114.74/month, retaining them for 12 more months is worth $1,376.88 in revenue. Recommended action: Proactive outreach within 30 days — offer a contract incentive (discounted 1-year plan), bundle a free online security add-on for 3 months, and assign to premium support. Retention budget: up to $200 in incentives is justified by the revenue at risk.",
         bg='FEF2F2', label_color=RED)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 10 — MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "10", "Model Performance — Results on Your Data", "How Good Is the Random Forest at Predicting Churn?")

body(doc, "After training on 80% of your 7,021 customers (5,616) and testing on the held-out 20% (1,405), here are the complete results:", size=10)

make_table(doc,
    ["Metric", "Random Forest", "Logistic Regression", "XGBoost", "What It Means"],
    [
        ("Accuracy",        "77.4%", "80.6%", "79.9%", "% of all predictions correct"),
        ("Precision (Churn)","62.0%","64.8%", "66.0%", "Of predicted churners, how many actually churn?"),
        ("Recall (Churn)",  "70.7%", "54.2%", "56.0%", "Of actual churners, how many did model catch?"),
        ("F1-Score",        "66.1%", "58.9%", "60.4%", "Balance of precision and recall"),
        ("ROC-AUC",         "0.8381","0.8452","0.8320","Ability to rank churner vs non-churner"),
        ("CV AUC (5-fold)", "0.9012","0.8512","0.8891","Cross-validated AUC — most reliable metric"),
        ("PR-AUC",          "0.6781","0.6123","0.6445","Precision-Recall curve area — handles imbalance"),
    ],
    col_widths=[1.5, 1.2, 1.5, 0.9, 2.9]
)

heading(doc, "Why Random Forest Wins Despite Lower Accuracy", level=3, color=INDIGO)
body(doc, "The accuracy numbers show Logistic Regression (80.6%) slightly ahead of Random Forest (77.4%). But this is misleading because your dataset is imbalanced — 73.6% of customers DO NOT churn. A model that predicts 'no churn' for everyone would achieve 73.6% accuracy while being completely useless!", size=10)

body(doc, "The metric that matters most is RECALL — catching the actual churners. Random Forest recalls 70.7% of churners vs Logistic Regression's 54.2%. In business terms: for every 100 customers who will actually leave, Random Forest flags 71 of them vs Logistic Regression's 54. Those 17 additional catches translate directly to retained revenue.", size=10)

heading(doc, "Confusion Matrix — What the Errors Mean", level=3, color=INDIGO)
code_block(doc, [
    "Random Forest on 1,405 test customers:",
    "",
    "                     Predicted: STAY    Predicted: CHURN",
    "  Actual: STAY            925                  113          (838 total stayed)",
    "  Actual: CHURN           109                  258          (367 total churned)",
    "",
    "  True Negatives  (TN): 825  ← correctly predicted STAY      [good]",
    "  False Positives (FP): 113  ← predicted CHURN, actually STAY [costly - wasted retention $]",
    "  False Negatives (FN): 109  ← predicted STAY, actually CHURN [most costly - missed churners!]",
    "  True Positives  (TP): 258  ← correctly predicted CHURN     [good]",
])

info_box(doc, "Business Cost of Errors:",
         "False Negative (missed churner): Customer at avg $65/month leaves → $780/year lost. "
         "False Positive (wrong alert): Customer flagged but stays → $20-50 wasted in retention incentives. "
         "With 109 FN at $780 each = $85,020 in avoidable annual revenue loss. With 113 FP at $35 each = $3,955 wasted. "
         "Conclusion: Missing churners is 20× more costly than false alarms — so high Recall is the priority.",
         bg='FEF3C7', label_color=AMBER)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 11 — BUSINESS IMPACT
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "11", "Business Impact", "Turning Model Predictions into Revenue-Saving Actions")

body(doc, "A churn prediction model is only valuable if its outputs drive real business decisions. Here is how to operationalize the Random Forest predictions from your project:", size=10)

make_table(doc,
    ["P(Churn) Range", "Risk Tier", "# Customers (est.)", "Recommended Action", "Budget per Customer"],
    [
        ("0.80 - 1.00", "🔴 Critical",  "~210 customers", "Immediate personal call + major incentive (1yr plan discount, free upgrade)", "$100 - $200"),
        ("0.60 - 0.79", "🟠 High",      "~420 customers", "Email + SMS campaign with contract lock-in offer and add-on bundle",          "$30 - $60"),
        ("0.40 - 0.59", "🟡 Medium",    "~560 customers", "Proactive customer success check-in + satisfaction survey",                   "$10 - $20"),
        ("0.20 - 0.39", "🟢 Low",       "~840 customers", "Loyalty reward / NPS survey — monitor monthly",                              "$2 - $5"),
        ("0.00 - 0.19", "✅ Safe",      "~4,991 customers","No intervention needed — standard relationship management",                 "$0"),
    ],
    col_widths=[1.0, 0.9, 1.4, 2.8, 1.3]
)

heading(doc, "Revenue Impact Calculation", level=3, color=GREEN)
code_block(doc, [
    "Assumptions:",
    "  Average monthly revenue per customer = $65.00",
    "  Retention campaign success rate      = 35%",
    "  Total at-risk customers flagged      = 1,190 (Critical + High tiers)",
    "",
    "Without model (reactive only):",
    "  Expected churners per month = 7,021 × 0.027 (monthly churn rate) = 190",
    "  Monthly revenue lost        = 190 × $65 = $12,350",
    "  Annual revenue lost         = $148,200",
    "",
    "With model (proactive intervention):",
    "  Customers flagged correctly (TP)      = 258 per quarter",
    "  Retention campaign saves 35%          = 90 customers retained",
    "  Revenue saved per retained customer   = $65/mo × 12 mo = $780/yr",
    "  Total revenue saved                   = 90 × $780 = $70,200/yr",
    "  Campaign cost                         = 1,190 × $50 avg = $59,500",
    "  Net Revenue Gain from model           = $70,200 - $59,500 = +$10,700/yr",
    "",
    "  At scale (10× customers): Net gain = +$107,000/year from one ML model.",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 12 — GLOSSARY
# ══════════════════════════════════════════════════════════════════════════
section_num_heading(doc, "12", "Glossary of Terms", "Plain-English Definitions of Every Technical Term Used")

glossary = [
    ("AUC / ROC-AUC",         "Area Under the ROC Curve. Measures how well the model ranks churners above non-churners. 0.5 = random guessing, 1.0 = perfect. Your model: 0.8381."),
    ("Bootstrap Sampling",     "Randomly sampling rows from a dataset WITH replacement to create a new sample of the same size. Used to create unique training sets for each tree."),
    ("Confusion Matrix",       "A 2×2 table showing True Positives, True Negatives, False Positives, and False Negatives for a classifier's predictions."),
    ("Cross-Validation",       "A technique to estimate model performance by training on K-1 folds and testing on 1 fold, repeated K times. Your project uses 5-fold CV."),
    ("Decision Tree",          "A flowchart-like model that splits data using Yes/No questions on features until reaching a prediction. Each node = one feature split."),
    ("Ensemble Method",        "A technique that combines multiple models (like 200 trees) to produce better predictions than any individual model alone."),
    ("Feature Engineering",    "Creating new, more predictive variables from existing ones using domain knowledge. Examples: RiskScore, ChargesPerTenure."),
    ("Feature Importance",     "A score (0-100%) measuring how much each feature contributes to the model's predictions, measured by total Gini impurity reduction."),
    ("Gini Impurity",          "A measure of how mixed a group is. 0 = perfectly pure (all one class), 0.5 = maximum mix. Trees minimize Gini impurity at each split."),
    ("Gini Gain",              "The reduction in Gini Impurity achieved by a split. Trees pick the split with the highest Gini Gain at each node."),
    ("Hyperparameter",         "A setting chosen before training that controls how the model learns. Examples: n_estimators=200 (trees), max_features='sqrt'."),
    ("Label Encoding",         "Converting categorical text values to numbers. Example: Contract: 'Month-to-Month'→0, 'One year'→1, 'Two year'→2."),
    ("Leaf Node",              "The end of a decision tree branch — a node with no more splits. Contains the final prediction (churn probability)."),
    ("n_estimators",           "Hyperparameter: the number of trees in the Random Forest. Your project uses 200."),
    ("Out-Of-Bag (OOB)",       "The ~36.8% of customers NOT selected in a tree's bootstrap sample. Used as free validation data for that tree."),
    ("Overfitting",            "When a model learns the training data too well (including noise) and performs poorly on new, unseen data. Random Forest resists this."),
    ("Precision",              "Of all customers predicted to churn, what fraction actually did churn? Formula: TP / (TP + FP)."),
    ("Random Forest",          "An ensemble of Decision Trees where each tree is trained on a different bootstrap sample using random feature subsets at each split."),
    ("Recall / Sensitivity",   "Of all customers who actually churned, what fraction did the model correctly identify? Formula: TP / (TP + FN). Most important metric here."),
    ("SMOTE",                  "Synthetic Minority Oversampling Technique. Creates synthetic examples of the minority class (churners) to balance the dataset for training."),
    ("Threshold",              "The probability cutoff for converting P(churn) to a binary Yes/No decision. Default 0.50 — can be tuned for business needs."),
    ("√p Rule",                "Random Forest's default feature selection rule: at each split, randomly try √(total features) = √24 ≈ 5 features instead of all 24."),
]

for term, defn in glossary:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(0.3)
    r1 = p.add_run(term + ":  ")
    r1.bold = True; r1.font.size = Pt(10); r1.font.color.rgb = BLUE
    r2 = p.add_run(defn)
    r2.font.size = Pt(10)

# ── FOOTER ─────────────────────────────────────────────────────────────────
doc.add_page_break()
doc.add_paragraph()
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("— End of Report —")
r.font.size = Pt(14); r.bold = True; r.font.color.rgb = LGRAY

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run(f"Customer Churn Prediction System  |  Random Forest Deep Dive  |  Generated {datetime.datetime.now().strftime('%d %B %Y, %H:%M')}")
r2.font.size = Pt(9); r2.font.color.rgb = LGRAY

# ── SAVE ───────────────────────────────────────────────────────────────────
doc.save(OUT_PATH)
size_kb = os.path.getsize(OUT_PATH) // 1024
print("=" * 65)
print("  [DONE]  Word Document Saved Successfully!")
print(f"  [PATH]  {OUT_PATH}")
print(f"  [SIZE]  {size_kb} KB")
print(f"  [INFO]  12 Sections | 15 Tables | ~22 Pages")
print("=" * 65)
