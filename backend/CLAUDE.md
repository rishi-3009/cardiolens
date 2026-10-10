# Backend — ML models + API (owner: Rishi)

Loaded automatically when Claude Code works inside `backend/`. Root `CLAUDE.md` rules still apply.

## Goal
Train leakage-safe classifiers for **CAD, LAD, LCX, RCA**, explain them with **SHAP**, and serve
everything through **FastAPI** exactly as described in `../contracts/api-contract.md`.

## Suggested layout (create as you go — explain each file to Rishi)
```
backend/
  data/raw/            # original .xlsx — never edited
  data/processed/      # cleaned CSV (generated, can be re-created)
  src/
    config.py          # target list, forbidden columns, feature metadata (labels, units, groups)
    data.py            # load + clean + encode
    train.py           # CV evaluation + fit final models + save artifacts   (python -m src.train)
    explain.py         # SHAP explainers
    api.py             # FastAPI app                                         (uvicorn src.api:app --reload)
  models/              # saved pipelines (*.joblib) + metrics.json + global_importance.json
  notebooks/           # optional exploration only — final logic lives in src/
  requirements.txt
```

## Rules specific to the backend
- `config.py` holds `TARGETS = ["CAD", "LAD", "LCX", "RCA"]` and `FORBIDDEN_INPUTS` (all label
  columns incl. Cath). Training code **asserts** no forbidden column is in the feature list.
- Every model is a scikit-learn `Pipeline` (preprocessing + classifier) so CV has no leakage and
  the API uses the exact same preprocessing.
- Evaluation: repeated stratified k-fold (e.g. 5×10), mean ± std for accuracy, precision, recall,
  F1, ROC-AUC (+ PR-AUC, Brier). Always include a majority-class baseline.
- Compare a few simple, explainable models (logistic regression, random forest, gradient boosting).
  Prefer the simpler model if scores are close — easier to explain to judges.
- Fixed `random_state` everywhere. Save `metrics.json` so the frontend and report read the same numbers.
- Feature metadata (human label, unit, group, min/max/default) lives in ONE place and feeds `/api/schema`.
- Before trusting results: print the class balance for each target and the exact list of input columns.

## Windows commands Rishi will use (explain on first use)
```powershell
python -m venv .venv            # create an isolated Python environment for this project
.venv\Scripts\Activate.ps1      # turn it on (prompt shows (.venv))
pip install -r requirements.txt # install libraries
python -m src.train             # train + evaluate + save models
uvicorn src.api:app --reload    # start the API at http://localhost:8000 (docs at /docs)
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (explain what it does first).
