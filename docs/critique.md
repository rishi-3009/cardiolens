# Critique of `docs/idea.md`: independent scoring

*Written Sat Oct 10, 2026, ~2 PM IST by the `critic` agent. I scored everything from scratch and did
not use the numbers in `idea.md`. I'm judging the way a busy judge would: watching a 3–10 minute
video and skimming the repo and the 6-page doc. Nothing here is decided. The team decides, then
records the choice in `docs/decisions.md`.*

---

## 0. How I scored (read this first)

**Weights:** Predictive Performance 30 · 3D Visualization 25 · Clinical Interpretability 20 ·
System Integration 15 · Technical Implementation 10 = 100.

**The baseline sets most of the score.** If the mandatory baseline ships cleanly (CV metrics
with mean ± std and a majority baseline, 3 named vessels colored by probability, local + global
SHAP, a form built from the schema that re-predicts, and the disclaimer), I'd guess it scores about:

| Pred | 3D | Interp | Integ | Tech | **Total** |
|---|---|---|---|---|---|
| 20 | 15 | 13 | 10 | 7 | **65** |

The standout layers in `idea.md` add roughly **+2 to +11** on top of that. So the top 4 options
below are within about **3 points** of each other, which is less than my margin of error (about ±3).
**Finishing the baseline cleanly matters more than which direction you pick.**

**Time reality (this is where `idea.md` is too optimistic).**
- `idea.md` says the baseline costs 16–20 h per person, which leaves 5–8 h for extras. That's
  plausible for **Rishi**: setup is done, the data is inspected, and scikit-learn + SHAP + FastAPI is
  a well-trodden path.
- For **Harshavi** it's too optimistic. The frontend hasn't started (no Vite app yet), and R3F, the
  form built from the schema, the SHAP charts, the side panel, mock → real integration, loading and
  error states, and the README all land on a beginner. I'm guessing Harshavi's baseline takes
  **20–24 h**, which leaves only **2–5 h** for extras.
- **Conclusion:** standout work should sit mostly on **Rishi's** side. Any plan that gives Harshavi
  more than ~5 extra hours puts the baseline polish at risk, and polish is what judges see in the video.

**How I computed the "expected" score.** I estimated the chance that each option fully ships by the
Wed 10 AM freeze. Then I mixed three outcomes: full ship, partial ship (fallbacks used), and
"overrun" (the extra work ate the baseline polish).

---

## 1. Direction A: "The Honest Heart" (uncertainty + consistency + validation panel)

| Criterion | Score if shipped | Why |
|---|---|---|
| Predictive (30) | **24** | A metrics panel inside the app, the majority baseline, and a Brier score/calibration directly hit "risk estimation quality" and "validation methodology". |
| 3D (25) | **15** | Same heart and same coloring as the baseline. A faint outline is not "anatomical representation". |
| Interp (20) | **14** | Ranges and an "expected vessels" line are honest, but they don't make the *why* any clearer. |
| Integration (15) | **10** | Standard predict → recolor. |
| Tech (10) | **8** | Saved fold models, metrics JSON, reproducible. |
| **Total** | **71** | |

- **Chance of fully shipping:** ~70%. Most of the work is Rishi's, and Harshavi's part is small
  (a Recharts table/chart and a range bar). **Expected: ~70** (70% × 71, the rest at ~68 with the
  fallbacks).
- **Weakest point a judge would see:** the 3D heart looks exactly like every other team's.
  A puts 0 of its effort into the 25% criterion.
- **Claim I disagree with most:** *"LAD 78% (likely range 71–84%)… RCA range 28–55%"*. The spread of
  the 5 cross-validation fold models is **not** a confidence interval. Each fold model is trained on
  80% of the same 303 patients, so with logistic regression or a random forest I'm guessing the
  spread will be about **±2–5 points**, not ±13. The demo effect ("wide range = unsure") will
  probably not appear. Calling it a "likely range" also over-claims. If you keep it, call it a
  "model stability range" and explain it in one sentence.
- **Also:** if Rishi uses `class_weight="balanced"` (gotcha 4), the predicted probabilities shift
  upward for LCX and RCA, and the **calibration plot will look bad**. Either calibrate inside the
  pipeline (`CalibratedClassifierCV`) or don't use balanced weights for the probability model.
  The calibration curve and Brier score must be computed on **out-of-fold** predictions only.
- **Rule risks:** over-claiming certainty ("likely range"). The consistency badge (A2b) may show
  "models disagree" on the very demo patient you picked, which looks like a bug. Test it on all
  sample patients first.

---

## 2. Direction B: "What-If Heart" (sliders + patient/clinician view)

| Criterion | Score if shipped | Why |
|---|---|---|
| Predictive (30) | **20** | Baseline only. |
| 3D (25) | **17** | A smooth color fade and auto-focus make the heart feel alive, but the anatomy is unchanged. |
| Interp (20) | **16** | The patient/clinician toggle with sentences is a real win for "clarity of risk explanation". |
| Integration (15) | **12** | Live updates with a before → after tag, about +2 over the baseline's re-predict. |
| Tech (10) | **7** | More frontend state means more ways for a beginner's code to break. |
| **Total** | **72** | |

- **Chance of fully shipping:** ~45%. That's +8–10 h on Harshavi, the person with the least slack.
  **Expected: ~69** (45% full; otherwise the Apply button plus a squeezed baseline, ~67).
- **Weakest point:** it's the most "copyable" idea. What-if sliders are the first extra almost
  every team thinks of.
- **Claim I disagree with most:** that the **"Apply changes" fallback still makes it a standout**.
  "Change an input → new prediction → 3D + charts update" is already **required** (gotcha 17,
  timeline Day 3). B's Apply-button fallback is just the baseline form. Only the delta tag, the
  color fade, the ordering by top SHAP features and B2 are actually new.
- **Rule risks:** suggesting cause and effect or treatment ("lower your BP → fewer blockages"). Keep
  the banner. Clamp sliders to the min/max in the schema so nobody drags into nonsense values.

---

## 3. Direction C: "Heart Tour & Compare" (camera tour + two hearts)

| Criterion | Score if shipped | Why |
|---|---|---|
| Predictive (30) | **20** | Baseline only. |
| 3D (25) | **19** | This would be the best 3D showing, *if* the camera moves smoothly. If it's jerky, it scores below the baseline. |
| Interp (20) | **15** | Captions and the "what's different" table are a good teaching tool. |
| Integration (15) | **10** | No new live flow. |
| Tech (10) | **6** | Two WebGL canvases plus camera state is the hardest code here for a beginner to explain. |
| **Total** | **70** | |

- **Chance of fully shipping:** ~25%. It needs 12–15 h on Harshavi, and I think even that estimate
  is low for a beginner doing camera animation. **Expected: ~65**, the worst option, because when it
  fails it eats the baseline polish.
- **Weakest point:** two 3D scenes on a laptop without a dedicated GPU (rule 7) stuttering live
  in the video.
- **Claim I disagree with most:** *"3D 21 if it works"*. A judge watching a video sees a camera
  move, not a better *anatomical representation*. The upside is smaller than it sounds.
- **Rule risks:** captions saying "a blockage is located here" (we predict vessel probability,
  not lesion location). Also the temptation to highlight the RWMA wall region during the tour.

---

## 4. Direction D: "Step-by-Step Checkup" (History → Symptoms & Exam → ECG → Labs & Echo)

| Criterion | Score if shipped | Why |
|---|---|---|
| Predictive (30) | **24** | A table of 4 steps × 4 targets, all with the same repeated CV, is a real "incremental value" analysis. That's rare on this dataset and exactly what "validation methodology" means. |
| 3D (25) | **16** | The heart visibly changes 3–4 times during the story. It's still the same anatomy. |
| Interp (20) | **15** | "Which *tests* drive the estimate" adds a layer above feature-level SHAP. |
| Integration (15) | **11** | Each step is a live re-predict. Driven by the schema's `group`, so it's extensible. |
| Tech (10) | **8** | Stages as config, 16 pipelines from one training loop. |
| **Total** | **74** | |

- **Chance of fully shipping:** ~60%. Rishi's part is mostly a loop around code Rishi will write
  anyway (about 75% likely). Harshavi's stepper is tabs over form groups the schema already provides,
  which is simpler than B's live loop (about 75%). **Expected: ~72** (60% full; otherwise the
  per-step chart and table ship with plain tabs and no early-step SHAP, ~70).
- **Weakest point:** the "coming into focus" effect in `idea.md` relies on **A1 ranges narrowing**.
  As explained under A, those ranges will be narrow at every step, so they won't visibly shrink.
  The real visual is the probabilities moving away from 50%. Script the demo around that.
- **Claim I disagree with most:** *"3D 19"* and *"~81 total"*. The stepper is a good **Predictive and
  Interpretability** feature, not a 3D feature. Also, the step names: the dataset's group 2 is
  "Symptom and examination", and typical chest pain is a *symptom*, so label the step
  "Symptoms & Exam", not "Exam".
- **Rule risks:**
  - **(1) Leakage times 16.** Sixteen pipelines means sixteen feature lists. Write one `assert` that
    checks every stage's column list against the label columns.
  - **(2) Medical advice.** "Echo and labs cost time and money" can sound like "you can skip the
    echo". Say "how much the *model's* accuracy improves", never "which tests are worth doing".
  - **(3) RWMA.** When Region RWMA arrives at step 4, don't light up a wall region on the heart.
  - **(4) Model choice.** Use the **same model family at every step**. Choosing the best model
    separately per step from the same CV makes the steps look better than they are.
  - **(5) Who the patients are.** All 303 had an angiogram (the test that images the arteries), so
    the per-step numbers apply to that group, not to everyone. Say so in the doc.

---

## 5. Direction E: "How Many Arteries?" (scored as an add-on, since it isn't a full direction)

| Criterion | Baseline + E-full | Why |
|---|---|---|
| Predictive (30) | **21** | One more target with a baseline. Small gain. |
| 3D (25) | **15** | Not on the heart (correctly). |
| Interp (20) | **14** | A "2 of 3 arteries" card is easy to understand. |
| Integration (15) | **10** | |
| Tech (10) | **7** | |
| **Total** | **67** | |

- **Chance of shipping:** ~85% (it's small). **Expected: ~67.**
- **Weakest point:** if E-full is built, a 4-class model on 303 patients will probably reach about
  **40–50% accuracy** (I'm guessing). Next to a 29% baseline that's real, but on a slide "45%
  accuracy" looks weak to a fast-skimming judge.
- **Claim I disagree with most:** *"small to build, but judges remember it"*. E-lite (LAD% + LCX% +
  RCA%) is literally the same as A2(a), so it's not a separate feature. E-full is the only new part,
  and its headline number is unflattering.
- **Rule risks:** the count target is built from LAD/LCX/RCA. That's fine as a **target**, but they
  must never be inputs. Don't stack in-sample vessel predictions as features. **"Clinical context
  in the video" must not drift into treatment talk** (stents vs bypass surgery, PCI vs CABG). That is
  over-claiming.

---

## 6. Combination "A + B-lite" (ideator's recommendation)

| Criterion | Score if shipped | Why |
|---|---|---|
| Predictive (30) | **24** | From A3 (+ A1). |
| 3D (25) | **16** | Color fade from B, otherwise baseline. |
| Interp (20) | **16** | The B2 toggle is the main gain. |
| Integration (15) | **12** | Delta tag + live re-predict. |
| Tech (10) | **8** | |
| **Total** | **76** | |

- **Chance of fully shipping:** ~35%. **Expected: ~72** (35% full at 76; 45% partial at ~72, with A
  done plus only the B2 toggle; 20% overrun at ~66).
- **Weakest point:** it splits Harshavi's few spare hours between two unrelated UI features (A's
  panels and B's sliders). Neither gets polished.
- **Claim I disagree with most:** *"each person gets about 6–8 standout hours"*. Harshavi's actual
  list (range bars + metrics tab + calibration chart + consistency badge + what-if panel + toggle)
  adds up to **8–10 h**, on the person who has the least slack. Also, the B-lite piece shipped first
  ("Apply changes" button) is the required baseline, not an extra.
- **Rule risks:** the sum of A's and B's (over-claiming ranges; cause-and-effect implied by sliders).

---

## 7. Combination "A + D (+E)"

| Criterion | Score if shipped | Why |
|---|---|---|
| Predictive (30) | **26** | A per-step table + calibration/Brier + vessel count, all with the same CV. The strongest validation story of any option. |
| 3D (25) | **16** | Heart re-colors at each step. |
| Interp (20) | **16** | Value of each test, SHAP, and a vessel-count card. |
| Integration (15) | **11** | |
| Tech (10) | **8** | |
| **Total** | **77** | |

- **Chance of fully shipping, as written:** ~30%. Rishi +8–10 h is tight, and Harshavi +7–9 h is too
  much. **Expected: ~73** (30% full; 45% partial at ~74, with D + the metrics panel and no ranges or
  badge; 25% overrun at ~66). It ranks first anyway because its partial version is still strong.
  The parts that get cut (ranges, badge) are the weakest parts.
- **Weakest point:** it has the same overload problem as A + B-lite, and it still does nothing for the
  25% 3D criterion.
- **Claim I disagree with most:** *"~83–84"*. Same optimism as everywhere else: that number assumes
  everything ships and every judge notices every feature.
- **Rule risks:** D's list + A's list (see above).

---

## 8. Ranking (by expected score)

| Rank | Option | If shipped | Chance to fully ship | **Expected** |
|---|---|---|---|---|
| 1 | **A + D (+E)** | 77 | ~30% (partial is still ~74) | **~73** |
| 2 | **D** alone | 74 | ~60% | **~72** |
| 3 | A + B-lite | 76 | ~35% | **~72** |
| 4 | A alone | 71 | ~70% | **~70** |
| 5 | B alone | 72 | ~45% | **~69** |
| 6 | E alone (add-on) | 67 | ~85% | **~67** |
| 7 | C | 70 | ~25% | **~65** |

The baseline alone is about **65**. My uncertainty is about ±3, so ranks 1–3 are effectively tied on
score. What separates them is **which person carries the risk**.

---

## 9. Verdict

**Pick "A + D (+E)", trimmed to "D + A3 + E-lite".** D is the spine. A3 is the metrics panel with
baseline + Brier + a 5-bin calibration chart. E-lite is one line: "expected narrowed arteries: 1.9 of 3".
Make A1 ranges and the A2 badge stretch goals only (the ranges will barely move anyway).
This puts most of the extra work on Rishi, gives Harshavi only ~5 extra hours (stepper tabs +
two Recharts charts), and leads the video with a story that comes from this dataset rather than one
every team will tell. Trimmed, I'd guess **~76 if shipped, ~60% chance, expected ~74**. Drop C entirely.

---

## 10. What would make the winner score higher (max 3)

1. **Spend Harshavi's freed hours on the heart itself, not on features.** 3D is 25% and *no*
   direction improves "anatomical representation". Put LAD down the front groove of the heart, LCX
   around the left side to the back, and RCA around the right side to the bottom (matching the brief's
   "supplies" text), on a light, licensed heart mesh. I'm guessing that's worth +2–4 on 3D, more than
   any standout feature.
2. **Make the probabilities trustworthy before showing them.**
   - Don't let `class_weight="balanced"` distort the colors: calibrate inside the pipeline or drop it.
   - Report the Brier score next to the "always predict the prevalence" Brier, so judges see a
     comparison and not a bare number.
   - Use the **same model family at all 4 steps**.
   - All of this is on out-of-fold predictions.
3. **Freeze the contract tonight with every optional field already in it**, so nothing changes
   silently later:
   - `stage` (1–4) in the `/predict` request
   - `stages` in `/api/schema`
   - `per_stage` + `brier` + `calibration` in `/api/metrics`
   - `vessel_count.expected` in `/predict`
   - a nullable `interval`

   Then script the demo video around the stepper: load a sample at step 1 → click through to step 4
   (watch LAD go red) → per-step AUC chart → SHAP for the selected vessel → disclaimer on screen the
   whole time.
