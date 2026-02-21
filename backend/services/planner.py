"""
Planner service.
Takes the analysis output and returns a modified weekly training plan.
"""

BASE_WEEK = {
    "monday":    {"type": "sprint",    "volume": 100, "intensity": 0.85},
    "tuesday":   {"type": "strength",  "volume": 80,  "intensity": 0.75},
    "wednesday": {"type": "plyometric","volume": 90,  "intensity": 0.80},
    "thursday":  {"type": "rest",      "volume": 0,   "intensity": 0.00},
    "friday":    {"type": "sprint",    "volume": 90,  "intensity": 0.80},
    "saturday":  {"type": "match",     "volume": 100, "intensity": 0.90},
    "sunday":    {"type": "rest",      "volume": 0,   "intensity": 0.00},
}


def adjust_plan(analysis: dict) -> dict:
    """
    Returns original + adjusted weekly plan based on risk analysis.
    """
    risk    = analysis.get("composite_risk_level", "LOW")
    actions = analysis.get("recommended_actions", [])
    plan    = {day: dict(session) for day, session in BASE_WEEK.items()}
    changes = []

    for day, session in plan.items():

        if "reduce_plyometrics" in actions and session["type"] == "plyometric":
            session["volume"]    = round(session["volume"] * 0.5)
            session["intensity"] = round(session["intensity"] * 0.7, 2)
            changes.append(f"{day.capitalize()}: plyometrics reduced by 50%")

        if "reduce_sprint_intensity" in actions and session["type"] == "sprint":
            session["intensity"] = round(session["intensity"] * 0.75, 2)
            changes.append(f"{day.capitalize()}: sprint intensity reduced")

        if "add_stability" in actions and session["type"] == "rest" and day == "thursday":
            session["type"]      = "stability"
            session["volume"]    = 60
            session["intensity"] = 0.50
            changes.append("Thursday: stability session added")

        if risk == "CRITICAL" and session["type"] == "match":
            session["intensity"] = round(session["intensity"] * 0.80, 2)
            changes.append(f"{day.capitalize()}: match intensity reduced (critical risk)")

    return {
        "original_plan": BASE_WEEK,
        "adjusted_plan": plan,
        "changes_made":  changes,
        "risk_level":    risk,
    }
