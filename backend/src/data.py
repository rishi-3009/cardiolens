"""Load the dataset and split it into model inputs (X) and answers (y).

No encoding or scaling happens here on purpose: that is done inside the model pipeline
(src/train.py), so it is re-fitted inside every cross-validation fold (no leakage).
"""
from pathlib import Path

import pandas as pd

from src.config import FEATURE_NAMES, FORBIDDEN_INPUTS, TARGET_COLUMNS

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "z_alizadeh_sani_extension.xlsx"


def load_raw():
    df = pd.read_excel(DATA_FILE)
    df.columns = [str(c).strip() for c in df.columns]  # remove stray spaces in column names
    return df


def load_dataset():
    """Return (X, y): X = the 52 input columns, y = one 0/1 column per target (CAD, LAD, LCX, RCA)."""
    df = load_raw()

    X = df[FEATURE_NAMES].copy()
    assert not set(X.columns) & set(FORBIDDEN_INPUTS), "Label column used as an input!"

    # "CAD"/"Stenotic" -> 1, "Normal" -> 0
    y = pd.DataFrame({target: (df[column] == positive).astype(int)
                      for target, (column, positive) in TARGET_COLUMNS.items()})
    return X, y
