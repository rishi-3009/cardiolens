# Rules & Gotchas — read before building

Each item says **why it matters** (which judging criterion it hits). `rules-checker` audits against this list.

## A. Machine learning (Predictive Performance 30%)

1. **Target leakage — the #1 way to lose credibility.**
   - LAD, LCX, RCA, Cath, and the overall CAD label are **never** model inputs — not for any target.
     When predicting LAD, the other vessels are also forbidden.
   - The UCI page itself warns that only one of these label columns may stay in the data for a
     given classification; the others must be removed.
   - Check: list the exact input columns in code and assert none of the label columns are in it.
2. **Preprocessing inside cross-validation.** Scaling, imputation, one-hot encoding, SMOTE, feature
   selection — all must be fitted inside each training fold (use a scikit-learn `Pipeline`).
   Fitting a scaler on all 303 rows first is a quiet form of leakage.
3. **Tiny dataset (303 rows).** A single 80/20 split gives noisy numbers. Use **repeated stratified
   k-fold** (e.g. 5 folds × 10 repeats) and report **mean ± std**. If you tune hyperparameters,
   use nested CV or a held-out test set that is touched once.
4. **Class imbalance**, especially for LCX and RCA. Accuracy alone is misleading — report
   precision, recall, F1, ROC-AUC (all required), and consider PR-AUC. Use `class_weight="balanced"`
   or similar, and compare against a trivial baseline ("always predict majority").
5. **Probabilities drive the 3D colors**, so they should mean something. Check calibration
   (calibration curve / Brier score). A model that outputs 0.51 for everyone colors everything amber.
6. **Overall CAD vs vessels.** By the dataset definition, CAD means at least one vessel is stenotic.
   Independent models may disagree (e.g. CAD 20% but LAD 70%). Decide how to handle and explain it
   (document in `docs/decisions.md`). Inspect the data to confirm which column is the overall label.
7. **Inspect the actual values** before coding: label values may be text (e.g. "Stenotic"/"Normal",
   "Cad"/"Normal") and many features are "Y"/"N" strings. Encode deliberately, write it down.
8. **Reproducibility:** fixed random seeds, `requirements.txt` with versions, a single command that
   retrains and saves weights (`python -m src.train`), saved metrics JSON committed to the repo.

## B. 3D visualization (25%)

9. **Exact correspondence:** one mapping, in the contract, from model output key (`LAD`, `LCX`, `RCA`)
   to the mesh/object name. Test it: set LAD=0.9, others=0.1 → only LAD turns red.
10. **No dedicated GPU required.** Keep the heart mesh light (aim < 10 MB, < ~300k triangles),
    compress with Draco or meshopt if needed, avoid heavy post-processing.
11. **Region with RWMA is NOT a location.** Do not paint wall regions based on it.
12. **Color is not the only signal**: also show the % and label on selection/hover (color-blind users,
    projector demos).
13. **Rotate, zoom, select** must all work (OrbitControls + click/hover on each vessel).

## C. Interpretability (20%)

14. SHAP explanations **per patient** (local) AND **global** feature importance.
15. Show the patient's actual measured value next to each feature's contribution
    ("Age = 63 → +0.12 toward CAD"). Use human-readable feature names and units.
16. Explain direction in plain words: "raised the risk" / "lowered the risk".

## D. Integration (15%) & Technical implementation (10%)

17. Real-time updates: change an input → new prediction → 3D colors and charts update.
18. Extensibility (explicitly asked): the frontend builds the input form from `/api/schema`, and
    vessels are a list, not hard-coded in five places. Adding a feature or a vessel = config change.
19. Clean repo: README, `requirements.txt`, `package.json`, `.gitignore`, no secrets, no
    `node_modules`, no 100 MB files.

## E. Submission & conduct

20. **Clinical disclaimer** visible in the UI at all times (banner or footer), plus in README and video.
21. **AI-use disclosure:** Devpost "Built With" lists Claude Code; README has an "AI assistance" section.
22. **Credits:** dataset citation (CC BY 4.0), mesh source + license, libraries.
23. Video: 3–10 min, YouTube **unlisted** (not private), English.
24. Both teammates added on Devpost with real full names.
25. Documentation **max 6 pages**.
