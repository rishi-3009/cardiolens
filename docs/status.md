# Status Board

Update this when you start, finish, or get stuck on something. Claude Code agents update it too.

## Now
| Who | Working on | State | Notes |
|---|---|---|---|
| Harshavi | Setup + idea | 🟡 in progress | |
| Rishi | Training pipeline | 🟢 done | Next: SHAP explanations (`src/explain.py`), then the FastAPI app |

## Blocked / needs the other person
- **Harshavi:** accept the GitHub invite to the private repo https://github.com/rishi-3009/cardiolens
  (sent to `harshavi3009`; check email or github.com/notifications), then
  `git clone https://github.com/rishi-3009/cardiolens.git`.

## Done
- 2026-10-10 · Project folder, docs, API contract draft, subagents created
- 2026-10-10 · Rishi: Python 3.11 venv in `backend/.venv`, libraries pinned in `backend/requirements.txt`,
  dataset in `backend/data/raw/`, first look via `python src/inspect_data.py`
  (303 patients, 59 columns, no missing values; 55 usable inputs after removing Cath/LAD/LCX/RCA)
- 2026-10-10 · Rishi: leakage-safe training (`python -m src.train`, ~6 min). Repeated stratified 5×10 CV.
  ROC-AUC CAD 0.926 (LogReg), LAD 0.852 (RF), LCX 0.729 (RF), RCA 0.730 (LogReg). 20 models (4 targets × 5 steps)
  + `metrics.json` in `backend/models/`.
