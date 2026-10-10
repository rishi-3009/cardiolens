"""The web API the frontend talks to. Follows contracts/api-contract.md (v1.0).

Run from the backend folder (with the virtual environment active):
    uvicorn src.api:app --reload
Then open http://localhost:8000/docs to try every endpoint in the browser.
"""
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.config import FEATURES, RISK_BANDS, STAGES, TARGETS, VESSELS, features_up_to, schema
from src.data import load_dataset, load_raw
from src.explain import PatientExplainer

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
FEATURE_INFO = {f["name"]: f for f in FEATURES}
FINAL_STAGE = STAGES[-1]["stage"]
VESSEL_KEYS = [v["key"] for v in VESSELS]
BAND_RANK = {band["band"]: i for i, band in enumerate(RISK_BANDS)}  # low 0 < moderate 1 < high 2

DISCLAIMER = ("For decision support and educational purposes only. Not a substitute for formal "
              "diagnostic imaging or a clinician's judgement.")
LABELS = {
    "CAD": {"low": "CAD unlikely", "moderate": "Uncertain", "high": "CAD likely"},
    "vessel": {"low": "Stenosis unlikely", "moderate": "Uncertain", "high": "Stenosis likely"},
}

state = {}  # everything loaded once at startup


# ---- Startup: load models, explainers, metrics ----------------------------------------------
def build_samples(X, pipelines):
    """3 real (anonymous, public) patients for the demo buttons. They were part of training."""
    raw = load_raw()
    stenotic = (raw[VESSEL_KEYS] == "Stenotic")
    full = features_up_to(FINAL_STAGE)
    prob = {t: pipelines[(t, FINAL_STAGE)].predict_proba(X[full])[:, 1] for t in TARGETS}

    picks = [
        ("sample-high", "Narrowing in all 3 arteries (confirmed by angiography)",
         stenotic.all(axis=1), lambda: sum(prob[v] for v in VESSEL_KEYS)),
        ("sample-lad", "Narrowing in the LAD only (confirmed by angiography)",
         stenotic["LAD"] & ~stenotic["LCX"] & ~stenotic["RCA"],
         lambda: prob["LAD"] - prob["LCX"] - prob["RCA"]),
        ("sample-low", "No coronary artery disease (confirmed by angiography)",
         raw["Cath"] == "Normal", lambda: -prob["CAD"]),
    ]
    samples = []
    for sample_id, title, mask, score in picks:
        best = pd.Series(score(), index=X.index)[mask.to_numpy()].idxmax()  # clearest example of its group
        features = {name: (v.item() if hasattr(v, "item") else v) for name, v in X.loc[best, full].items()}
        samples.append({"id": sample_id, "title": title, "features": features})
    return samples


@asynccontextmanager
async def lifespan(app):
    X, _ = load_dataset()
    info = json.loads((MODELS_DIR / "model_info.json").read_text(encoding="utf-8"))
    pipelines, explainers = {}, {}
    for target in TARGETS:
        for s in STAGES:
            k = s["stage"]
            pipelines[(target, k)] = joblib.load(MODELS_DIR / f"{target}_stage{k}.joblib")
            explainers[(target, k)] = PatientExplainer(pipelines[(target, k)], X[features_up_to(k)])
    state.update(
        model_version=info["model_version"],
        pipelines=pipelines,
        explainers=explainers,
        metrics=json.loads((MODELS_DIR / "metrics.json").read_text(encoding="utf-8")),
        global_importance=json.loads((MODELS_DIR / "global_importance.json").read_text(encoding="utf-8")),
        samples=build_samples(X, pipelines),
    )
    explainers[(TARGETS[0], FINAL_STAGE)].explain(X[features_up_to(FINAL_STAGE)].iloc[[0]])  # warm-up (~8 s once)
    yield
    state.clear()


app = FastAPI(title="CardioLens API", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["*"], allow_headers=["*"])


# ---- Errors in the contract's shape: {"error": ..., "detail": ...} ---------------------------
@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail), "detail": None})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request", "detail": str(exc.errors())})


@app.exception_handler(Exception)
async def server_error(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Server error", "detail": repr(exc)})


# ---- Helpers ----------------------------------------------------------------------------------
def band_of(probability):
    for band in RISK_BANDS:
        if probability <= band["max"]:
            return band["band"]
    return RISK_BANDS[-1]["band"]


def prepare_input(features, stage):
    """Check the inputs, fill missing ones with typical values -> (1-row DataFrame, warnings)."""
    allowed = features_up_to(stage)
    warnings, missing, row = [], [], {}

    unknown = [n for n in features if n not in FEATURE_INFO]
    if unknown:
        warnings.append(f"Ignored unknown inputs: {', '.join(unknown)}")
    later = [n for n in features if n in FEATURE_INFO and n not in allowed]
    if later:
        warnings.append(f"Ignored {len(later)} input(s) from later checkup steps (stage {stage} selected).")

    for name in allowed:
        info, value = FEATURE_INFO[name], features.get(name)
        if value is None or value == "":
            row[name] = info["default"]
            missing.append(info["label"])
        elif info["type"] == "numeric":
            try:
                value = float(value)
            except (TypeError, ValueError):
                raise HTTPException(400, f"{info['label']} must be a number, got {value!r}")
            if not info["min"] <= value <= info["max"]:
                warnings.append(f"{info['label']} = {value:g} is outside the range seen in the data "
                                f"({info['min']}–{info['max']}); the estimate may be unreliable.")
            row[name] = value
        else:
            # Accept 1 or "1" for option 1 (HTML forms often send text)
            match = [opt for opt in info["options"] if value == opt or str(value) == str(opt)]
            if not match:
                raise HTTPException(400, f"{info['label']} must be one of {info['options']}, got {value!r}")
            row[name] = match[0]

    if missing:
        warnings.append(f"{len(missing)} missing input(s) filled with typical values: {', '.join(missing)}")
    return pd.DataFrame([row], columns=allowed), warnings


# ---- Endpoints --------------------------------------------------------------------------------
class PredictRequest(BaseModel):
    features: dict[str, Any] = {}
    stage: int | None = Field(default=None, ge=1, le=FINAL_STAGE)


@app.get("/api/health")
def health():
    return {"status": "ok", "model_version": state["model_version"]}


@app.get("/api/schema")
def get_schema():
    return schema(state["model_version"])


@app.get("/api/samples")
def samples():
    return {"samples": state["samples"]}


@app.get("/api/metrics")
def metrics():
    return state["metrics"]


@app.get("/api/global-importance")
def global_importance():
    return state["global_importance"]


@app.post("/api/predict")
def predict(request: PredictRequest):
    stage = request.stage or FINAL_STAGE
    row, warnings = prepare_input(request.features, stage)

    predictions, explanations = {}, {}
    for target in TARGETS:
        probability = float(state["pipelines"][(target, stage)].predict_proba(row)[0, 1])
        band = band_of(probability)
        kind = "CAD" if target == "CAD" else "vessel"
        predictions[target] = {"probability": round(probability, 4), "band": band,
                               "label": LABELS[kind][band], "interval": None}
        explanations[target] = state["explainers"][(target, stage)].explain(row)

    vessel_probs = [predictions[v]["probability"] for v in VESSEL_KEYS]
    max_vessel = max(vessel_probs)
    # Only flag a real disagreement: the riskiest vessel is in a HIGHER band than overall CAD
    # (e.g. LAD "high" but CAD "moderate"). Two "low" results never count as disagreeing.
    consistent = BAND_RANK[band_of(max_vessel)] <= BAND_RANK[predictions["CAD"]["band"]]
    return {
        "model_version": state["model_version"],
        "stage": stage,
        "predictions": predictions,
        # E-lite: expected number of narrowed arteries = sum of the vessel probabilities
        "vessel_count": {"expected": round(sum(vessel_probs), 2), "distribution": None,
                         "method": "sum_of_vessels"},
        # Overall CAD = "at least one vessel narrowed", so CAD % should not be below the highest vessel %
        "consistency": {
            "max_vessel_probability": max_vessel,
            "consistent": consistent,
            "note": ("Overall CAD estimate is consistent with the vessel estimates." if consistent else
                     "The overall CAD estimate is lower than one vessel's estimate. The separate models "
                     "disagree, so treat both with extra caution."),
        },
        "explanations": explanations,
        "warnings": warnings,
        "disclaimer": DISCLAIMER,
    }
