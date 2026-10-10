"""Custom model pieces used inside the training pipelines."""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict


def _logit(p):
    p = np.clip(p, 1e-3, 1 - 1e-3)
    return np.log(p / (1 - p))


class CalibratedForest(BaseEstimator, ClassifierMixin):
    """A random forest whose probabilities are corrected so that "70%" really means ~70%.

    Random forests tend to be timid (squeeze probabilities toward the middle). We fix this with
    "Platt scaling": a tiny logistic regression that maps the forest's probability to a corrected one.
    The mapping is learned from out-of-fold predictions (the forest never saw those patients), and only
    on the training data it is given, so it stays leak-free inside cross-validation.
    """

    def __init__(self, forest, cv=5, random_state=42):
        self.forest = forest
        self.cv = cv
        self.random_state = random_state

    def fit(self, X, y):
        y = np.asarray(y)
        folds = StratifiedKFold(self.cv, shuffle=True, random_state=self.random_state)
        out_of_fold = cross_val_predict(clone(self.forest), X, y, cv=folds, method="predict_proba")[:, 1]
        self.calibrator_ = LogisticRegression(C=1e6).fit(_logit(out_of_fold)[:, None], y)
        self.forest_ = clone(self.forest).fit(X, y)
        self.classes_ = self.forest_.classes_
        return self

    def calibrate(self, raw_probability):
        """Raw forest probability -> corrected probability (always increasing, so order is kept)."""
        raw = np.asarray(raw_probability, dtype=float)
        return self.calibrator_.predict_proba(_logit(raw).reshape(-1, 1))[:, 1].reshape(raw.shape)

    def predict_proba(self, X):
        p = self.calibrate(self.forest_.predict_proba(X)[:, 1])
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
