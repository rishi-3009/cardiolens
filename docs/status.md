# Status Board

Update this when you start, finish, or get stuck on something. Claude Code agents update it too.

## Now
| Who | Working on | State | Notes |
|---|---|---|---|
| Harshavi | Setup + idea | 🟡 in progress | |
| Rishi | Contract v0.2 + `backend/src/config.py` | 🟢 done | Waiting for Harshavi's review → freeze as v1.0 tonight. Next: leakage-safe training pipeline (`src/data.py`, `src/train.py`) |

## Blocked / needs the other person
- **Harshavi:** please review `contracts/api-contract.md` v0.2 (changes listed in `docs/decisions.md`).
  New mock files are ready: `contracts/mock-schema.json` (real 52 features, 5 steps) and the updated
  `contracts/mock-predict-response.json`. Freeze as v1.0 together tonight.
- **Harshavi:** send Rishi your exact GitHub username (or create an account) so you can be added to
  the private repo https://github.com/rishi-3009/cardiolens. `harshavi0930` doesn't exist on GitHub.

## Done
- 2026-10-10 · Project folder, docs, API contract draft, subagents created
- 2026-10-10 · Rishi: Python 3.11 venv in `backend/.venv`, libraries pinned in `backend/requirements.txt`,
  dataset in `backend/data/raw/`, first look via `python src/inspect_data.py`
  (303 patients, 59 columns, no missing values; 55 usable inputs after removing Cath/LAD/LCX/RCA)
