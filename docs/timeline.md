# Timeline — 4.5 days (all times IST)

**Real deadline: Wed Oct 14, 8:00 PM.** Devpost closes Oct 15, 12:15 AM — the last 4 hours are
buffer for upload problems only. Each day ends with a 15-minute sync between Harshavi and Rishi.

## Day 0–1 · Sat Oct 10 — Decide & set up
| Harshavi (frontend) | Rishi (backend) |
|---|---|
| Install Node.js, Git, Claude Code; open this folder | Install Python 3.11, Git, Claude Code |
| Run `ideator` together → pick direction → `docs/decisions.md` | (together) |
| Create Vite + React app in `frontend/` | Download dataset into `backend/data/raw/`; inspect columns & label values |
| Heart placeholder + 3 vessel tubes named LAD/LCX/RCA, colored from `mock-predict-response.json` | Fill the real feature list into the contract (`/api/schema`) |
| **Together: freeze `contracts/api-contract.md` v1.0** | |
| Create GitHub repo (Claude Code explains each git step) | |

**Done when:** contract frozen; frontend shows a rotatable heart with 3 colored vessels from mock data.

## Day 2 · Sun Oct 11 — Build the halves
| Harshavi | Rishi |
|---|---|
| Click/hover a vessel → side panel with its % + top factors | Leakage-safe pipelines for CAD/LAD/LCX/RCA, repeated stratified CV, baseline comparison |
| Input form auto-built from schema (mock schema until real one) | Pick best model per target; save weights + `metrics.json` |
| CAD overall risk card + disclaimer banner | SHAP per-patient + global importance |
| SHAP waterfall/bar chart from mock data | FastAPI: `/health`, `/schema`, `/predict` working locally |

**Done when:** backend answers `/api/predict` with real numbers; frontend fully works on mock data.

## Day 3 · Mon Oct 12 — Integrate
| Both |
|---|
| Swap mock → real API (`integration-tester`) |
| `/metrics`, `/global-importance`, `/samples` + their panels |
| Real-time update: change an input → colors + charts update |
| Run `rules-checker` → fix every "must fix" |
| Upgrade heart mesh if time (keep vessel names) |

**Done when:** end-to-end demo works on both laptops from a fresh clone using the README.

## Day 4 · Tue Oct 13 — Polish & write
| Harshavi | Rishi |
|---|---|
| UI polish, loading/error states, mobile-ish layout, sample-patient buttons | Calibration check, final metrics table, model card |
| README (setup, run, credits, AI-use section) with `docs-writer` | 6-page documentation with `docs-writer` (preprocessing, models, evaluation, 3D pipeline) |
| `code-explainer` sessions: each explains the other's code back | |
| Write video script; rehearse | |

## Day 5 · Wed Oct 14 — Ship (FEATURE FREEZE at 10 AM)
- 10 AM–2 PM: record demo video (3–10 min, aim ~6), English, show it running + approach.
- 2 PM: upload to YouTube as **Unlisted**; check it plays in a private window.
- 3 PM: Devpost: description, Built With (incl. Claude Code), GitHub link, video link, both members added.
- 5 PM: final `rules-checker` + `docs/submission-checklist.md` pass.
- **8 PM: SUBMIT.** Then stop touching the repo.
