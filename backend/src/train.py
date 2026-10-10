"""Train and evaluate the CAD / LAD / LCX / RCA models, and save them.

Run from the backend folder (with the virtual environment active):
    python -m src.train

What it does, per target:
1. Compares 3 model types with repeated stratified 5-fold cross-validation (10 repeats).
2. Picks one model type (best ROC-AUC; logistic regression wins if within 0.01 - easier to explain).
3. Evaluates that model type at every checkup step (step 1 = history only ... step 5 = everything).
4. Fits the final models on all 303 patients and saves them + metrics into backend/models/.

All preprocessing lives INSIDE the scikit-learn Pipeline, so in every fold it is fitted on the
training patients only and never sees the test patients (no leakage).
"""
import json
import warnings
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from src.config import FEATURES, FORBIDDEN_INPUTS, NOMINAL_FEATURES, STAGES, TARGETS, features_up_to
from src.data import load_dataset

SEED = 42                    # fixed random seed -> same results every run
N_SPLITS, N_REPEATS = 5, 10  # 5 folds x 10 repeats = 50 train/test rounds
SIMPLER_MODEL_MARGIN = 0.01  # prefer logistic regression if its ROC-AUC is this close to the best
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

FEATURE_INFO = {f["name"]: f for f in FEATURES}
FINAL_STAGE = STAGES[-1]["stage"]
SIMPLE_MODEL = "LogisticRegression"
CONTRACT_METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]


# ---- Pipeline = preprocessing + model ---------------------------------------------------
def build_preprocessor(features):
    """Turn the raw inputs into numbers the models can use."""
    numeric = [f for f in features if FEATURE_INFO[f]["type"] == "numeric"]
    nominal = [f for f in features if f in NOMINAL_FEATURES]
    coded = [f for f in features if f not in numeric and f not in nominal]
    return ColumnTransformer([
        # numbers -> same scale (mean 0, spread 1)
        ("numeric", StandardScaler(), numeric),
        # N/Y, Male/Fmale, 0/1, VHD none..severe -> 0, 1, 2... in the order listed in config.py
        ("coded", Pipeline([
            ("encode", OrdinalEncoder(categories=[FEATURE_INFO[f]["options"] for f in coded])),
            ("scale", StandardScaler()),
        ]), coded),
        # BBB (no natural order) -> yes/no columns for LBBB and RBBB ("N" is the reference)
        ("nominal", OneHotEncoder(categories=[FEATURE_INFO[f]["options"] for f in nominal],
                                  drop="first"), nominal),
    ], verbose_feature_names_out=False)


def candidate_models():
    return {
        # Picks its own regularization strength with an inner 5-fold CV on the training part only
        "LogisticRegression": LogisticRegressionCV(
            Cs=np.logspace(-3, 1, 9), l1_ratios=(0,),  # l1_ratio 0 = plain L2 regularization
            cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
            scoring="neg_log_loss", max_iter=5000, use_legacy_attributes=False),
        "RandomForest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, random_state=SEED),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=2, learning_rate=0.05, subsample=0.8, random_state=SEED),
    }


def make_pipeline(model_name, features):
    return Pipeline([
        ("prep", build_preprocessor(features)),
        ("model", clone(candidate_models()[model_name])),
    ])


# ---- Cross-validation ---------------------------------------------------------------------
def _score_fold(pipeline, X, y, train_idx, test_idx):
    """Train on one part, test on the held-out part. Returns scores + test predictions."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # quiet convergence chatter inside worker processes
        model = clone(pipeline).fit(X.iloc[train_idx], y.iloc[train_idx])
        prob = model.predict_proba(X.iloc[test_idx])[:, 1]
    true = y.iloc[test_idx].to_numpy()
    pred = (prob >= 0.5).astype(int)
    scores = {
        "accuracy": accuracy_score(true, pred),
        "precision": precision_score(true, pred, zero_division=0),
        "recall": recall_score(true, pred),
        "f1": f1_score(true, pred),
        "roc_auc": roc_auc_score(true, prob),
        "pr_auc": average_precision_score(true, prob),
        "brier": brier_score_loss(true, prob),
    }
    return scores, true, prob


def cross_validate(model_name, features, X, y):
    """Repeated stratified k-fold CV. Returns {metric: [mean, std]} and the out-of-fold predictions."""
    assert not set(features) & set(FORBIDDEN_INPUTS), "Label column used as an input!"
    pipeline = make_pipeline(model_name, features)
    # Same seed for every model and target -> all are tested on exactly the same splits
    cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
    results = Parallel(n_jobs=-1)(
        delayed(_score_fold)(pipeline, X[features], y, train_idx, test_idx)
        for train_idx, test_idx in cv.split(X, y))

    folds = [scores for scores, _, _ in results]
    summary = {metric: [round(float(np.mean([f[metric] for f in folds])), 4),
                        round(float(np.std([f[metric] for f in folds])), 4)]
               for metric in folds[0]}
    oof_true = np.concatenate([true for _, true, _ in results])
    oof_prob = np.concatenate([prob for _, _, prob in results])
    return summary, oof_true, oof_prob


def calibration_bins(true, prob, n_bins=5):
    """'When the model says ~X%, how often was it really positive?' on out-of-fold predictions.

    Predictions are pooled over all repeats; `count` is divided by N_REPEATS so it reads as patients.
    """
    edges = np.linspace(0, 1, n_bins + 1)
    which_bin = np.clip(np.digitize(prob, edges[1:-1]), 0, n_bins - 1)
    bins = []
    for b in range(n_bins):
        in_bin = which_bin == b
        if in_bin.any():
            bins.append({"predicted": round(float(prob[in_bin].mean()), 3),
                         "observed": round(float(true[in_bin].mean()), 3),
                         "count": int(round(in_bin.sum() / N_REPEATS))})
    return bins


def fmt(mean_std):
    return f"{mean_std[0]:.3f} +/- {mean_std[1]:.3f}"  # plain ASCII so Windows log files stay readable


# ---- Main ---------------------------------------------------------------------------------
def main():
    X, y = load_dataset()
    MODELS_DIR.mkdir(exist_ok=True)
    all_features = features_up_to(FINAL_STAGE)
    validation = (f"Repeated stratified {N_SPLITS}-fold CV ({N_REPEATS} repeats), n={len(X)}. "
                  "Model type chosen per target on the same CV (small optimistic bias).")

    metrics = {"validation": validation, "targets": {}}                  # -> /api/metrics (contract shape)
    details = {"validation": validation, "seed": SEED, "targets": {}}    # -> everything, for the report
    info = {"model_version": datetime.now().strftime("%Y-%m-%d-%H%M"),
            "stages": {s["stage"]: features_up_to(s["stage"]) for s in STAGES},
            "targets": {}}

    print(f"{len(X)} patients, {len(all_features)} inputs. {validation}")
    for target in TARGETS:
        yt = y[target]
        baseline = round(float(max(yt.mean(), 1 - yt.mean())), 4)
        print(f"\n=== {target}: {yt.sum()} positive / {len(yt)}  "
              f"(always guessing the majority = {baseline:.1%} accuracy) ===")

        # 1. Compare the model types, using all inputs
        comparison = {}
        for name in candidate_models():
            comparison[name] = cross_validate(name, all_features, X, yt)
            s = comparison[name][0]
            print(f"  {name:<19} ROC-AUC {fmt(s['roc_auc'])}   F1 {fmt(s['f1'])}   "
                  f"accuracy {fmt(s['accuracy'])}   Brier {fmt(s['brier'])}")

        # 2. Pick one (prefer the simple model if it is close)
        best = max(comparison, key=lambda n: comparison[n][0]["roc_auc"][0])
        gap = comparison[best][0]["roc_auc"][0] - comparison[SIMPLE_MODEL][0]["roc_auc"][0]
        chosen = SIMPLE_MODEL if gap <= SIMPLER_MODEL_MARGIN else best
        print(f"  -> chosen: {chosen}")

        # 3. Same model type at every checkup step
        stage_results = {}
        for s in STAGES:
            k = s["stage"]
            if k == FINAL_STAGE:
                stage_results[k] = comparison[chosen][0]
            else:
                stage_results[k] = cross_validate(chosen, features_up_to(k), X, yt)[0]
        print("  by step (ROC-AUC): " + "  ".join(
            f"{s['label']} {stage_results[s['stage']]['roc_auc'][0]:.3f}" for s in STAGES))

        # 4. Final models on all patients, one per step
        for s in STAGES:
            k = s["stage"]
            features = features_up_to(k)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pipeline = make_pipeline(chosen, features).fit(X[features], yt)
            joblib.dump(pipeline, MODELS_DIR / f"{target}_stage{k}.joblib")

        final, oof_true, oof_prob = comparison[chosen]
        metrics["targets"][target] = {
            "model": chosen,
            **{m: final[m] for m in CONTRACT_METRICS},
            "baseline_accuracy": baseline,
            "brier": final["brier"],
            "calibration": calibration_bins(oof_true, oof_prob),
            "by_stage": [{"stage": k, "roc_auc": stage_results[k]["roc_auc"]} for k in stage_results],
        }
        details["targets"][target] = {
            "positives": int(yt.sum()), "baseline_accuracy": baseline, "chosen": chosen,
            "comparison": {name: res[0] for name, res in comparison.items()},
            "by_stage": {k: v for k, v in stage_results.items()},
        }
        info["targets"][target] = {"model": chosen,
                                   "files": {s["stage"]: f"{target}_stage{s['stage']}.joblib" for s in STAGES}}

    for filename, content in [("metrics.json", metrics), ("cv_details.json", details), ("model_info.json", info)]:
        (MODELS_DIR / filename).write_text(json.dumps(content, indent=2), encoding="utf-8")

    print("\n=== Summary (all inputs, chosen model) ===")
    print(f"{'target':<7}{'model':<20}{'ROC-AUC':<17}{'F1':<17}{'accuracy':<17}baseline")
    for target, m in metrics["targets"].items():
        print(f"{target:<7}{m['model']:<20}{fmt(m['roc_auc']):<17}{fmt(m['f1']):<17}"
              f"{fmt(m['accuracy']):<17}{m['baseline_accuracy']:.3f}")
    print(f"\nSaved {len(TARGETS) * len(STAGES)} models + metrics.json, cv_details.json, model_info.json "
          f"to {MODELS_DIR}")


if __name__ == "__main__":
    main()
