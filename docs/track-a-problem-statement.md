# Track A: Cardiovascular Risk Visualization & Prediction
*(Copied from the official Multimodal AI Hackathon 2026 problem statement PDF. This is the source of truth.)*

## Challenge
Build an interactive 3D visualization system that predicts coronary artery disease and overall
cardiac risk from patient physiological and clinical data, mapping predictions onto an interactive
3D human anatomical model.

## Quick Medical Primer for Developers
- **Coronary Artery Disease (CAD) & Stenosis:** Coronary arteries supply blood to the heart muscle.
  Stenosis refers to narrowing of a coronary artery, typically caused by plaque buildup. In the
  provided dataset, CAD is associated with at least 50% narrowing of one or more of the major
  coronary vessels.
- **The Three Target Vessels:**
  - **LAD (Left Anterior Descending):** Supplies blood to the front of the heart.
  - **LCX (Left Circumflex):** Supplies blood to the side and back of the heart.
  - **RCA (Right Coronary Artery):** Supplies blood to the right side and bottom of the heart.
  - **ML Goal:** Train models to predict overall CAD status and the stenosis status of the LAD,
    LCX, and RCA using the available clinical features.
- **Overall CAD Status:** The dataset provides an overall CAD classification in addition to the
  individual vessel labels. A patient may have significant stenosis in one or more of the target
  vessels, while the overall CAD label represents the presence or absence of CAD according to the
  dataset definition.
- **Clinical and ECG Features:** demographic, clinical examination, laboratory, ECG, and
  echocardiographic features (age, blood pressure, pulse rate, cholesterol, cardiac enzymes,
  ST Elevation, T Inversion, LVH, Region with RWMA, …). These are inputs to the prediction models
  and **should not be treated as direct anatomical coordinates.**
- **Regional Wall Motion Abnormality (RWMA):** an echocardiographic finding indicating abnormal
  motion of a region of the heart wall. It can be used as a clinical feature by the model, but it
  **does not provide a direct pixel-level or 3D anatomical lesion map** in this dataset.

## Context
Cardiovascular disease remains a leading cause of death globally. While statistical algorithms can
generate risk percentages, raw numbers fail to give clinicians or patients an intuitive
understanding of where and how pathology is developing inside the body.

## Requirements
1. **Predictive Modeling**
   - a. Train classification models to predict overall CAD status.
   - b. Predict stenosis status for the LAD, LCX, and RCA.
   - c. Use demographic, clinical examination, ECG, laboratory, and echocardiographic features available in the dataset.
   - d. **Exclude LAD, LCX, RCA, and Cath from model input features** when predicting CAD or vessel-specific stenosis to prevent target leakage.
   - e. Evaluate predictions using appropriate classification metrics (**accuracy, precision, recall, F1-score, ROC-AUC**).
2. **3D Visual Mapping**
   - a. Render an interactive 3D human torso/heart model (Three.js, WebGL, React Three Fiber, or VTK.js).
   - b. Dynamically update the color-code of individual coronary artery nodes (LAD, LCX, RCA) based on predicted stenosis probabilities.
   - c. Allow users to rotate, zoom, and select anatomical regions to inspect localized/vessel-specific risk detail.
3. **Clinical Dashboard**
   - a. Display the predicted overall CAD status and vessel-specific stenosis probabilities alongside the 3D visualization canvas.
   - b. Provide an interpretable breakdown of why the model predicted a given risk score (e.g., SHAP values or LIME).
   - c. Display physiological measurements alongside their relative contribution to the overall prediction.
4. **3D models:** You may use open-source mesh anatomical files (.obj/.gltf) for rendering human anatomy.
5. **Clinical Safety Disclaimer:** The UI must include clear, visible visual disclaimers indicating
   that predictions are for decision support / educational purposes only and not a substitute for
   formal diagnostic imaging.

## Expected Deliverables
- **Working Software Prototype:** web-based application with the interactive 3D viewer integrated with the ML model backend.
- **Trained Prediction Pipeline:** clean code and model weights for cardiac risk and multi-vessel stenosis classification.
- **Clinical Explanation Dashboard:** prediction metrics, feature importances (SHAP/LIME), patient physiological breakdowns.
- **Project Documentation:** dataset preprocessing, model architecture, 3D pipeline setup, usage instructions, evaluation results (**max 6 pages**).
- **Demonstration Video:** **3–10 minute YouTube** video showing the working system, feature input workflow, 3D interactions, and technical implementation.

## Technical Considerations
- Responsive 3D interaction in modern browsers **without dedicated GPUs**.
- Architecture should support **adding clinical features, prediction models, or anatomical structures without a complete redesign**.
- Visualization must keep a **consistent correspondence** between model outputs and the displayed LAD, LCX, RCA structures.

## Evaluation Criteria
| Criterion | Weight | What judges look at |
|---|---|---|
| Predictive Performance | **30%** | Classification performance, risk estimation quality, validation methodology |
| 3D Visualization | **25%** | Anatomical representation, spatial risk mapping, interactive visualization |
| Clinical Interpretability | **20%** | Feature attribution quality, clarity of risk explanation, physiological factor breakdown |
| System Integration | **15%** | Data pipeline, model-dashboard integration, real-time visualization updates |
| Technical Implementation | **10%** | Architecture, code quality, reproducibility, use of public datasets and anatomical resources |

## Suggested Primary Dataset & Starter Resources
- **Primary dataset:** UCI Machine Learning Repository — *Extension of Z-Alizadeh Sani Dataset* (also on Kaggle).
  303 patient records with demographics, vital signs, lab values, echo findings. Ground-truth labels:
  LAD, LCX, RCA stenosis status + overall CAD.
- **3D meshes:** BodyParts3D (Database Center for Life Science); open-source .gltf/.glb/.obj heart
  models (Sketchfab, Three.js repositories, NIH 3D Print Exchange).
