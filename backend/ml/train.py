"""
Dev 1's training script.
Run this once to train and save all models:
    python ml/train.py
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(MODELS_DIR, exist_ok=True)


def generate_synthetic_data(n=3000) -> pd.DataFrame:
    """
    Synthetic dataset calibrated to literature-reported injury rates.
    Replace/augment with real Kaggle data when available.
    """
    np.random.seed(42)
    df = pd.DataFrame({
        "cycle_phase":          np.random.choice([0, 1, 2, 3], n, p=[0.2, 0.35, 0.15, 0.30]),
        "acute_chronic_ratio":  np.random.normal(1.1, 0.3, n).clip(0.4, 2.5),
        "knee_soreness":        np.random.randint(0, 11, n),
        "hamstring_soreness":   np.random.randint(0, 11, n),
        "groin_soreness":       np.random.randint(0, 11, n),
        "session_rpe":          np.random.normal(6.5, 1.5, n).clip(1, 10),
        "weekly_load":          np.random.normal(250, 80, n).clip(50, 600),
        "days_since_last_rest": np.random.randint(0, 10, n),
    })

    # ACL risk — higher in ovulatory phase + high load
    acl_prob = (
        0.04
        + 0.30 * (df["cycle_phase"] == 2)
        + 0.25 * (df["acute_chronic_ratio"] > 1.5)
        + 0.10 * (df["knee_soreness"] > 7)
        + 0.05 * (df["session_rpe"] > 8)
    ).clip(0, 0.95)
    df["acl_injury"] = (np.random.random(n) < acl_prob).astype(int)

    # Soft tissue risk — driven more by soreness + load
    soft_prob = (
        0.05
        + 0.20 * (df["acute_chronic_ratio"] > 1.4)
        + 0.15 * (df["hamstring_soreness"] > 6)
        + 0.10 * (df["groin_soreness"] > 6)
        + 0.10 * (df["days_since_last_rest"] > 6)
    ).clip(0, 0.95)
    df["soft_tissue_injury"] = (np.random.random(n) < soft_prob).astype(int)

    # Overtraining — driven by RPE + load + rest
    ot_prob = (
        0.05
        + 0.25 * (df["session_rpe"] > 8)
        + 0.20 * (df["weekly_load"] > 350)
        + 0.20 * (df["days_since_last_rest"] > 5)
    ).clip(0, 0.95)
    df["overtraining"] = (np.random.random(n) < ot_prob).astype(int)

    return df


FEATURES = [
    "acute_chronic_ratio", "cycle_phase", "knee_soreness",
    "hamstring_soreness", "session_rpe", "days_since_last_rest", "weekly_load",
]


def train():
    print("Loading data...")
    # TODO: load real Kaggle data here and merge with synthetic
    # real_df = pd.read_csv(f"{DATA_DIR}/raw/kaggle_injury.csv")
    df = generate_synthetic_data(n=3000)
    print(f"Dataset: {len(df)} rows — ACL: {df.acl_injury.mean():.1%}, "
          f"Soft: {df.soft_tissue_injury.mean():.1%}, OT: {df.overtraining.mean():.1%}")

    X = df[FEATURES]
    X_train, X_test, y_acl_train, y_acl_test = train_test_split(X, df["acl_injury"], test_size=0.2, random_state=42)

    # ── Train 3 logistic regression models ───────────────────
    for target in ["acl_injury", "soft_tissue_injury", "overtraining"]:
        name = target.replace("_injury", "").replace("training", "ot")
        print(f"\nTraining {name} model...")
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, df.loc[X_train.index, target])
        preds = model.predict(X_test)
        print(classification_report(df.loc[X_test.index, target], preds, zero_division=0))
        fname = f"{MODELS_DIR}/{name}_model.pkl"
        joblib.dump(model, fname)
        print(f"Saved → {fname}")

    # ── Train Random Forest for feature importance ────────────
    print("\nTraining Random Forest (feature importance)...")
    combined = ((df["acl_injury"] | df["soft_tissue_injury"]).astype(int))
    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(X_train, combined.loc[X_train.index])
    joblib.dump(rf, f"{MODELS_DIR}/rf_importance.pkl")
    print(f"Saved → {MODELS_DIR}/rf_importance.pkl")

    # Print feature importances
    print("\nFeature importances:")
    for feat, imp in sorted(zip(FEATURES, rf.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat:<30} {imp:.3f}")

    print("\nAll models saved. Hand models/ folder to Dev 2.")


if __name__ == "__main__":
    train()
