# API Contract — backend (Rishi) ↔ frontend (Harshavi)

**Version: 0.2 (ready to freeze as 1.0 — both review tonight).**
Any change: edit this file, bump the version, add a line in `docs/decisions.md`, tell the other person.

Base URL during development: `http://localhost:8000`. All responses are JSON.
Backend must allow CORS from `http://localhost:5173` (Vite's default dev address).

Mock files for building the frontend before the backend is ready:
- `contracts/mock-schema.json`: the real `/api/schema` shape with the real 52 features. It is
  generated from `backend/src/config.py` (`python src/config.py`), so never edit it by hand.
- `contracts/mock-predict-response.json`: a full `/api/predict` response.

**Fields marked *(optional)* may be missing or `null`.** The frontend must still work without them
(hide that piece of UI). Everything else is always present.

---

## Shared constants (both sides use exactly these)

### Targets
| Key | Meaning | Shown on 3D? |
|---|---|---|
| `CAD` | Overall coronary artery disease | No — shown as the overall risk card (optionally a whole-heart glow) |
| `LAD` | Left Anterior Descending stenosis | Yes → object named `LAD` |
| `LCX` | Left Circumflex stenosis | Yes → object named `LCX` |
| `RCA` | Right Coronary Artery stenosis | Yes → object named `RCA` |

The vessel list comes from the API (`vessels` in `/api/schema`), so a new vessel can be added
without rewriting the frontend.

### Checkup steps
The inputs are split into 5 steps that follow a real hospital visit. **Steps are cumulative:** the
step-3 model uses the inputs from steps 1, 2 and 3. The UI shows a step bar, and predicting "at step k"
means using only what is known by then.

| `stage` | `key` (= feature `group`) | Label | New inputs | Total inputs |
|---|---|---|---|---|
| 1 | `history` | History | 15 | 15 |
| 2 | `exam` | Exam & symptoms | 13 | 28 |
| 3 | `ecg` | ECG | 7 | 35 |
| 4 | `labs` | Blood tests | 14 | 49 |
| 5 | `echo` | Echo | 3 | 52 |

### Risk bands & colors
| Band | Probability | Color | Label |
|---|---|---|---|
| `low` | < 0.33 | `#2E9E6A` (green) | Low |
| `moderate` | 0.33 – 0.66 | `#E3A008` (amber) | Moderate |
| `high` | > 0.66 | `#D64545` (red) | High |

Frontend may draw a smooth gradient between these, but must always also show the % and band label.
The backend returns `band` so both sides agree on the cut-offs.

### Input features (52)
Defaults are the dataset median (numbers) or most common value. **`options` are the exact values
the model expects**, so send them back unchanged. Show `option_labels` to the user. For example,
`Sex` is sent as `"Fmale"` (the dataset's spelling) but displayed as "Female".

Not used as inputs: `Cath`, `LAD`, `LCX`, `RCA` (labels, so using them would be leakage);
`Weight`, `Length` (BMI already captures them); `Exertional CP` (same value for every patient).

| Step | `name` (exact) | Label | Type | Unit / options | Range | Default |
|---|---|---|---|---|---|---|
| 1 | `Age` | Age | numeric | years | 30–86 | 58 |
| 1 | `Sex` | Sex | categorical | `Male`, `Fmale` → Male, Female | | `Male` |
| 1 | `BMI` | Body mass index | numeric | kg/m² | 18–41 | 26.8 |
| 1 | `DM` | Diabetes | binary | `0`/`1` | | 0 |
| 1 | `HTN` | High blood pressure (hypertension) | binary | `0`/`1` | | 1 |
| 1 | `Current Smoker` | Current smoker | binary | `0`/`1` | | 0 |
| 1 | `EX-Smoker` | Ex-smoker | binary | `0`/`1` | | 0 |
| 1 | `FH` | Family history of heart disease | binary | `0`/`1` | | 0 |
| 1 | `Obesity` | Obesity | binary | `N`/`Y` | | `Y` |
| 1 | `CRF` | Chronic kidney failure | binary | `N`/`Y` | | `N` |
| 1 | `CVA` | Previous stroke | binary | `N`/`Y` | | `N` |
| 1 | `Airway disease` | Airway disease | binary | `N`/`Y` | | `N` |
| 1 | `Thyroid Disease` | Thyroid disease | binary | `N`/`Y` | | `N` |
| 1 | `CHF` | Congestive heart failure | binary | `N`/`Y` | | `N` |
| 1 | `DLP` | High blood fats (dyslipidemia) | binary | `N`/`Y` | | `N` |
| 2 | `BP` | Blood pressure | numeric | mmHg | 90–190 | 130 |
| 2 | `PR` | Pulse rate | numeric | beats/min | 50–110 | 70 |
| 2 | `Edema` | Swelling (edema) | binary | `0`/`1` | | 0 |
| 2 | `Weak Peripheral Pulse` | Weak pulse in limbs | binary | `N`/`Y` | | `N` |
| 2 | `Lung rales` | Crackles in lungs (rales) | binary | `N`/`Y` | | `N` |
| 2 | `Systolic Murmur` | Systolic heart murmur | binary | `N`/`Y` | | `N` |
| 2 | `Diastolic Murmur` | Diastolic heart murmur | binary | `N`/`Y` | | `N` |
| 2 | `Typical Chest Pain` | Typical chest pain | binary | `0`/`1` | | 1 |
| 2 | `Dyspnea` | Shortness of breath | binary | `N`/`Y` | | `N` |
| 2 | `Function Class` | Functional class (symptom limits) | categorical | `0`–`3` | | 0 |
| 2 | `Atypical` | Atypical chest pain | binary | `N`/`Y` | | `N` |
| 2 | `Nonanginal` | Non-anginal chest pain | binary | `N`/`Y` | | `N` |
| 2 | `LowTH Ang` | Low-threshold angina | binary | `N`/`Y` | | `N` |
| 3 | `Q Wave` | Q wave | binary | `0`/`1` | | 0 |
| 3 | `St Elevation` | ST elevation | binary | `0`/`1` | | 0 |
| 3 | `St Depression` | ST depression | binary | `0`/`1` | | 0 |
| 3 | `Tinversion` | T-wave inversion | binary | `0`/`1` | | 0 |
| 3 | `LVH` | Thickened heart wall (LVH) | binary | `N`/`Y` | | `N` |
| 3 | `Poor R Progression` | Poor R-wave progression | binary | `N`/`Y` | | `N` |
| 3 | `BBB` | Bundle branch block | categorical | `N`, `LBBB`, `RBBB` → None, Left, Right | | `N` |
| 4 | `FBS` | Fasting blood sugar | numeric | mg/dL | 62–400 | 98 |
| 4 | `CR` | Creatinine | numeric | mg/dL | 0.5–2.2 | 1.0 |
| 4 | `TG` | Triglycerides | numeric | mg/dL | 37–1050 | 122 |
| 4 | `LDL` | LDL cholesterol | numeric | mg/dL | 18–232 | 100 |
| 4 | `HDL` | HDL cholesterol | numeric | mg/dL | 15–111 | 39 |
| 4 | `BUN` | Blood urea nitrogen | numeric | mg/dL | 6–52 | 16 |
| 4 | `ESR` | ESR (inflammation marker) | numeric | mm/h | 1–90 | 15 |
| 4 | `HB` | Hemoglobin | numeric | g/dL | 8.9–17.6 | 13.2 |
| 4 | `K` | Potassium | numeric | mEq/L | 3.0–6.6 | 4.2 |
| 4 | `Na` | Sodium | numeric | mEq/L | 128–156 | 141 |
| 4 | `WBC` | White blood cells | numeric | cells/µL | 3700–18000 | 7100 |
| 4 | `Lymph` | Lymphocytes | numeric | % | 7–60 | 32 |
| 4 | `Neut` | Neutrophils | numeric | % | 32–89 | 60 |
| 4 | `PLT` | Platelets | numeric | ×1000/µL | 25–742 | 210 |
| 5 | `EF-TTE` | Ejection fraction (pumping strength) | numeric | % | 15–60 | 50 |
| 5 | `Region RWMA` | Regions with wall-motion abnormality | categorical | `0`–`4` | | 0 |
| 5 | `VHD` | Valve disease | categorical | `N`, `mild`, `Moderate`, `Severe` → None, Mild, Moderate, Severe | | `mild` |

`Region RWMA` is a model input only. It is **never drawn as a location on the heart**.

---

## Endpoints

### `GET /api/health`
`{ "status": "ok", "model_version": "2026-10-11-a" }`

### `GET /api/schema`
Everything the frontend needs to build the step bar, the input form and the 3D legend.
Full real example: `contracts/mock-schema.json`. Shape:
```json
{
  "model_version": "2026-10-11-a",
  "targets": ["CAD", "LAD", "LCX", "RCA"],
  "vessels": [
    {"key": "LAD", "name": "Left Anterior Descending", "supplies": "Front of the heart"}
  ],
  "stages": [
    {"stage": 1, "key": "history", "label": "History"}
  ],
  "features": [
    {"name": "Age", "label": "Age", "group": "history", "type": "numeric", "unit": "years",
     "min": 30, "max": 86, "step": 1, "default": 58},
    {"name": "Obesity", "label": "Obesity", "group": "history", "type": "binary",
     "options": ["N", "Y"], "option_labels": ["No", "Yes"], "default": "Y"}
  ],
  "risk_bands": [
    {"band": "low", "max": 0.33, "color": "#2E9E6A"},
    {"band": "moderate", "max": 0.66, "color": "#E3A008"},
    {"band": "high", "max": 1.0, "color": "#D64545"}
  ]
}
```
- `name` = exact column name the model expects. `label` = human-readable text for the UI.
- `group` = the `key` of the step the feature belongs to.
- `type` ∈ `numeric | binary | categorical`. Numeric has `unit/min/max/step`; the others have
  `options` + `option_labels`.

### `GET /api/samples`
A few example patients (no identifiers) for the demo "Load sample" button.
```json
{ "samples": [ { "id": "sample-1", "title": "High-risk example", "features": { "Age": 67, "DM": 1 } } ] }
```

### `POST /api/predict`
Request:
```json
{ "stage": 5, "features": { "Age": 63, "DM": 1, "Obesity": "Y", "Region RWMA": 0 } }
```
- `stage` *(optional, 1–5, default 5)*: which step model to use. Features from **later** steps are
  ignored.
- Missing features from steps ≤ `stage` → backend fills them with the default and lists them in `warnings`.

Response: see `contracts/mock-predict-response.json` for a full example. Shape:
```json
{
  "model_version": "string",
  "stage": 5,
  "predictions": {
    "CAD": {"probability": 0.0-1.0, "band": "low|moderate|high", "label": "string",
            "interval": [0.0-1.0, 0.0-1.0]},
    "LAD": {...}, "LCX": {...}, "RCA": {...}
  },
  "vessel_count": {
    "expected": 0.0-3.0,
    "distribution": [p0, p1, p2, p3],
    "method": "sum_of_vessels | count_model"
  },
  "consistency": {
    "max_vessel_probability": 0.0-1.0,
    "consistent": true,
    "note": "string"
  },
  "explanations": {
    "CAD": {
      "base_value": 0.0-1.0,
      "contributions": [
        {"feature": "Age", "label": "Age", "value": 63, "display_value": "63 years",
         "shap": 0.12, "direction": "increases"}
      ]
    },
    "LAD": {...}, "LCX": {...}, "RCA": {...}
  },
  "warnings": ["string"],
  "disclaimer": "string"
}
```
- `interval` *(optional)*: likely range `[low, high]` from the cross-validation models.
- `vessel_count` *(optional)*: estimated number of narrowed arteries (0–3). `expected` is always
  present when the object is. `distribution` (chance of 0/1/2/3) is only present when
  `method = "count_model"`. **Show as an estimate only; never suggest a treatment.**
- `consistency` *(optional)*: overall CAD means "at least one vessel narrowed", so the CAD %
  should not be lower than the highest vessel %. `consistent: false` → show a small "models disagree"
  note with `note` as the text.
- `contributions` sorted by absolute `shap`, largest first; backend returns the top 10 per target.
- `explanations` may be empty `{}` for early steps if SHAP is only computed for the final step.
- `shap` values are in **probability units** if possible (so base_value + sum ≈ probability);
  if they are in log-odds, add `"shap_units": "log_odds"` so the UI labels them correctly.
- `direction` ∈ `increases | decreases`.

### `GET /api/metrics`
Cross-validated evaluation results, for the "How good is this model?" panel. Each metric is `[mean, std]`.
```json
{
  "validation": "Repeated stratified 5-fold CV (10 repeats), n=303",
  "targets": {
    "CAD": {
      "model": "LogisticRegression",
      "accuracy": [0.87, 0.04], "precision": [0.9, 0.04], "recall": [0.92, 0.04],
      "f1": [0.91, 0.03], "roc_auc": [0.93, 0.03],
      "baseline_accuracy": 0.71,
      "brier": [0.11, 0.02],
      "calibration": [ {"predicted": 0.1, "observed": 0.08, "count": 40} ],
      "by_stage": [ {"stage": 1, "roc_auc": [0.74, 0.05]}, {"stage": 5, "roc_auc": [0.93, 0.03]} ]
    }
  },
  "vessel_count": {"model": "string", "accuracy": [0.45, 0.05], "macro_f1": [0.42, 0.05],
                   "baseline_accuracy": 0.29}
}
```
- Top-level metrics are for the full model (step 5).
- `brier`, `calibration`, `by_stage` *(optional)*: `calibration` is a list of bins (predicted
  vs. actually observed rate), computed on out-of-fold predictions. `by_stage` drives the "How much
  did each test add?" chart.
- `vessel_count` *(optional)*: only present if a dedicated count model exists.
- All numbers in the examples above are made up.

### `GET /api/global-importance`
Global feature importance per target (mean |SHAP|, full model), for the overview chart.
```json
{ "targets": { "CAD": [ {"feature": "Typical Chest Pain", "label": "Typical chest pain", "importance": 0.21} ] } }
```

---

## Errors
`{ "error": "message for humans", "detail": "optional technical detail" }` with HTTP 400 (bad input) or 500.
