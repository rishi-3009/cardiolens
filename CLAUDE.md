# CardioLens (working name) — Multimodal AI Hackathon 2026, Track A

> Claude Code reads this file automatically at the start of every session and every subagent.
> Keep it short. Details live in `docs/`. Rename "CardioLens" once the team picks a name.

## What we are building
An interactive web app that predicts **coronary artery disease (CAD)** and **stenosis in the three
main coronary arteries (LAD, LCX, RCA)** from patient clinical data, and shows the predictions on an
**interactive 3D heart** with **SHAP explanations** and a **clinical safety disclaimer**.

Full problem statement: `docs/track-a-problem-statement.md`. Judging weights:
Predictive performance 30% · 3D visualization 25% · Clinical interpretability 20% ·
System integration 15% · Technical implementation 10%.

## Hard facts
- **Deadline: Oct 15, 2026 @ 12:15 AM IST** — treat **Oct 14, 8:00 PM IST** as our real deadline.
- Team of 2. **One track only** (Track A). Both members need Devpost accounts with real full names.
- Submission = Devpost description + public GitHub repo (README with setup) + YouTube demo
  video 3–10 min (unlisted OK, English) + 6-page project documentation.
- Day-by-day plan: `docs/timeline.md`. Submission checklist: `docs/submission-checklist.md`.

## Who owns what
| Person | Owns | Folder | Main agents |
|---|---|---|---|
| **Rishi** | ML models, SHAP, backend API | `backend/` | `ml-engineer`, `api-builder` |
| **Harshavi** | 3D heart, dashboard, UI | `frontend/` | `heart-3d-engineer`, `dashboard-builder` |
| Both | Idea, integration, docs, video | `docs/`, `contracts/` | `ideator`, `integration-tester`, `rules-checker`, `docs-writer`, `code-explainer` |

The two halves talk ONLY through the API described in `contracts/api-contract.md`.
**Never change the contract silently** — any change must be written in the contract file AND
logged in `docs/decisions.md`, because the other person is building against it.

## Non-negotiable rules (breaking these loses points or the submission)
1. **No target leakage.** LAD, LCX, RCA, Cath (and the overall CAD label) are NEVER model inputs.
   All preprocessing (scaling, imputation, encoding, feature selection) happens INSIDE the
   cross-validation pipeline, never on the full dataset first.
2. **Clinical disclaimer always visible** in the UI: predictions are for decision support /
   educational purposes only and are not a substitute for formal diagnostic imaging.
3. **Region with RWMA is a model input, not a 3D location.** Never draw it as a lesion on the heart.
4. **The 3D vessels must match the model outputs exactly**: the mesh named `LAD` shows the LAD
   probability, etc. One shared mapping, defined in the contract.
5. **AI-use disclosure:** README must say which parts were AI-assisted, and Devpost "Built With"
   must list Claude Code. Both teammates must be able to explain every part of the code to a judge.
6. **Licenses:** dataset is CC BY 4.0 (cite it); any 3D mesh must have a license that allows reuse
   (record it in `docs/resources.md` and the README credits).
7. Must run in a normal browser **without a dedicated GPU**. Keep meshes light.
8. No real patient photos or identifiable data anywhere.

## How to work with Harshavi and Rishi (IMPORTANT)
- Both are **beginners** at building software. Before writing a large chunk of code,
  **say what you are about to do and ask any clarifying questions first.**
- **Explain each step in plain words**: what a command does, what a file is for, why.
  Don't assume they know git, the terminal, npm, pip, or virtual environments — explain on first use.
- They use **Windows**. Give **PowerShell** commands (e.g. `.venv\Scripts\Activate.ps1`), not bash.
- Prefer simple, well-known tools over clever ones. Fewer dependencies is better.
- After finishing a piece of work, give a 3–5 line summary: what changed, how to run it,
  how to check it worked.
- Update `docs/status.md` when a task is finished or blocked.

## Tech stack (default — change only via `docs/decisions.md`)
- **Backend:** Python 3.11, pandas, scikit-learn (+ optional XGBoost/LightGBM), SHAP, FastAPI, uvicorn, joblib.
- **Frontend:** React + Vite (JavaScript), React Three Fiber (`@react-three/fiber`, `@react-three/drei`),
  Recharts for charts. Plain CSS or Tailwind.
- **Data:** `backend/data/raw/` (UCI "extention of Z-Alizadeh sani dataset", 303 patients).

## Workflow with subagents
1. `researcher` (quick lookups) → `ideator` (proposes 2–3 directions in `docs/idea.md`)
2. Team picks a direction → recorded in `docs/decisions.md`
3. Builders: `ml-engineer` + `api-builder` (Rishi), `heart-3d-engineer` + `dashboard-builder` (Harshavi)
4. `integration-tester` connects both halves → `rules-checker` audits against the problem statement
5. `docs-writer` writes README, 6-page report, video script, Devpost text
6. `code-explainer` anytime: "explain this file so I can answer a judge"

## Key files
- `docs/track-a-problem-statement.md` — the full brief (source of truth)
- `docs/rules-and-gotchas.md` — every rule + common mistakes
- `contracts/api-contract.md` — backend ↔ frontend agreement
- `contracts/mock-predict-response.json` — fake response so the frontend can be built before the backend is ready
- `docs/decisions.md` — every decision, with date and reason
- `docs/status.md` — who is doing what right now
