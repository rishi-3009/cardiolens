# Frontend — 3D heart + clinical dashboard (owner: Harshavi)

Loaded automatically when Claude Code works inside `frontend/`. Root `CLAUDE.md` rules still apply.

## Goal
A React web app with an interactive **3D heart** whose **LAD, LCX, RCA** vessels are colored by
predicted stenosis probability, next to a **dashboard** (overall CAD risk, vessel risks, SHAP
explanations, input form, model metrics) and an always-visible **clinical disclaimer**.

## Build order (each step works on its own before the next)
1. Vite + React app runs (`npm run dev` → http://localhost:5173).
2. 3D canvas: heart placeholder + three tube vessels named `LAD`, `LCX`, `RCA`; orbit (rotate/zoom).
3. Colors from `../contracts/mock-predict-response.json` via the risk bands in the contract.
4. Click/hover a vessel → highlight + side panel (name, what it supplies, %, band, top SHAP factors).
5. Dashboard panels: CAD card, vessel list, SHAP bar/waterfall chart, disclaimer banner.
6. Input form built from `/api/schema` (mock schema first) → "Predict" → update everything.
7. Swap mock for the real API (one switch in `src/api.js`: `USE_MOCK = true/false`).
8. Polish: loading + error states, sample-patient buttons, metrics panel, nice camera framing.

## Suggested layout
```
frontend/
  public/models/        # heart.glb (+ credits in docs/resources.md)
  src/
    api.js              # ALL backend calls live here (+ mock switch)
    risk.js             # bands, colors, formatting — from the contract
    components/
      HeartScene.jsx    # <Canvas>, lights, OrbitControls, loads heart + vessels
      Vessel.jsx        # one vessel: color from probability, hover/click
      RiskPanel.jsx     # CAD + vessel cards
      ShapChart.jsx     # contributions chart
      PatientForm.jsx   # built from schema
      Disclaimer.jsx
    App.jsx
```

## Rules specific to the frontend
- Vessel names/keys come from the API (`schema.vessels`); never hard-code the list in several places.
- Show the **number and label**, not color alone.
- Performance: no dedicated GPU. Light meshes, `<Canvas dpr={[1, 2]}>`, no heavy post-processing,
  test on a normal laptop with the browser's performance overlay.
- **Region with RWMA must not be drawn on the heart** — it's an input, not a location.
- The disclaimer is visible on every screen size without scrolling (sticky banner or footer).
- All network calls go through `src/api.js`; components never call `fetch` directly.

## Windows commands Harshavi will use (explain on first use)
```powershell
npm create vite@latest . -- --template react   # create the React app in this folder
npm install                                     # download libraries listed in package.json
npm install three @react-three/fiber @react-three/drei recharts
npm run dev                                     # start the dev server
```
