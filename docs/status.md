# Status Board

Update this when you start, finish, or get stuck on something. Claude Code agents update it too.

## Now
| Who | Working on | State | Notes |
|---|---|---|---|
| Harshavi | Setup + idea | 🟡 in progress | |
| Rishi | Uncertainty ranges + forest calibration | 🟢 done | `interval` now filled for every target/step. Next: E-full vessel-count model, help Harshavi switch to the real API |

## Blocked / needs the other person
- **Harshavi:** accept the GitHub invite to the private repo https://github.com/rishi-3009/cardiolens
  (sent to `harshavi3009`; check email or github.com/notifications), then
  `git clone https://github.com/rishi-3009/cardiolens.git`.

- **Harshavi:** the real backend is ready whenever you want to switch from the mock files.
  Run it (from `backend/`, venv active): `uvicorn src.api:app --reload` → try it at http://127.0.0.1:8000/docs.
  Tip: use `http://127.0.0.1:8000` as the API base URL; on Windows `localhost` adds ~0.2 s per request.
  `interval` is now filled ([low, high]); `vessel_count.distribution` is still `null` (E-lite).
  /predict takes ~0.6–0.7 s on Rishi's laptop, so show a small loading state while waiting.

## Done
- 2026-10-10 · Project folder, docs, API contract draft, subagents created
- 2026-10-10 · Rishi: Python 3.11 venv in `backend/.venv`, libraries pinned in `backend/requirements.txt`,
  dataset in `backend/data/raw/`, first look via `python src/inspect_data.py`
  (303 patients, 59 columns, no missing values; 55 usable inputs after removing Cath/LAD/LCX/RCA)
- 2026-10-10 · Rishi: leakage-safe training (`python -m src.train`, ~6 min). Repeated stratified 5×10 CV.
  ROC-AUC CAD 0.926 (LogReg), LAD 0.852 (RF), LCX 0.729 (RF), RCA 0.730 (LogReg). 20 models (4 targets × 5 steps)
  + `metrics.json` in `backend/models/`.
- 2026-10-10 · Rishi: SHAP explanations (`src/explain.py`, probability units, adds up exactly) +
  global importance; FastAPI app (`src/api.py`) with health/schema/predict/metrics/global-importance/samples.
  /predict ≈ 0.28 s incl. SHAP for all 4 targets.
- 2026-10-10 · Rishi: random forests (LAD, LCX) now calibrated (LAD Brier 0.164→0.154, LCX recall 0.39→0.51);
  uncertainty ranges from 20 models on random 80% subsets (typical width 7–23 points). Retrain ≈ 10 min.
