# Status Board

Update this when you start, finish, or get stuck on something. Claude Code agents update it too.

## Now
| Who | Working on | State | Notes |
|---|---|---|---|
| Harshavi | Setup + idea | 🟡 in progress | |
| Rishi | Training pipeline (`src/data.py`, `src/train.py`) | 🟡 in progress | Contract v1.0 frozen |

## Blocked / needs the other person
- **Harshavi:** accept the GitHub invite to the private repo https://github.com/rishi-3009/cardiolens
  (sent to `harshavi3009`; check email or github.com/notifications), then
  `git clone https://github.com/rishi-3009/cardiolens.git`.

## Done
- 2026-10-10 · Project folder, docs, API contract draft, subagents created
- 2026-10-10 · Rishi: Python 3.11 venv in `backend/.venv`, libraries pinned in `backend/requirements.txt`,
  dataset in `backend/data/raw/`, first look via `python src/inspect_data.py`
  (303 patients, 59 columns, no missing values; 55 usable inputs after removing Cath/LAD/LCX/RCA)
