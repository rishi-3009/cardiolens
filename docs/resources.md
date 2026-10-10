# Resources (datasets, 3D meshes, libraries)

Record here every external thing we use, with its license. The README credits section is built from this file.

## Dataset
- **Extension of Z-Alizadeh Sani dataset** — UCI ML Repository, dataset id 411
  https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset
  - 303 patients, 59 features in four groups: demographic, symptom & examination, ECG, laboratory & echo.
  - Labels: LAD, LCX, RCA stenosis + Cath (angiography result) + overall CAD (last column).
  - File: `extention of Z-Alizadeh sani dataset.xlsx` (~128 KB) → save into `backend/data/raw/`.
  - **License: CC BY 4.0** — free to use with credit.
  - Citation: Alizadehsani, R., Roshanzamir, M., & Sani, Z. *extention of Z-Alizadeh sani dataset*.
    UCI Machine Learning Repository.
  - Mirrors: Mendeley Data (DOI 10.17632/9k56pwtvz9.1), Kaggle.

## 3D heart / coronary meshes
The key need: **LAD, LCX and RCA must be separate, selectable objects.** Most free heart models
have the coronaries merged into one mesh, so plan for that.

| Option | Pros | Cons | License |
|---|---|---|---|
| **A. Procedural vessels (recommended start)** — any heart mesh + draw LAD/LCX/RCA ourselves as `TubeGeometry` along hand-placed curves | Guaranteed separate + named; tiny; works day 1 | Less realistic; curves must be placed carefully | Ours |
| **B. BodyParts3D** (lifesciencedb.jp/bp3d) — anatomy split into separate OBJ parts | Real anatomy, parts already separated | Need to find the right part IDs, convert OBJ→GLB, align parts | CC BY-SA 2.1 Japan (credit + share-alike) |
| **C. Sketchfab** heart models | Often beautiful | License varies per model (check "Downloadable" + CC license); coronaries usually merged | Per model |
| **D. NIH 3D Print Exchange** | Medical-grade sources | Often heavy STL; may need cleanup | Per model |

Recommendation: build with **A** first so integration works immediately; upgrade the heart body to
B/C later if time allows, keeping the vessel objects named `LAD`, `LCX`, `RCA`.

Tools: Blender (free) to inspect/split/rename meshes and export GLB; https://gltf.report or
`gltf-transform` to compress.

## Libraries
- Backend: pandas, scikit-learn, shap, fastapi, uvicorn, joblib, openpyxl (to read .xlsx)
- Frontend: react, vite, three, @react-three/fiber, @react-three/drei, recharts

## Mesh credits (fill in when chosen)
- Heart body: _source, author, license, URL_
- Vessels: _source / procedural_
