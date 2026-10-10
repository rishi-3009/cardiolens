# Submission Checklist — tick every box before pressing Submit

## Devpost
- [ ] Both teammates have Devpost accounts with **real full names**
- [ ] Both are **added to the submission** (not just registered)
- [ ] Submitted to **Track A** only
- [ ] Project description: problem, what we built, how it works, results, limitations
- [ ] "Built With" lists the stack **and Claude Code** (AI-tool disclosure)
- [ ] GitHub link (repo is **public**)
- [ ] YouTube link (**Unlisted**, not Private) — opens in a logged-out/incognito window

## GitHub repo
- [ ] README: overview, screenshots/GIF, prerequisites, setup (PowerShell + bash), how to run backend + frontend, how to retrain
- [ ] README: **AI assistance** section — which parts were AI-assisted
- [ ] README: **clinical disclaimer**
- [ ] README: credits — dataset citation (CC BY 4.0), 3D mesh source + license, libraries
- [ ] `backend/requirements.txt` with versions; `frontend/package.json`
- [ ] Trained model weights included (or one command regenerates them) + `metrics.json`
- [ ] `.gitignore` — no `node_modules`, `.venv`, `.env`, secrets
- [ ] Fresh clone → follow README → app works (test on the *other* teammate's laptop)

## The app (judging criteria)
- [ ] Predicts overall CAD + LAD, LCX, RCA
- [ ] LAD, LCX, RCA, Cath, CAD never used as inputs (checked in code)
- [ ] Accuracy, precision, recall, F1, ROC-AUC shown, with validation method
- [ ] 3D heart: rotate, zoom, select vessel; colors driven by predicted probabilities
- [ ] Vessel ↔ prediction mapping verified (LAD high → only LAD red)
- [ ] Overall CAD + vessel probabilities shown next to the 3D canvas
- [ ] SHAP (or LIME) explanation per prediction + measured values with their contribution
- [ ] Disclaimer visible on screen at all times
- [ ] Runs smoothly on a laptop without a dedicated GPU

## Documentation (max 6 pages)
- [ ] Dataset & preprocessing · model architecture · evaluation results · 3D pipeline · usage · limitations

## Demo video (3–10 min, English)
- [ ] Shows the system running: input workflow, prediction, 3D interaction, explanations
- [ ] Explains technical approach (models, validation, leakage prevention, 3D mapping)
- [ ] Mentions the disclaimer and limitations
