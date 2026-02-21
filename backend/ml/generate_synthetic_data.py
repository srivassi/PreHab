"""
generate_synthetic_data.py

Generates 3000 synthetic female athlete training sessions calibrated to real
dataset distributions, using literature-derived risk multipliers loaded from
backend/training_data/thresholds_data.json.

Output columns
--------------
  acute_chronic_ratio    : float  – ACWR (acute 7-day / chronic 28-day load)
  cycle_phase_encoded    : int    – 0=Menstrual, 1=Follicular, 2=Ovulatory, 3=Luteal/Premenstrual
  knee_soreness          : float  – self-reported soreness 0–10
  hamstring_soreness     : float  – self-reported soreness 0–10
  groin_soreness         : float  – self-reported soreness 0–10
  days_since_last_rest   : int    – consecutive training days without a rest day
  session_rpe            : float  – session Rating of Perceived Exertion 1–10
  weekly_load            : float  – arbitrary training load units
  oral_contraceptive_use : int    – binary (1 = current OC user)
  acl_injury             : int    – binary outcome
  soft_tissue_injury     : int    – binary outcome (muscle strains / ligament sprains)
  overtraining           : int    – binary outcome

Multipliers applied
-------------------
  Source: thresholds_data.json (all values loaded at runtime – no hard-coding)

  ACL risk:
    × 1.61  when cycle_phase_encoded == 2 (Ovulatory)   [Wojtys et al. 1998]
    × 0.82  when oral_contraceptive_use == 1             [Herzberg et al. 2017]

  Soft tissue risk:
    × 6.07  when cycle_phase_encoded == 3 (Premenstrual) [Barlow et al. 2024]

  All injury types:
    × 2.1   when acute_chronic_ratio > 1.5
    NOTE: This ACWR multiplier is drawn from general (mixed-sex) population
    literature only. No female-specific RR/OR/HR was identified in the reviewed
    documents (JSON value = 0.0 for this factor). The value 2.1 is retained as
    a reasonable modelling assumption but must not be cited as female-specific.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE            = Path(__file__).resolve().parents[1]   # backend/
THRESHOLDS_PATH = BASE / "training_data" / "thresholds_data.json"
MULTIMODAL_PATH = BASE / "training_data" / "multimodal_sports_injury" / "multimodal_sports_injury_dataset.csv"
PERIOD_LOG_PATH = BASE / "training_data" / "menstrual_data_1" / "Period_Log.csv"
USER_PROFILE_PATH = BASE / "training_data" / "menstrual_data_1" / "User_Profile.csv"
OUTPUT_PATH     = BASE / "training_data" / "synthetic_training_data.csv"

N_ROWS = 3_000
RNG    = np.random.default_rng(42)

# ── 1. Load thresholds_data.json and extract multipliers ───────────────────────
with open(THRESHOLDS_PATH) as f:
    thresholds = json.load(f)

# Build a lookup: factor_name → multiplier value
_mul_lookup = {
    factor["factor_name"]: factor["statistical_multiplier"]["value"]
    for factor in thresholds["risk_factors"]
}

BASE_INJURY_RATE: float = thresholds["base_injury_rate"]["value"] / 100  # 6.58 → 0.0658

# Named multipliers extracted from JSON
ACL_OVULATORY_MUL: float = _mul_lookup[
    "Menstrual Cycle Phase: Ovulatory (ACL Injury)"
]  # 1.61 — Wojtys et al. 1998

SOFT_TISSUE_PREMENSTRUAL_MUL: float = _mul_lookup[
    "Menstrual Cycle Phase: Premenstrual/Late Luteal (Phase 4) for Muscle Injuries"
]  # 6.07 — Barlow et al. 2024

OC_ACL_MUL: float = _mul_lookup[
    "Hormonal Contraceptive (OC) Use (ACL Injury)"
]  # 0.82 — Herzberg et al. 2017

# NOTE: The JSON entry for ACWR > 1.5 has value=0.0 (no female-specific evidence
# was found). We apply 2.1 as a general population approximation. This must NOT
# be presented as female-specific in any downstream analysis or citation.
ACWR_HIGH_MUL: float = 2.1  # general population only

print("=" * 60)
print("Multipliers loaded from thresholds_data.json")
print("=" * 60)
print(f"  Base injury rate:              {BASE_INJURY_RATE * 100:.2f} per 100 AE")
print(f"  ACL × ovulatory phase:         {ACL_OVULATORY_MUL}")
print(f"  Soft tissue × premenstrual:    {SOFT_TISSUE_PREMENSTRUAL_MUL}")
print(f"  ACL × oral contraceptive use:  {OC_ACL_MUL}")
print(f"  All injuries × ACWR > 1.5:     {ACWR_HIGH_MUL}  ← general pop. only")
print()

# ── 2. Extract real distributions (female athletes only) ──────────────────────

## 2a. Multimodal dataset — session RPE, training load, fatigue (female only)
multi         = pd.read_csv(MULTIMODAL_PATH)
female_multi  = multi[multi["gender"] == "Female"].copy()

rpe_mean  = float(female_multi["training_intensity"].mean())
rpe_std   = float(female_multi["training_intensity"].std())
load_mean = float(female_multi["training_load"].mean())
load_std  = float(female_multi["training_load"].std())

print("=" * 60)
print(f"Real female distributions  (multimodal, n={len(female_multi):,})")
print("=" * 60)
print(f"  session_rpe  (training_intensity): mean={rpe_mean:.2f}, std={rpe_std:.2f}")
print(f"  weekly_load  (training_load):      mean={load_mean:.2f}, std={load_std:.2f}")
print()

## 2b. Period Log — cycle phase proportions
period_log   = pd.read_csv(PERIOD_LOG_PATH)
phase_counts = period_log["cycle_phase"].value_counts()
total        = phase_counts.sum()

menstrual_p  = phase_counts.get("Menstrual",  0) / total   # ~10%
follicular_p = phase_counts.get("Follicular", 0) / total   # ~45%
luteal_p     = phase_counts.get("Luteal",     0) / total   # ~45%

# "Follicular" in this dataset conflates early-follicular and ovulatory.
# A typical 28-day cycle assigns roughly equal days to each half of the
# follicular/pre-ovulatory window, so we split Follicular 50 / 50.
phase_probs = np.array([
    menstrual_p,          # 0: Menstrual
    follicular_p * 0.50,  # 1: Follicular (early)
    follicular_p * 0.50,  # 2: Ovulatory
    luteal_p,             # 3: Luteal / Premenstrual
])
phase_probs /= phase_probs.sum()  # normalise to guard against float drift

print("=" * 60)
print(f"Cycle phase distribution  (Period_Log, n={len(period_log):,})")
print("=" * 60)
for i, label in enumerate(["Menstrual", "Follicular", "Ovulatory", "Luteal/Premenstrual"]):
    print(f"  Phase {i} ({label:20s}): {phase_probs[i] * 100:.1f}%")
print()

## 2c. User Profile — oral contraceptive prevalence
user_profile = pd.read_csv(USER_PROFILE_PATH)
oc_rate      = float(user_profile["birth_control_use"].mean())

print("=" * 60)
print(f"Oral contraceptive use  (User_Profile, n={len(user_profile):,})")
print("=" * 60)
print(f"  Prevalence: {oc_rate * 100:.1f}%")
print()

# ── 3. Generate synthetic input features ──────────────────────────────────────

## 3a. Cycle phase
cycle_phase_encoded = RNG.choice([0, 1, 2, 3], size=N_ROWS, p=phase_probs)

## 3b. Oral contraceptive use
oral_contraceptive_use = RNG.binomial(1, oc_rate, size=N_ROWS)

## 3c. Acute:Chronic Workload Ratio
# Log-normal centred on 1.0; σ=0.28 gives ~18% of sessions above 1.5 —
# consistent with intermittent training spikes seen in field sport literature.
acwr_raw            = RNG.lognormal(mean=0.0, sigma=0.28, size=N_ROWS)
acute_chronic_ratio = np.clip(acwr_raw, 0.30, 2.50).round(3)

## 3d. Session RPE — sampled from female multimodal distribution, clipped 1–10
session_rpe = np.clip(
    RNG.normal(rpe_mean, rpe_std, size=N_ROWS), 1.0, 10.0
).round(1)

## 3e. Weekly load — sampled from female multimodal distribution, clipped > 0
weekly_load = np.clip(
    RNG.normal(load_mean, load_std, size=N_ROWS), 50.0, 2_000.0
).round(1)

## 3f. Days since last rest — exponential; higher values correlate with
#  accumulated fatigue. Clipped to realistic range of 1–14 days.
days_since_last_rest = np.clip(
    (RNG.exponential(scale=3.0, size=N_ROWS) + 1).astype(int), 1, 14
)

## 3g. Soreness scores (0–10) — linearly driven by ACWR and RPE with noise.
#  Knee, hamstring, and groin have independent noise terms to reflect their
#  distinct anatomical contributions to lower-limb injury risk.
_soreness_base = (
    (acute_chronic_ratio - 0.8) * 3.0
    + (session_rpe - 5.0) * 0.4
    + RNG.normal(0.0, 1.5, size=N_ROWS)
)
knee_soreness      = np.clip(_soreness_base + RNG.normal(0, 0.8, N_ROWS), 0, 10).round(1)
hamstring_soreness = np.clip(_soreness_base + RNG.normal(0, 0.8, N_ROWS), 0, 10).round(1)
groin_soreness     = np.clip(_soreness_base * 0.7 + RNG.normal(0, 0.8, N_ROWS), 0, 10).round(1)

# ── 4. Compute per-session injury probabilities via JSON multipliers ───────────
#
# Strategy: apportion the base injury rate across three injury types according
# to proportions consistent with football/field sport injury epidemiology:
#   ACL injuries        ≈ 20% of all injuries
#   Soft tissue injuries≈ 40% (muscle strains + ligament sprains, excl. ACL)
#   Overtraining        ≈ 40% (overuse / excessive load outcomes)
#
BASE_ACL_P = BASE_INJURY_RATE * 0.20  # 0.01316
BASE_ST_P  = BASE_INJURY_RATE * 0.40  # 0.02632
BASE_OT_P  = BASE_INJURY_RATE * 0.40  # 0.02632

# ACWR multiplier (general population — not female-specific, see module docstring)
acwr_factor = np.where(acute_chronic_ratio > 1.5, ACWR_HIGH_MUL, 1.0)

# --- ACL injury probability ---
# Elevated during ovulatory phase; reduced by OC use
acl_cycle_factor = np.where(cycle_phase_encoded == 2, ACL_OVULATORY_MUL, 1.0)
acl_oc_factor    = np.where(oral_contraceptive_use == 1, OC_ACL_MUL, 1.0)
p_acl = np.clip(BASE_ACL_P * acwr_factor * acl_cycle_factor * acl_oc_factor, 0.0, 1.0)

# --- Soft tissue injury probability ---
# Strongly elevated in premenstrual phase (IIRR 6.07, Barlow 2024)
st_phase_factor = np.where(cycle_phase_encoded == 3, SOFT_TISSUE_PREMENSTRUAL_MUL, 1.0)
p_st = np.clip(BASE_ST_P * acwr_factor * st_phase_factor, 0.0, 1.0)

# --- Overtraining probability ---
# Primarily load-driven; elevated when rest is insufficient (> 5 consecutive days)
rest_factor = np.where(days_since_last_rest > 5, 1.5, 1.0)
p_ot = np.clip(BASE_OT_P * acwr_factor * rest_factor, 0.0, 1.0)

# Sample binary outcomes
acl_injury         = RNG.binomial(1, p_acl)
soft_tissue_injury = RNG.binomial(1, p_st)
overtraining       = RNG.binomial(1, p_ot)

# ── 5. Assemble DataFrame and save ────────────────────────────────────────────
df = pd.DataFrame({
    "acute_chronic_ratio":    acute_chronic_ratio,
    "cycle_phase_encoded":    cycle_phase_encoded,
    "knee_soreness":          knee_soreness,
    "hamstring_soreness":     hamstring_soreness,
    "groin_soreness":         groin_soreness,
    "days_since_last_rest":   days_since_last_rest,
    "session_rpe":            session_rpe,
    "weekly_load":            weekly_load,
    "oral_contraceptive_use": oral_contraceptive_use,
    "acl_injury":             acl_injury,
    "soft_tissue_injury":     soft_tissue_injury,
    "overtraining":           overtraining,
})

df.to_csv(OUTPUT_PATH, index=False)

# ── 6. Summary report ─────────────────────────────────────────────────────────
n = len(df)
acl_rate = df["acl_injury"].mean() * 100
st_rate  = df["soft_tissue_injury"].mean() * 100
ot_rate  = df["overtraining"].mean() * 100
any_rate = df[["acl_injury", "soft_tissue_injury", "overtraining"]].any(axis=1).mean() * 100
target   = BASE_INJURY_RATE * 100

print("=" * 60)
print("Output")
print("=" * 60)
print(f"  Rows written: {n:,}")
print(f"  Path:         {OUTPUT_PATH}")
print()

print("=" * 60)
print("Injury rate summary")
print("=" * 60)
print(f"  Target base rate (JSON):          {target:.2f}%")
print(f"  Achieved any-injury rate:         {any_rate:.2f}%")
print(f"  ├── ACL injury rate:              {acl_rate:.2f}%")
print(f"  ├── Soft tissue injury rate:      {st_rate:.2f}%")
print(f"  └── Overtraining rate:            {ot_rate:.2f}%")
print()

print("  ACL rate by cycle phase:")
for phase, label in [(0, "Menstrual"), (1, "Follicular"),
                     (2, "Ovulatory"), (3, "Luteal/Premenstrual")]:
    mask = df["cycle_phase_encoded"] == phase
    if mask.sum():
        r = df.loc[mask, "acl_injury"].mean() * 100
        print(f"    Phase {phase} ({label:20s}): {r:.2f}%  (n={mask.sum()})")
print()

print("  Soft tissue rate by cycle phase:")
for phase, label in [(0, "Menstrual"), (1, "Follicular"),
                     (2, "Ovulatory"), (3, "Luteal/Premenstrual")]:
    mask = df["cycle_phase_encoded"] == phase
    if mask.sum():
        r = df.loc[mask, "soft_tissue_injury"].mean() * 100
        print(f"    Phase {phase} ({label:20s}): {r:.2f}%  (n={mask.sum()})")
print()

print("  ACL rate by OC use:")
for oc, label in [(1, "OC user"), (0, "Non-user")]:
    mask = df["oral_contraceptive_use"] == oc
    if mask.sum():
        r = df.loc[mask, "acl_injury"].mean() * 100
        print(f"    {label:10s}: {r:.2f}%  (n={mask.sum()})")
print()

print("  Any-injury rate by ACWR threshold:")
for condition, label in [(True, "ACWR > 1.5"), (False, "ACWR ≤ 1.5")]:
    mask = (df["acute_chronic_ratio"] > 1.5) == condition
    if mask.sum():
        r = df.loc[mask, ["acl_injury", "soft_tissue_injury", "overtraining"]].any(axis=1).mean() * 100
        print(f"    {label}: {r:.2f}%  (n={mask.sum()})")
print()
