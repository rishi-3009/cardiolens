"""One place for everything the model and the API agree on: targets, steps and input features.

/api/schema is built from this file, so the frontend form always matches the model.
Run this file to regenerate the frontend's mock schema:
    python src/config.py
"""
import json
from pathlib import Path

# ---- What we predict -------------------------------------------------------
TARGETS = ["CAD", "LAD", "LCX", "RCA"]

# Model target -> column in the dataset, and which value means "positive"
TARGET_COLUMNS = {
    "CAD": ("Cath", "CAD"),
    "LAD": ("LAD", "Stenotic"),
    "LCX": ("LCX", "Stenotic"),
    "RCA": ("RCA", "Stenotic"),
}

VESSELS = [
    {"key": "LAD", "name": "Left Anterior Descending", "supplies": "Front of the heart"},
    {"key": "LCX", "name": "Left Circumflex", "supplies": "Side and back of the heart"},
    {"key": "RCA", "name": "Right Coronary Artery", "supplies": "Right side and bottom of the heart"},
]

# Label columns. NEVER model inputs, for any target (no target leakage).
FORBIDDEN_INPUTS = ["Cath", "LAD", "LCX", "RCA"]

# Columns we deliberately leave out (see docs/decisions.md):
#   Weight, Length -> BMI is computed from them, so keeping all three splits SHAP credit
#   Exertional CP  -> "N" for every patient, tells the model nothing
DROPPED_COLUMNS = ["Weight", "Length", "Exertional CP"]

# ---- Checkup steps (Direction D) ---------------------------------------------
# Steps are cumulative: the step-3 model sees steps 1 + 2 + 3.
STAGES = [
    {"stage": 1, "key": "history", "label": "History"},
    {"stage": 2, "key": "exam", "label": "Exam & symptoms"},
    {"stage": 3, "key": "ecg", "label": "ECG"},
    {"stage": 4, "key": "labs", "label": "Blood tests"},
    {"stage": 5, "key": "echo", "label": "Echo"},
]

RISK_BANDS = [
    {"band": "low", "max": 0.33, "color": "#2E9E6A"},
    {"band": "moderate", "max": 0.66, "color": "#E3A008"},
    {"band": "high", "max": 1.0, "color": "#D64545"},
]


# ---- Input features ------------------------------------------------------------
# "options" are the exact values in the dataset (the model expects these);
# "option_labels" are what the UI shows. Defaults = median (numbers) or most common value.
def num(name, label, group, unit, lo, hi, step, default):
    return {"name": name, "label": label, "group": group, "type": "numeric", "unit": unit,
            "min": lo, "max": hi, "step": step, "default": default}


def yes_no(name, label, group, default="N"):
    """Dataset stores this as "N"/"Y"."""
    return {"name": name, "label": label, "group": group, "type": "binary",
            "options": ["N", "Y"], "option_labels": ["No", "Yes"], "default": default}


def zero_one(name, label, group, default=0):
    """Dataset stores this as 0/1."""
    return {"name": name, "label": label, "group": group, "type": "binary",
            "options": [0, 1], "option_labels": ["No", "Yes"], "default": default}


def choice(name, label, group, options, option_labels, default):
    return {"name": name, "label": label, "group": group, "type": "categorical",
            "options": options, "option_labels": option_labels, "default": default}


FEATURES = [
    # Step 1 - history
    num("Age", "Age", "history", "years", 30, 86, 1, 58),
    choice("Sex", "Sex", "history", ["Male", "Fmale"], ["Male", "Female"], "Male"),  # "Fmale" is the dataset's spelling
    num("BMI", "Body mass index", "history", "kg/m²", 18, 41, 0.1, 26.8),
    zero_one("DM", "Diabetes", "history"),
    zero_one("HTN", "High blood pressure (hypertension)", "history", default=1),
    zero_one("Current Smoker", "Current smoker", "history"),
    zero_one("EX-Smoker", "Ex-smoker", "history"),
    zero_one("FH", "Family history of heart disease", "history"),
    yes_no("Obesity", "Obesity", "history", default="Y"),
    yes_no("CRF", "Chronic kidney failure", "history"),
    yes_no("CVA", "Previous stroke", "history"),
    yes_no("Airway disease", "Airway disease", "history"),
    yes_no("Thyroid Disease", "Thyroid disease", "history"),
    yes_no("CHF", "Congestive heart failure", "history"),
    yes_no("DLP", "High blood fats (dyslipidemia)", "history"),
    # Step 2 - exam & symptoms
    num("BP", "Blood pressure", "exam", "mmHg", 90, 190, 1, 130),
    num("PR", "Pulse rate", "exam", "beats/min", 50, 110, 1, 70),
    zero_one("Edema", "Swelling (edema)", "exam"),
    yes_no("Weak Peripheral Pulse", "Weak pulse in limbs", "exam"),
    yes_no("Lung rales", "Crackles in lungs (rales)", "exam"),
    yes_no("Systolic Murmur", "Systolic heart murmur", "exam"),
    yes_no("Diastolic Murmur", "Diastolic heart murmur", "exam"),
    zero_one("Typical Chest Pain", "Typical chest pain", "exam", default=1),
    yes_no("Dyspnea", "Shortness of breath", "exam"),
    choice("Function Class", "Functional class (symptom limits)", "exam", [0, 1, 2, 3],
           ["0 - none", "1", "2", "3"], 0),
    yes_no("Atypical", "Atypical chest pain", "exam"),
    yes_no("Nonanginal", "Non-anginal chest pain", "exam"),
    yes_no("LowTH Ang", "Low-threshold angina", "exam"),
    # Step 3 - ECG
    zero_one("Q Wave", "Q wave", "ecg"),
    zero_one("St Elevation", "ST elevation", "ecg"),
    zero_one("St Depression", "ST depression", "ecg"),
    zero_one("Tinversion", "T-wave inversion", "ecg"),
    yes_no("LVH", "Thickened heart wall (LVH)", "ecg"),
    yes_no("Poor R Progression", "Poor R-wave progression", "ecg"),
    choice("BBB", "Bundle branch block", "ecg", ["N", "LBBB", "RBBB"], ["None", "Left", "Right"], "N"),
    # Step 4 - blood tests
    num("FBS", "Fasting blood sugar", "labs", "mg/dL", 62, 400, 1, 98),
    num("CR", "Creatinine", "labs", "mg/dL", 0.5, 2.2, 0.1, 1.0),
    num("TG", "Triglycerides", "labs", "mg/dL", 37, 1050, 1, 122),
    num("LDL", "LDL cholesterol", "labs", "mg/dL", 18, 232, 1, 100),
    num("HDL", "HDL cholesterol", "labs", "mg/dL", 15, 111, 1, 39),
    num("BUN", "Blood urea nitrogen", "labs", "mg/dL", 6, 52, 1, 16),
    num("ESR", "ESR (inflammation marker)", "labs", "mm/h", 1, 90, 1, 15),
    num("HB", "Hemoglobin", "labs", "g/dL", 8.9, 17.6, 0.1, 13.2),
    num("K", "Potassium", "labs", "mEq/L", 3.0, 6.6, 0.1, 4.2),
    num("Na", "Sodium", "labs", "mEq/L", 128, 156, 1, 141),
    num("WBC", "White blood cells", "labs", "cells/µL", 3700, 18000, 100, 7100),
    num("Lymph", "Lymphocytes", "labs", "%", 7, 60, 1, 32),
    num("Neut", "Neutrophils", "labs", "%", 32, 89, 1, 60),
    num("PLT", "Platelets", "labs", "×1000/µL", 25, 742, 1, 210),
    # Step 5 - echo
    num("EF-TTE", "Ejection fraction (pumping strength)", "echo", "%", 15, 60, 1, 50),
    choice("Region RWMA", "Regions with wall-motion abnormality", "echo", [0, 1, 2, 3, 4],
           ["0 - none", "1", "2", "3", "4"], 0),
    choice("VHD", "Valve disease", "echo", ["N", "mild", "Moderate", "Severe"],
           ["None", "Mild", "Moderate", "Severe"], "mild"),
]

FEATURE_NAMES = [f["name"] for f in FEATURES]

# Categorical features whose options have NO natural order -> one yes/no column per option.
# All other options are listed in a meaningful order (e.g. VHD none < mild < moderate < severe).
NOMINAL_FEATURES = ["BBB"]

# Safety checks: fail loudly if a label or dropped column ever sneaks into the inputs
assert not set(FEATURE_NAMES) & set(FORBIDDEN_INPUTS), "Label column used as an input!"
assert not set(FEATURE_NAMES) & set(DROPPED_COLUMNS), "Dropped column used as an input!"
assert {f["group"] for f in FEATURES} == {s["key"] for s in STAGES}, "Every feature needs a valid step"


def features_up_to(stage):
    """Input columns the step-`stage` model may use (steps are cumulative)."""
    keys = {s["key"] for s in STAGES if s["stage"] <= stage}
    return [f["name"] for f in FEATURES if f["group"] in keys]


def schema(model_version):
    """The /api/schema response."""
    return {
        "model_version": model_version,
        "targets": TARGETS,
        "vessels": VESSELS,
        "stages": STAGES,
        "features": FEATURES,
        "risk_bands": RISK_BANDS,
    }


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "contracts" / "mock-schema.json"
    out.write_text(json.dumps(schema("mock-0.2"), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(FEATURES)} features in {len(STAGES)} steps -> {out}")
    for s in STAGES:
        print(f"  step {s['stage']} {s['label']:<16} {len(features_up_to(s['stage'])):>2} inputs (cumulative)")
