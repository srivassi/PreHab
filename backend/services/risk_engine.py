import joblib
import os
from schemas import AthleteInput

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../ml/models")

FACTOR_LABELS = {
    "acute_chronic_ratio":   "Training load spike detected",
    "cycle_phase":           "Hormonal risk window active",
    "knee_soreness":         "Elevated knee soreness",
    "hamstring_soreness":    "Elevated hamstring soreness",
    "groin_soreness":        "Elevated groin soreness",
    "session_rpe":           "High perceived exertion",
    "weekly_load":           "High weekly training volume",
    "days_since_last_rest":  "Insufficient rest days",
}

FORECAST_TABLE = {
    ("CRITICAL", "spiking",  2): ("critical", "high",     "moderate"),
    ("CRITICAL", "rising",   2): ("critical", "high",     "moderate"),
    ("CRITICAL", "spiking",  1): ("high",     "high",     "moderate"),
    ("HIGH",     "spiking",  2): ("high",     "high",     "moderate"),
    ("HIGH",     "rising",   2): ("high",     "moderate", "low"),
    ("HIGH",     "rising",   1): ("moderate", "moderate", "low"),
    ("MEDIUM",   "flat",     1): ("moderate", "low",      "low"),
    ("MEDIUM",   "flat",     0): ("low",      "low",      "low"),
    ("LOW",      "falling",  0): ("low",      "low",      "low"),
}


def _load_models():
    """Load .pkl models. Falls back to dummy if not yet trained."""
    try:
        return {
            "acl":  joblib.load(f"{MODELS_DIR}/acl_model.pkl"),
            "soft": joblib.load(f"{MODELS_DIR}/soft_model.pkl"),
            "ot":   joblib.load(f"{MODELS_DIR}/ot_model.pkl"),
            "rf":   joblib.load(f"{MODELS_DIR}/rf_importance.pkl"),
        }
    except FileNotFoundError:
        # ── DUMMY fallback until Dev 1 trains the models ──────────
        return None


def _dummy_scores(data: AthleteInput):
    """Rule-based fallback if .pkl files don't exist yet."""
    acl = min(0.9, 0.1
        + 0.35 * (data.cycle_phase == 2)
        + 0.30 * max(0, data.acute_chronic_ratio - 1.3)
        + 0.05 * (data.knee_soreness / 10))
    soft = min(0.9, 0.1
        + 0.25 * (data.acute_chronic_ratio > 1.5)
        + 0.05 * (data.hamstring_soreness / 10)
        + 0.05 * (data.groin_soreness / 10))
    ot = min(0.9, 0.1
        + 0.20 * (data.days_since_last_rest > 5)
        + 0.20 * (data.session_rpe > 8)
        + 0.10 * (data.weekly_load > 300))
    return acl, soft, ot, None


def _feature_vector(data: AthleteInput):
    return [[
        data.acute_chronic_ratio,
        data.cycle_phase,
        data.knee_soreness,
        data.hamstring_soreness,
        data.session_rpe,
        data.days_since_last_rest,
        data.weekly_load,
    ]]


def _composite_risk(acl, soft, ot) -> str:
    score = max(acl, soft, ot)
    if score >= 0.75: return "CRITICAL"
    if score >= 0.55: return "HIGH"
    if score >= 0.35: return "MEDIUM"
    return "LOW"


def _detect_load_trajectory(history) -> str:
    if len(history) < 3: return "insufficient_data"
    delta = history[-1] - history[0]
    if delta > 20:  return "spiking"
    if delta > 8:   return "rising"
    if delta < -8:  return "falling"
    return "flat"


def _detect_soreness_trajectory(history) -> str:
    if len(history) < 3: return "stable"
    rising = sum(1 for i in range(1, len(history)) if history[i] > history[i - 1])
    if rising >= 3: return f"rising_{rising}_days"
    if rising == 0: return "falling"
    return "stable"


def _detect_cycle_risk_window(phase, acr) -> str:
    if phase == 2 and acr > 1.3:  return "peak"
    if phase == 2:                 return "entering_peak"
    if phase == 1 and acr > 1.5:  return "approaching"
    return "safe"


def _get_contributing_factors(rf_model, X, features):
    feature_names = [
        "acute_chronic_ratio", "cycle_phase", "knee_soreness",
        "hamstring_soreness", "session_rpe", "days_since_last_rest", "weekly_load"
    ]
    if rf_model:
        importances = rf_model.feature_importances_
    else:
        # Dummy importances if no model yet
        importances = [0.30, 0.25, 0.15, 0.12, 0.08, 0.06, 0.04]

    ranked = sorted(zip(feature_names, importances), key=lambda x: -x[1])
    return [
        {"factor": f, "contribution": round(float(i), 2), "label": FACTOR_LABELS.get(f, f)}
        for f, i in ranked[:3]
    ]


def _recommended_actions(risk, soreness_traj, phase) -> list:
    actions = []
    if risk in ("HIGH", "CRITICAL"): actions.append("reduce_plyometrics")
    if risk == "CRITICAL":           actions.append("flag_physio")
    if phase == 2:                   actions.append("add_stability")
    if "rising" in soreness_traj:    actions.append("reduce_sprint_intensity")
    if risk == "LOW":                actions.append("maintain_plan")
    return actions


def _forecast(risk, load_traj, phase):
    key = (risk, load_traj, phase)
    result = FORECAST_TABLE.get(key, ("moderate", "moderate", "low"))
    return {"next_3_days": result[0], "next_7_days": result[1], "next_14_days": result[2]}


def run(data: AthleteInput) -> dict:
    """Main entry point. Returns the full analysis dict."""
    models = _load_models()
    features = _feature_vector(data)

    if models:
        acl  = float(models["acl"].predict_proba(features)[0][1])
        soft = float(models["soft"].predict_proba(features)[0][1])
        ot   = float(models["ot"].predict_proba(features)[0][1])
        rf   = models["rf"]
    else:
        acl, soft, ot, rf = _dummy_scores(data)

    risk          = _composite_risk(acl, soft, ot)
    load_traj     = _detect_load_trajectory(data.last_7_days_load)
    soreness_traj = _detect_soreness_trajectory(data.last_7_days_soreness)
    cycle_window  = _detect_cycle_risk_window(data.cycle_phase, data.acute_chronic_ratio)
    factors       = _get_contributing_factors(rf, features[0], None)
    forecast      = _forecast(risk, load_traj, data.cycle_phase)

    return {
        "risk_profile": {
            "acl_risk":              round(acl, 2),
            "soft_tissue_risk":      round(soft, 2),
            "overtraining_risk":     round(ot, 2),
            "recovery_status":       round(1 - ot, 2),
            "performance_readiness": round(1 - max(acl, soft), 2),
        },
        "trend_analysis": {
            "load_trajectory":     load_traj,
            "soreness_trajectory": soreness_traj,
            "cycle_risk_window":   cycle_window,
            "acute_chronic_ratio": round(data.acute_chronic_ratio, 2),
        },
        "contributing_factors":   factors,
        "confidence":             round((acl + soft + ot) / 3, 2),
        "composite_risk_level":   risk,
        "recommended_actions":    _recommended_actions(risk, soreness_traj, data.cycle_phase),
        "injury_window_forecast": forecast,
    }
