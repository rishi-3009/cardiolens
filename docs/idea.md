# Idea Directions: CardioLens (Track A)

*Written Sat Oct 10, 2026, ~1 PM IST by the `ideator` agent. Real deadline: **Wed Oct 14, 8 PM IST**
(feature freeze Wed 10 AM). Nothing here is decided yet. Once the team picks a direction, record it in
`docs/decisions.md`.*

---

## 0. Ground rules for all directions

**Every direction below includes the full mandatory baseline.** The directions only differ in the
**standout layer** added on top.

| Mandatory piece | Source in brief |
|---|---|
| Models for overall CAD (`Cath`) + LAD, LCX, RCA, with no label columns as inputs and preprocessing inside CV | Req 1a–1e |
| Accuracy, precision, recall, F1, ROC-AUC reported (mean ± std over repeated stratified CV) + a "majority class" baseline | Req 1e, gotcha 3–4 |
| 3D heart with 3 separate vessel objects named `LAD`/`LCX`/`RCA`, colored from the predicted probabilities | Req 2a–2b |
| Rotate, zoom, and click/hover a vessel to see its % and top reasons | Req 2c |
| Dashboard: overall CAD card, vessel %s, per-patient SHAP (with the patient's actual values) + global importance | Req 3a–3c |
| Always-visible clinical disclaimer | Req 5 |
| Region RWMA used only as a model input, never painted on the heart | Brief + gotcha 11 |

**What "standout" has to beat.** At least one public repo from this same hackathon already does the
basics (SVM/Random Forest, 3D vessels, SHAP, disclaimer). Its README reports **no metrics, no
validation method, no calibration, no uncertainty, and no what-if** ([cardio-risk-3d][comp]). Doing
the basics well is necessary, but it won't separate us from other teams. A visible, honest
evaluation plus a feeling of "the heart reacts to me" will.

---

## 1. Realistic targets (research summary)

### What published papers report
- **Overall CAD:** papers report accuracy of about **89–98%** and AUC up to **0.98–0.99**
  ([Frontiers 2025 SVM+SHAP][bosvm], [GSVMA][gsvma], [Random Trees][rt]).
- **Per vessel:** accuracy varies widely. Simple bagging/C4.5 trees got LAD ~77–80%, LCX ~61–65%,
  RCA ~63–69%. Tuned SVMs with feature selection got LAD ~86%, LCX ~83%, RCA ~83%. Heavily optimized
  stacking or multi-filter methods claim 86–95% ([Alizadehsani et al., uncertainty paper][unc],
  [whale + stacking][whale], [Semantic Scholar table][ss]).
- **Features that matter most:** *Typical chest pain* is consistently #1. After that come **Age,
  EF-TTE** (heart pumping strength on echo), **Region RWMA, T-wave inversion, HTN** (high blood
  pressure), **DM** (diabetes), and **ESR** (an inflammation blood test) ([Random Trees][rt],
  [Frontiers 2025][bosvm], [5-feature AdaBoost][ada5]).

### Why we should NOT chase the 95% numbers
Many papers pick features or oversample (SMOTE, which creates synthetic patients) using the whole
dataset, or tune repeatedly on the same test folds. Both leak information and inflate scores. Our
rules forbid that. Judges score *validation methodology*, so honest numbers with mean ± std and a
baseline are worth more than a suspicious 97%.

### Our honest target ranges
These are **our own estimates** for a leakage-safe pipeline using logistic regression or a tree model,
not cited numbers.

| Target | Majority baseline accuracy | Realistic CV accuracy | Realistic ROC-AUC |
|---|---|---|---|
| CAD (`Cath`) | 71% | 84–90% | 0.88–0.94 |
| LAD | 58% | 70–80% | 0.75–0.85 |
| LCX | 61% | 65–75% | 0.65–0.78 |
| RCA | 62% | 65–76% | 0.68–0.80 |

If LCX/RCA end up around AUC 0.70, **that is normal for this dataset, not a failure.** Present it
honestly: "vessel-level prediction from clinical data alone is hard; this is why imaging exists."

### Data notes that affect every direction
These come from Rishi's inspection of the real file.
- **54 usable inputs.** That is 59 columns, minus the 4 labels, minus `Exertional CP`, which is constant.
- **`Sex` uses "Fmale"** (a typo in the data). Encode it deliberately and show "Female" in the UI.
- **BMI is computed from Weight and Length.** When features are correlated, SHAP (the method that
  splits the prediction into per-feature contributions) shares the credit between them, so each
  looks weaker than it is. Suggestion: keep **BMI** and drop Weight/Length from the model inputs.
  Log this in `decisions.md` if adopted.
- **The labels are almost perfectly consistent.** `Cath = CAD` exactly when at least one vessel is
  stenotic, except for **1 patient**. The count of stenotic vessels is 0→86, 1→87, 2→67, 3→63. This
  makes a "number of diseased vessels" idea cheap and well-supported.
- **Cholesterol barely matters here.** In this dataset the strong signals are symptoms, ECG, and echo,
  not cholesterol. A what-if slider on LDL may hardly change the colors, and a judge could think the
  app is broken. Any what-if panel should **lead with the features that matter for this patient** (the
  top SHAP features), not a fixed "cholesterol / BP" list.

### Time budget (honest)
From Sat 1 PM to the Wed 10 AM freeze, minus sleep, the Tuesday docs/video prep, and life, each
person has roughly **22–26 focused hours**. The mandatory baseline costs about **16–20 h each**.
That leaves a **standout budget of about 5–8 hours per person**. Anything bigger cuts into polish,
and polish is where beginners lose demos.

---

## Direction A: "The Honest Heart" (trust and validation layer)

### 1. One-line pitch
**"A heart that tells you how sure it is, and proves it."**

### 2. What the user sees (30-second demo)
1. Click "Load sample: high-risk patient". The vessels color in. LAD is red, at **78%
   (likely range 71–84%)**, shown as a small range bar under the number.
2. Hover RCA. It reads "41%, Moderate, the models disagree a lot (range 28–55%)", and the vessel has a
   faint pulsing outline to signal uncertainty.
3. The overall card reads: "CAD risk 91%. Expected number of narrowed vessels: **1.9 of 3**.
   ✔ Consistent with vessel predictions."
4. Open the **"How good is this model?"** tab. It shows a metrics table for all 4 targets (mean ± std
   vs. the "always guess majority" baseline), a **calibration plot** ("when we say 70%, about 70%
   really had it"), and a one-paragraph "How we validated" card covering repeated stratified CV,
   no label columns as inputs, and preprocessing inside each fold.

### 3. Standout features (max 3)
| # | Feature | What it is, in plain words | Boosts |
|---|---|---|---|
| A1 | **Uncertainty range** | Keep the 5 models trained during cross-validation and run all 5 on the patient. Show the average plus the lowest/highest as a range. A wide range means "the data doesn't pin this down." | Predictive performance (risk estimation quality), Interpretability |
| A2 | **Consistency layer** | Two simple, mathematically sound checks. **(a)** Expected number of narrowed vessels = LAD% + LCX% + RCA% (true even when the vessels are related). **(b)** CAD means "any vessel narrowed", so CAD% should be **at least the highest vessel %**. If it isn't, show a "models disagree" badge and explain why. | Predictive performance, Interpretability |
| A3 | **In-app validation panel** | Metrics table with baseline, calibration curve + Brier score (a single number for how well probabilities match reality; lower is better), and a "How we validated" card. | Predictive performance (validation methodology), Technical implementation |

### 4. Score estimate (rough guesses, assuming the baseline is solid)
| Criterion | Est. | Why |
|---|---|---|
| Predictive performance (30) | **25** | Judges see methodology, baseline, calibration, and uncertainty without opening the code. |
| 3D visualization (25) | **16** | Correct vessel coloring and selection, plus an uncertainty outline, but nothing that wows. |
| Clinical interpretability (20) | **15** | SHAP is solid. Ranges and the consistency badge add honesty, but there is no plain-language layer. |
| System integration (15) | **11** | Standard predict → recolor flow. |
| Technical implementation (10) | **8** | Clean pipeline, saved metrics JSON, reproducible. |
| **Total** | **~75** | Strong where the weight is highest. Weaker on "wow". |

### 5. Feasibility
- **Rishi: +6–8 h.** Save the fold models (1 h), range in `/predict` (1–2 h), calibration bins +
  Brier in `/metrics` (2 h), consistency numbers (1 h), contract update (1 h).
- **Harshavi: +3–4 h.** Range bar under each %, a metrics/calibration tab (Recharts line chart),
  a consistency badge, and an uncertainty outline on the vessel.
- **Riskiest part:** the calibration curve with only 303 patients looks jagged and can confuse a
  judge. **Fallback:** use 5 wide bins, and if it still looks bad, show only the Brier score and
  a sentence.
- **Contract change:** add optional fields `interval: [low, high]` per target,
  `consistency: {expected_vessels, cad_lower_bound, consistent}` in `/predict`, and `calibration` in
  `/metrics`. These are additive, so nothing breaks.

### 6. Cut first
1. Uncertainty outline on the 3D vessel (keep the range as text).
2. Calibration plot (keep the Brier score).
3. Consistency badge (keep "expected narrowed vessels" as one line).

---

## Direction B: "What-If Heart" (live interaction layer)

### 1. One-line pitch
**"Move a slider, watch the arteries change, and read why in plain English."**

### 2. What the user sees (30-second demo)
1. Load a sample patient. LAD is red at 72%.
2. A **"What-if" panel** lists this patient's 5 most influential features as sliders and toggles
   (e.g. Typical chest pain = Yes, EF = 40%, Age 63, DM = Yes, BP 150).
3. Drag **EF** from 40% to 55%. Within half a second the LAD tube **fades from red to amber**. A small
   "72% → 58% (▼14)" tag appears next to it, and a faint "ghost" marker shows the original value.
4. Click **"Patient view"**. The SHAP bars turn into sentences: "Your chest-pain pattern raised the
   estimate the most. Your normal pumping strength lowered it." Click **"Clinician view"** to see the
   full SHAP waterfall with raw values and units.
5. A banner under the panel stays visible: "What-if shows how *the model's estimate* responds. It does
   not predict what a treatment would do."

### 3. Standout features (max 3)
| # | Feature | What it is, in plain words | Boosts |
|---|---|---|---|
| B1 | **Live what-if panel** | Sliders and toggles built from `/api/schema`, pre-filled with the patient and ordered by that patient's top SHAP features. Each change, after a short pause (a "debounce"), calls `/predict` again. The vessels smoothly animate to new colors, and a before→after delta tag appears. "Reset to patient" button. | System integration (real-time updates), 3D visualization, Interpretability |
| B2 | **Patient view / Clinician view toggle** | The same SHAP numbers shown two ways. Patient view uses template sentences ("X raised your estimate a lot"), with no AI text generator. Clinician view shows the waterfall chart, raw values, units, and SHAP units. | Clinical interpretability (clarity of explanation) |
| B3 | **Auto-focus riskiest vessel** | After each prediction, the riskiest vessel's side panel opens automatically and the camera eases a little toward it. This is a lighter version of a full guided tour. | 3D visualization (spatial risk mapping) |

### 4. Score estimate
| Criterion | Est. | Why |
|---|---|---|
| Predictive performance (30) | **20** | Baseline metrics only. Judges see the numbers, but not why to trust them. |
| 3D visualization (25) | **20** | Live animated recoloring and auto-focus make the 3D feel useful, not decorative. |
| Clinical interpretability (20) | **17** | Two audiences, plain-language reasons, and what-if exploration. |
| System integration (15) | **13** | "Change an input → colors + charts update" is literally what this criterion asks for. |
| Technical implementation (10) | **7** | Schema-driven form shows extensibility. |
| **Total** | **~77** | Most memorable demo. Weaker on the heaviest criterion. |

### 5. Feasibility
- **Rishi: +2–3 h.** Make `/predict` fast (under ~300 ms). Logistic regression or tree models with a
  matching SHAP explainer are fast enough, but **avoid KernelExplainer, which is too slow for live
  use**. Optionally add a `modifiable: true/false` flag per feature in the schema.
- **Harshavi: +8–10 h.** What-if panel from the schema (3 h), debounce + before/after delta (2 h),
  color tween (1 h), patient/clinician toggle with sentence templates (2–3 h), auto-focus (1 h).
  This is **at the edge of Harshavi's standout budget**.
- **Riskiest part:** the live slider loop (input → API → 3D + charts) gets laggy or flickers, or
  state gets tangled (beginner React risk). **Fallback:** replace live dragging with an **"Apply
  changes"** button. It still counts as a real-time update, and is much simpler.
- **Clinical risk:** sliders can suggest cause and effect ("lower BP → fewer blockages"). The model
  learned correlations, not causes. Keep the banner and the wording "the model's estimate".
- **Contract change:** optional `modifiable` flag in `/api/schema` features. Everything else is
  already in the contract.

### 6. Cut first
1. Auto-focus camera move (just auto-open the side panel).
2. Ghost "original value" markers (keep the delta tag).
3. Live drag (switch to the "Apply changes" button).

---

## Direction C: "Heart Tour & Compare" (storytelling layer)

### 1. One-line pitch
**"A guided tour of two hearts: see exactly where and why one patient is at higher risk."**

### 2. What the user sees (30-second demo)
1. Click **"Tour"**. The camera flies to the riskiest vessel (LAD, red), pauses, and a caption card
   says "LAD supplies the front of the heart. Estimated 78%, driven mainly by typical chest pain and
   T-wave inversion." The camera then moves on to LCX and RCA.
2. Click **"Compare"**. The screen splits into two hearts side by side, Patient A (high risk) and
   Patient B (low risk), with matching vessel colors and a table of the features that differ most.
3. The captions come in patient-friendly wording.

### 3. Standout features (max 3)
| # | Feature | What it is, in plain words | Boosts |
|---|---|---|---|
| C1 | **Guided camera tour** | Animated camera stops at each vessel in risk order, each with a caption card. Built with drei's `CameraControls`. | 3D visualization (spatial mapping, interactivity) |
| C2 | **Two-patient comparison** | Two synced 3D views + a "what's different" table (the features with the biggest SHAP difference between the two). | 3D visualization, Interpretability |
| C3 | **Narrated captions** | Template sentences built from SHAP for each stop. | Clinical interpretability |

### 4. Score estimate
| Criterion | Est. | Why |
|---|---|---|
| Predictive performance (30) | **20** | Baseline metrics only. |
| 3D visualization (25) | **21** if it works, **13** if buggy | Highest ceiling, highest variance. A jerky camera looks worse than no tour. |
| Clinical interpretability (20) | **16** | Comparison is a good teaching tool. |
| System integration (15) | **11** | Two predictions at once, but no live editing. |
| Technical implementation (10) | **6** | More complex frontend state and more ways to break. |
| **Total** | **~74, with high variance** | |

### 5. Feasibility
- **Rishi: +2 h.** A "compare" helper, or just call `/predict` twice from the frontend.
- **Harshavi: +12–15 h.** Camera animation math (4–5 h), two 3D views on a laptop without a dedicated
  GPU (3–4 h, since two WebGL scenes double the work), captions (2 h), comparison table (2 h).
  **This is about double Harshavi's standout budget**, and all of it lands on the frontend person.
- **Riskiest part:** two simultaneous 3D canvases stuttering on an integrated GPU, and camera
  animation bugs (the camera flipping or ending up inside the heart).
- **Fallback:** no fly-through, just preset camera positions ("Front / Left / Right" buttons).
  Compare as two cards with numbers and a single shared heart.

### 6. Cut first
1. Second 3D view (compare = numbers only).
2. Animated tour (preset camera buttons).
3. Captions (reuse side-panel text).

---

> **Directions D and E** were added after the ideator run (Sat Oct 10, Rishi + Claude Code). A–C
> mostly add common hackathon extras on top of the brief. D and E come from **the structure of this
> specific dataset**, so other teams are less likely to have them.

## Direction D: "Step-by-Step Checkup" (follows a real hospital visit)

### 1. One-line pitch
**"Watch the heart come into focus as each test result comes in, and see which tests actually matter."**

### 2. What the user sees (30-second demo)
1. A 4-step bar sits above the heart: **History → Exam → ECG → Labs & Echo**. Only step 1 is filled in.
   The vessels show cautious, middling colors, and each % has a **wide** range (e.g. "LAD 55%, range 38–70%").
2. Click **Exam**. Typical chest pain = Yes is added. LAD jumps to 68%, and the ranges get narrower.
3. Click **ECG**, then **Labs & Echo**. EF-TTE (pumping strength) and Region RWMA come in. LAD settles
   at red 81% with a tight range, and RCA drops to green.
4. A small chart under the bar shows **"How much did each test add?"** It plots CV ROC-AUC per step for
   the selected target, e.g. CAD 0.74 → 0.85 → 0.87 → 0.92. *These numbers are invented for the
   example; the real ones come from training.*

### 3. Why it's different
- The dataset's columns **already come in these 4 groups, in this order** (file columns 1–17
  demographic/history, 18–31 symptoms & exam, 32–38 ECG, 39–55 labs & echo). It matches the order a
  real patient goes through, from questions and an exam to an ECG, then blood tests and an echo.
- It answers a real clinical question: **how much does each extra test tell us?** Echo and labs cost
  time and money. Most projects on this dataset only report one number for "all features".
- It gives the report a strong, honest results table (performance per step × per target), which helps
  with the 30% *validation methodology* criterion.

### 4. Standout features
| # | Feature | What it is, in plain words | Boosts |
|---|---|---|---|
| D1 | **Step models** | For each target, train 4 pipelines on **cumulative** feature sets: step 1 = history only, step 2 = history + exam, and so on up to all features. 4 steps × 4 targets = 16 pipelines, all evaluated with the same repeated stratified CV. The app uses the model for the furthest completed step, **so no step pretends to know values it hasn't seen.** | Predictive performance, Interpretability |
| D2 | **Checkup stepper on the heart** | The 4-step bar. Each step reveals the next group of form fields, which already come grouped from `/api/schema` (`group`). Each completed step re-predicts and recolors the vessels. Works well with A1 ranges: watching the ranges narrow is the "coming into focus" effect. | 3D visualization, System integration |
| D3 | **"Value of each test" chart** | Line or bar chart of CV ROC-AUC per step for each target (from `/api/metrics`). | Predictive performance, Clinical interpretability |

### 5. Score estimate (rough guesses, assuming the baseline is solid)
| Criterion | Est. | Why |
|---|---|---|
| Predictive performance (30) | **24** | A per-step results table is unusual and shows careful validation. |
| 3D visualization (25) | **19** | The heart visibly changes as the story moves forward, not just once. |
| Clinical interpretability (20) | **17** | Explains *which tests* drive the estimate, on top of which features. |
| System integration (15) | **13** | Each step is a live predict → recolor update. |
| Technical implementation (10) | **8** | Schema groups drive the stepper, so adding a step means changing config, not code. |
| **Total** | **~81** | |

### 6. Feasibility
- **Rishi: +4–6 h.** Loop the training over 4 cumulative feature sets (2–3 h, mostly reusing the same
  code), per-step metrics in `metrics.json` (1 h), `stage` parameter in `/predict` (1 h), contract update (1 h).
- **Harshavi: +4–5 h.** Stepper bar that reveals form groups (2–3 h), per-step chart in Recharts (1–2 h).
- **Riskiest part:** early steps may predict poorly for the vessels (e.g. LCX AUC ~0.55 from history
  alone). **That is fine, and it's the point.** It shows honestly that history alone can't locate disease.
  Say so in the demo.
- **Other risk:** 16 pipelines mean 16 SHAP explainers. **Fallback:** show SHAP only for the
  full-information step, and for earlier steps show just the % and range.
- **Optional split:** make Echo (EF-TTE, Region RWMA, VHD) its own 5th step, separate from blood tests,
  since it is a different test in real life. Decide when filling the schema.
- **Contract change (additive):** optional `"stage": 1-4` in the `/predict` request (default = all
  features), a `stages` list in `/api/schema`, and per-stage results in `/api/metrics`.

### 7. Cut first
1. The 5th Echo step (keep 4 steps).
2. SHAP for early steps (show it for the full step only).
3. The stepper animation (simple tabs work too).

---

## Direction E: "How Many Arteries?" (disease extent)

### 1. One-line pitch
**"Not just *is* there disease, but *how widespread* is it: 1, 2 or all 3 arteries."**

### 2. What the user sees
Next to the overall CAD card, a small card reads **"Narrowed arteries: estimated 2 of 3"**, with 4 bars
showing the chance of 0 / 1 / 2 / 3 narrowed arteries (e.g. 5% / 22% / 41% / 32%).

### 3. Why it's different
- In real cardiology, **how many** main arteries are narrowed (single-, double-, or triple-vessel
  disease) is one of the main things that shapes the next steps. Few projects on this dataset predict it.
- The data supports it well. Patients with 0 / 1 / 2 / 3 stenotic vessels: **86 / 87 / 67 / 63**, a
  rare well-balanced split.
- **Safety framing:** the UI shows the estimate only, never a treatment suggestion. Clinical context
  belongs in the docs and video, with the disclaimer.

### 4. Two ways to build it
| Option | How | Effort | Notes |
|---|---|---|---|
| **E-lite** | Expected count = LAD% + LCX% + RCA% (same as A2). No new model. | Rishi 0.5 h | Gives one number, not the 0/1/2/3 bars. |
| **E-full** | One extra model that predicts the count (0–3) directly. The target is built from the LAD/LCX/RCA labels, which stay **forbidden as inputs**. | Rishi 2–3 h | Gives the 4 bars. Report accuracy, macro-F1, and one-vs-rest AUC vs. the "always guess most common" baseline (87/303 = 29%). |

- **Harshavi: +1–2 h** for the card (bars or a 0–3 gauge). It is **not drawn on the 3D heart**, since
  it isn't one vessel.
- **Riskiest part:** E-full's count can disagree with the 3 vessel %s. **Fallback:** show the E-lite
  number, or a small "models disagree" note (same idea as A2).
- **Contract change (additive):** optional `vessel_count: {expected, distribution: [p0, p1, p2, p3]}`
  in `/predict`, and a `VESSEL_COUNT` entry in `/api/metrics`.

### 5. Score effect
Adds an estimated **+1–2 to Predictive performance and +1–2 to Interpretability** on top of whichever
direction is chosen. It is small to build, but judges remember it.

---

## Alternative to the recommendation below: "A + D (+E)"

Use **A as the backbone** as recommended, but replace B-lite with **D**, and add **E-lite** for almost
no extra cost (E-full if time allows).
- **Rishi:** A1 ranges, A3 metrics + calibration, D1 step models, E-lite (and A2 consistency if time).
  About +8–10 h, more than A alone, so **D1 comes before A2**.
- **Harshavi:** D2 stepper, D3 per-step chart, A range bars and metrics tab, E card. About +7–9 h.
- **Why:** A + D covers the same criteria as A + B-lite, but D's story ("the heart comes into focus
  test by test") is based on the dataset rather than the brief. That makes it harder for other teams
  to copy and easier to remember.
- **Rough score:** ~83–84 (a guess, not a promise).

---

## Recommendation (ideator's original)

**Pick Direction A as the backbone, and add a trimmed version of Direction B on the frontend
("A + B-lite").** If the team prefers one pure direction, choose **A**.

Why:
1. **It matches who has spare time.** A's work is mostly backend (Rishi), and B's work is mostly
   frontend (Harshavi). Combining A with a *trimmed* B gives each person about 6–8 standout hours
   instead of overloading one person. C puts 12–15 h on Harshavi alone, which is too risky.
2. **It puts effort where the points are.** Predictive performance is the biggest criterion (30%), and
   A makes our validation *visible in the app*. The other public team project shows no metrics at all.
   B's live recoloring hits integration (15%) and 3D (25%).
3. **Every piece has a safe fallback.** Ranges fall back to text, calibration to the Brier score, and
   live sliders to an "Apply changes" button. None of them can break the baseline.

**What "A + B-lite" includes:**
- **Rishi:** A1 (uncertainty range), A2 (consistency check), A3 (metrics + calibration), and a fast `/predict`.
- **Harshavi:** B1 (what-if panel) with the **"Apply changes" button first** and live drag only if
  there's time Monday night; B2 (patient/clinician toggle); range bars and a metrics tab for A.
- **Skip:** the guided tour, two-patient comparison, uncertainty outlines on the 3D vessels, and ghost markers.
- **Rough score:** Pred 25 · 3D 19 · Interp 17 · Integration 13 · Tech 8 ≈ **82** (a guess, not a promise).

**Order of work:** the baseline first (all of it, end to end, by Mon evening), then standout features
in this order: A3 metrics panel → B1 what-if with Apply button → A1 ranges → B2 toggle → A2
consistency → live drag. Stop wherever Tuesday noon arrives.

---

## 3 questions to answer before choosing

1. **How many focused hours can each of you really give between now and Tue night** (classes,
   work, sleep)? If either answer is under ~20 h, choose **pure A** and treat what-if as stretch only.
2. **Are you comfortable pitching honest, lower vessel numbers** (e.g. LCX AUC ~0.70) next to papers
   claiming 90%+, with "we validated properly, and here's the proof" as the headline? A only wins
   points if you lean into this message in the video and docs.
3. **Who is the main "user" in the demo story, a cardiologist or a patient?** This decides which view
   is the default, the wording of captions, and which optional fields (`interval`, `consistency`,
   `calibration`, `modifiable`) go into **contract v1.0 tonight**, before it's frozen.

---

## Sources

- cardio-risk-3d, another Multimodal AI Hackathon 2026 project: https://github.com/AdhiAgrawal0205/cardio-risk-3d
- Alizadehsani et al., *Model uncertainty quantification for diagnosis of each main coronary artery stenosis* (Soft Computing): https://link.springer.com/article/10.1007/s00500-019-04531-0
- *Diagnosis of Coronary Arteries Stenosis Using Data Mining* (per-vessel results table): https://www.semanticscholar.org/paper/Diagnosis-of-Coronary-Arteries-Stenosis-Using-Data-Alizadehsani-Habibi/93c6703110d33642dfe3fe0c819a6c4884b0e322/figure/0
- *Diagnosis of each main coronary artery stenosis based on whale optimization algorithm and stacking model* (MBE 2022): http://www.aimspress.com/article/doi/10.3934/mbe.2022211
- *CAD Diagnosis: Ranking the Significant Features Using Random Trees Model*: https://arxiv.org/pdf/2001.09841
- *CAD prediction using Bayesian-optimized SVM with feature selection* (Frontiers in Network Physiology, 2025): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12738877/
- *GSVMA: Genetic-SVM-ANOVA method for CAD diagnosis on Z-Alizadeh Sani*: https://arxiv.org/pdf/2108.08292
- *Novel CAD Diagnosis Method Based on Search, PCA, and AdaBoostM1* (J. Clin. Med. 2024): https://doi.org/10.3390/jcm13102868
- Other related work: [LightGBM + class balancing (MDPI Electronics)](https://www.mdpi.com/2079-9292/11/9/1495), [AI Framework for Early CAD Diagnosis (arXiv 2308.15339)](https://arxiv.org/pdf/2308.15339)

[comp]: https://github.com/AdhiAgrawal0205/cardio-risk-3d
[unc]: https://link.springer.com/article/10.1007/s00500-019-04531-0
[ss]: https://www.semanticscholar.org/paper/Diagnosis-of-Coronary-Arteries-Stenosis-Using-Data-Alizadehsani-Habibi/93c6703110d33642dfe3fe0c819a6c4884b0e322/figure/0
[whale]: http://www.aimspress.com/article/doi/10.3934/mbe.2022211
[rt]: https://arxiv.org/pdf/2001.09841
[bosvm]: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12738877/
[gsvma]: https://arxiv.org/pdf/2108.08292
[ada5]: https://doi.org/10.3390/jcm13102868
