"""First look at the dataset. Read-only: prints a report, changes nothing.

Run from the backend folder (with the virtual environment active):
    python src/inspect_data.py
"""
from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "z_alizadeh_sani_extension.xlsx"

# Label columns (what we predict). These must NEVER be model inputs.
LABEL_NAMES = ["Cath", "LAD", "LCX", "RCA"]


def main():
    df = pd.read_excel(DATA_FILE)
    df.columns = [str(c).strip() for c in df.columns]  # remove stray spaces in column names

    print(f"Rows (patients): {len(df)}   Columns: {df.shape[1]}\n")

    # 1. Every column: its type, how many different values, how many are missing
    print("=== All columns ===")
    print(f"{'#':>3}  {'column':<28} {'type':<8} {'unique':>6} {'missing':>7}  examples")
    for i, col in enumerate(df.columns, start=1):
        s = df[col]
        examples = ", ".join(str(v) for v in s.dropna().unique()[:4])
        print(f"{i:>3}  {col:<28} {str(s.dtype):<8} {s.nunique():>6} {s.isna().sum():>7}  {examples}")

    # 2. The label columns and how balanced they are
    print("\n=== Label columns (targets - never inputs) ===")
    for name in LABEL_NAMES:
        matches = [c for c in df.columns if c.lower() == name.lower()]
        if not matches:
            print(f"!! {name}: NOT FOUND - check the column list above")
            continue
        counts = df[matches[0]].value_counts(dropna=False)
        pct = (counts / len(df) * 100).round(1)
        print(f"\n{matches[0]}:")
        for value, n in counts.items():
            print(f"   {str(value):<12} {n:>4}  ({pct[value]}%)")

    # 3. Text (non-number) columns - these will need encoding before training
    text_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    print(f"\n=== Text columns ({len(text_cols)}) - need converting to numbers ===")
    for col in text_cols:
        print(f"   {col:<28} {sorted(df[col].dropna().astype(str).unique())}")

    # 4. Number columns - range of values
    num = df.select_dtypes("number")
    print(f"\n=== Number columns ({num.shape[1]}) - min / median / max ===")
    for col in num.columns:
        print(f"   {col:<28} {num[col].min():>8g} {num[col].median():>8g} {num[col].max():>8g}")


if __name__ == "__main__":
    main()
