# Decision Log

Every decision that the other teammate needs to know about. Newest at the bottom.
Format: `YYYY-MM-DD · who · decision · why`

- 2026-10-10 · both · Chose **Track A** (Cardiovascular Risk). · Rules allow one track per team; Track A is feasible for a 2-person beginner team in 4.5 days (small CSV dataset, no live judge-chosen data runs).
- 2026-10-10 · both · Split: **Rishi = ML + backend API**, **Harshavi = 3D heart + dashboard**. · Matches interests; the API contract lets both work in parallel.
- 2026-10-10 · both · Default stack: Python/scikit-learn/SHAP/FastAPI + React/Vite/React Three Fiber. · Popular, beginner-friendly, well documented.
- 2026-10-10 · both · Start with procedural LAD/LCX/RCA tubes over a heart mesh; upgrade mesh later. · Guarantees separate, correctly named vessel objects from day 1.
- 2026-10-10 · both (confirmed by Rishi) · Direction: **A + D + E** from `docs/idea.md`. A = "Honest Heart": in-app validation panel, uncertainty ranges, CAD-vs-vessel consistency check. D = "Step-by-Step Checkup": models per cumulative feature step (History → Exam → ECG → Labs & Echo), with a stepper and a "value of each test" chart. E = "How many arteries?": estimated number of narrowed vessels. Suggested build order from `docs/critique.md`: D → A3 metrics/calibration → E-lite, then A1 ranges, A2 consistency badge and E-full if time. · Ranked #1 by the critic (~73 expected / 100). It's distinctive because it's built on the dataset's own feature groups, and most extra work falls on the backend, where there are spare hours. Mandatory baseline still comes first. Scope guards: never word results as "skip this test"; no treatment advice in the vessel-count card; a label-column check on every step's input list.
- 2026-10-10 · Rishi · **5 checkup steps**: History → Exam & symptoms → ECG → Blood tests → Echo. Echo (EF-TTE, Region RWMA, VHD) is its own step, separate from blood tests. · Matches a real hospital visit; echo is a separate test in real life.
- 2026-10-10 · Rishi · **Drop Weight and Length, keep BMI; drop Exertional CP** → 52 model inputs. · BMI is computed from Weight/Length, and keeping all three splits SHAP credit. Exertional CP is "N" for all 303 patients.
- 2026-10-10 · Rishi · **Contract v0.2** (for Harshavi to review; freeze as v1.0 tonight). Changes from v0.1:
  - real 52-feature list, with features sent as their exact dataset values (e.g. `"N"/"Y"`, `"Fmale"`);
  - `stages` in `/api/schema`, and feature `group` = step key;
  - optional `stage` in the `/predict` request;
  - optional `interval`, `vessel_count` and `consistency` in the `/predict` response;
  - optional `brier`, `calibration`, `by_stage` and `vessel_count` in `/api/metrics`;
  - new `contracts/mock-schema.json`, generated from `backend/src/config.py`; the mock prediction updated to match.

  All additions are optional fields, so code built on v0.1 still works. · Needed for directions A + D + E.
