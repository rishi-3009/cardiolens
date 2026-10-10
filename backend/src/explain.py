"""SHAP explanations: why did the model give this patient this probability?

SHAP splits (this patient's probability - the average patient's probability) into one
contribution per input, in probability units, so base_value + sum(contributions) = probability.

Run from the backend folder to (re)build the global importance chart data (~1 min):
    python -m src.explain
"""
import json
from pathlib import Path

import joblib
import numpy as np
import shap
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier

from src.config import FEATURES, NOMINAL_FEATURES, STAGES, TARGETS, features_up_to
from src.data import load_dataset

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
SEED = 42
BACKGROUND_SIZE = 100  # "average patient" = 100 patients sampled from the dataset
TOP_K = 10             # contract: top 10 contributions per target
FEATURE_INFO = {f["name"]: f for f in FEATURES}


def display_value(feature, value):
    """Human-readable value, e.g. 63 -> "63 years", "Y" -> "Yes", "Fmale" -> "Female"."""
    info = FEATURE_INFO[feature]
    if info["type"] == "numeric":
        number = f"{value:g}" if isinstance(value, (int, float, np.number)) else str(value)
        return f"{number} {info['unit']}"
    labels = dict(zip(info["options"], info["option_labels"]))
    return labels.get(value, str(value))


class PatientExplainer:
    """Explains one saved pipeline (one target at one checkup step)."""

    def __init__(self, pipeline, background_raw):
        self.pipeline = pipeline
        self.prep = pipeline.named_steps["prep"]
        self.model = pipeline.named_steps["model"]
        self.features = list(background_raw.columns)

        # Map each model column back to its input (BBB_LBBB, BBB_RBBB -> BBB)
        columns = self.prep.get_feature_names_out()
        self.column_to_feature = [self._feature_of(c) for c in columns]

        sample = background_raw.sample(min(BACKGROUND_SIZE, len(background_raw)), random_state=SEED)
        background = self.prep.transform(sample)
        if isinstance(self.model, (RandomForestClassifier, GradientBoostingClassifier)):
            # Exact and fast for tree models
            self.explainer = shap.TreeExplainer(self.model, data=background,
                                                feature_perturbation="interventional",
                                                model_output="probability")
            self.kind = "tree"
        else:
            # Works for any model; still adds up exactly to the prediction
            self.explainer = shap.PermutationExplainer(
                lambda rows: self.model.predict_proba(rows)[:, 1], background, seed=SEED)
            self.kind = "permutation"

    @staticmethod
    def _feature_of(column):
        if column in FEATURE_INFO:
            return column
        return next(f for f in NOMINAL_FEATURES if column.startswith(f + "_"))

    def shap_values(self, rows_raw):
        """Per-input SHAP values (probability units) for a DataFrame of raw inputs -> (base, array)."""
        transformed = self.prep.transform(rows_raw[self.features])
        if self.kind == "tree":
            values = self.explainer.shap_values(transformed, check_additivity=False)
            values = values[..., 1] if values.ndim == 3 else values  # keep the "positive" class
            base = self.explainer.expected_value
            base = float(np.atleast_1d(base)[-1])
        else:
            result = self.explainer(transformed, silent=True)
            values, base = result.values, float(np.atleast_1d(result.base_values)[0])

        # Add up model columns that belong to the same input (BBB)
        per_feature = np.zeros((len(transformed), len(self.features)))
        for col, feature in enumerate(self.column_to_feature):
            per_feature[:, self.features.index(feature)] += values[:, col]
        return base, per_feature

    def explain(self, row_raw, top_k=TOP_K):
        """Contract-shaped explanation for ONE patient (a 1-row DataFrame)."""
        base, values = self.shap_values(row_raw)
        contributions = []
        for i in np.argsort(-np.abs(values[0]))[:top_k]:
            feature = self.features[i]
            value = row_raw.iloc[0][feature]
            value = value.item() if hasattr(value, "item") else value  # numpy -> plain Python for JSON
            contributions.append({
                "feature": feature,
                "label": FEATURE_INFO[feature]["label"],
                "value": value,
                "display_value": display_value(feature, value),
                "shap": round(float(values[0, i]), 4),
                "direction": "increases" if values[0, i] > 0 else "decreases",
            })
        return {"base_value": round(base, 4), "contributions": contributions}


def load_explainers():
    """{(target, stage): PatientExplainer} for every saved model."""
    X, _ = load_dataset()
    explainers = {}
    for target in TARGETS:
        for s in STAGES:
            k = s["stage"]
            pipeline = joblib.load(MODELS_DIR / f"{target}_stage{k}.joblib")
            explainers[(target, k)] = PatientExplainer(pipeline, X[features_up_to(k)])
    return explainers


def global_importance():
    """Mean |SHAP| over all patients for the full (step 5) models -> /api/global-importance."""
    X, _ = load_dataset()
    final = STAGES[-1]["stage"]
    features = features_up_to(final)
    result = {"targets": {}}
    for target in TARGETS:
        explainer = PatientExplainer(joblib.load(MODELS_DIR / f"{target}_stage{final}.joblib"), X[features])
        _, values = explainer.shap_values(X[features])
        importance = np.abs(values).mean(axis=0)
        order = np.argsort(-importance)
        result["targets"][target] = [
            {"feature": features[i], "label": FEATURE_INFO[features[i]]["label"],
             "importance": round(float(importance[i]), 4)} for i in order]
        top = ", ".join(f"{features[i]} {importance[i]:.3f}" for i in order[:5])
        print(f"{target}: {top}")
    return result


if __name__ == "__main__":
    data = global_importance()
    (MODELS_DIR / "global_importance.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {MODELS_DIR / 'global_importance.json'}")
