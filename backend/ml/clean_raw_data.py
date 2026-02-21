"""
clean_raw_data.py

Cleans each raw training dataset and writes the result to
backend/training_data/cleaned/.  The originals are never modified.

Cleaning steps applied to every file
--------------------------------------
1. Drop fully duplicate rows
2. Drop columns where > 40% of values are missing
3. Fill remaining numeric NaNs with column median
4. Fill remaining categorical NaNs with column mode

Additional step for multimodal dataset
---------------------------------------
- Filter to female athletes only (gender == "Female") before any cleaning
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE        = Path(__file__).resolve().parents[1]   # backend/
DATA        = BASE / "training_data"
CLEANED_DIR = DATA / "cleaned"
CLEANED_DIR.mkdir(exist_ok=True)

MISSING_DROP_THRESHOLD = 0.40   # drop column if > 40% of values are missing

# ── Helpers ───────────────────────────────────────────────────────────────────

def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def _report_missing(df: pd.DataFrame, label: str) -> None:
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print(f"  [{label}] No missing values.")
    else:
        print(f"  [{label}] Missing values:")
        for col, count in missing.items():
            pct = count / len(df) * 100
            print(f"    {col:40s}: {count:5d}  ({pct:.1f}%)")


def clean_dataset(
    path: Path,
    *,
    female_only: bool = False,
    gender_col: str = "gender",
) -> pd.DataFrame:
    """
    Load, clean, and return a DataFrame.  Also writes the cleaned CSV.

    Parameters
    ----------
    path        : path to the raw CSV
    female_only : if True, filter to rows where gender_col == "Female" first
    gender_col  : name of the gender column (dataset-specific)
    """
    _section(path.name)

    # ── Load ──────────────────────────────────────────────────────────────────
    df = pd.read_csv(path)
    print(f"  Shape (raw):                   {df.shape}")

    # ── Female filter (multimodal only) ───────────────────────────────────────
    if female_only:
        before = len(df)
        df = df[df[gender_col] == "Female"].copy()
        print(f"  Rows after female filter:      {len(df)}  (dropped {before - len(df)} non-female rows)")

    # ── Step 1: drop fully duplicate rows ────────────────────────────────────
    n_before = len(df)
    df = df.drop_duplicates()
    n_dupes = n_before - len(df)
    print(f"  Duplicate rows dropped:        {n_dupes}")

    # ── Step 2: drop high-missingness columns (> 40%) ────────────────────────
    missing_frac = df.isnull().mean()
    cols_to_drop = missing_frac[missing_frac > MISSING_DROP_THRESHOLD].index.tolist()
    if cols_to_drop:
        print(f"  Columns dropped (>{MISSING_DROP_THRESHOLD*100:.0f}% missing): {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)
    else:
        print(f"  Columns dropped (>{MISSING_DROP_THRESHOLD*100:.0f}% missing): none")

    # ── Report remaining missingness before imputation ────────────────────────
    _report_missing(df, "before imputation")

    # ── Step 3 & 4: impute numeric → median, categorical → mode ──────────────
    numeric_cols     = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns

    numeric_filled = 0
    for col in numeric_cols:
        n_null = df[col].isnull().sum()
        if n_null:
            df[col] = df[col].fillna(df[col].median())
            numeric_filled += n_null

    categorical_filled = 0
    for col in categorical_cols:
        n_null = df[col].isnull().sum()
        if n_null:
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val.iloc[0])
                categorical_filled += n_null

    print(f"  Numeric NaNs filled (median):  {numeric_filled}")
    print(f"  Categorical NaNs filled (mode):{categorical_filled}")

    # ── Final shape and null check ─────────────────────────────────────────────
    print(f"  Shape (cleaned):               {df.shape}")
    remaining_nulls = df.isnull().sum().sum()
    print(f"  Remaining nulls:               {remaining_nulls}")

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = CLEANED_DIR / f"cleaned_{path.name}"
    df.to_csv(out_path, index=False)
    print(f"  Saved →  {out_path.relative_to(BASE.parent)}")

    return df


# ── Run all datasets ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Cleaning raw datasets")
    print(f"Output directory: {CLEANED_DIR}")

    # 1. Multimodal sports injury — female athletes only
    clean_dataset(
        DATA / "multimodal_sports_injury" / "multimodal_sports_injury_dataset.csv",
        female_only=True,
        gender_col="gender",
    )

    # 2. Collegiate athlete injury
    clean_dataset(
        DATA / "collegiate_athlete_injury_dataset.csv",
    )

    # 3. Menstrual Period Log
    clean_dataset(
        DATA / "menstrual_data_1" / "Period_Log.csv",
    )

    # 4. User Profile
    clean_dataset(
        DATA / "menstrual_data_1" / "User_Profile.csv",
    )

    # 5. Menstrual cycle dataset with factors
    clean_dataset(
        DATA / "menstrual_data_2" / "menstrual_cycle_dataset_with_factors.csv",
    )

    print(f"\n{'=' * 60}")
    print("  All datasets cleaned.")
    print(f"  Cleaned files written to: {CLEANED_DIR}")
    print(f"{'=' * 60}\n")
