"""
Quick smoke tests — run before handing endpoint to Dev 3.
    python -m pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app
from db import init_db

client = TestClient(app)

SAMPLE_INPUT = {
    "athlete_id":            "test_athlete_001",
    "cycle_phase":           2,
    "acute_chronic_ratio":   1.67,
    "knee_soreness":         7,
    "hamstring_soreness":    4,
    "groin_soreness":        2,
    "session_rpe":           8.5,
    "weekly_load":           320.0,
    "days_since_last_rest":  4,
    "last_7_days_soreness":  [3, 4, 4, 5, 6, 7, 7],
    "last_7_days_load":      [200, 210, 230, 260, 290, 310, 320],
}


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_returns_200():
    r = client.post("/analyze/", json=SAMPLE_INPUT)
    assert r.status_code == 200


def test_analyze_has_required_fields():
    r = client.post("/analyze/", json=SAMPLE_INPUT)
    data = r.json()
    assert "risk_profile"           in data
    assert "trend_analysis"         in data
    assert "contributing_factors"   in data
    assert "composite_risk_level"   in data
    assert "recommended_actions"    in data
    assert "injury_window_forecast" in data
    assert "confidence"             in data


def test_analyze_risk_profile_values_in_range():
    r = client.post("/analyze/", json=SAMPLE_INPUT)
    rp = r.json()["risk_profile"]
    for key, val in rp.items():
        assert 0.0 <= val <= 1.0, f"{key} out of range: {val}"


def test_analyze_composite_risk_valid():
    r = client.post("/analyze/", json=SAMPLE_INPUT)
    assert r.json()["composite_risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def test_high_risk_scenario_triggers_actions():
    r = client.post("/analyze/", json=SAMPLE_INPUT)  # ovulatory + ACR 1.67 = should be high/critical
    actions = r.json()["recommended_actions"]
    assert len(actions) > 0


def test_low_risk_scenario():
    low_risk = {**SAMPLE_INPUT,
        "cycle_phase": 0, "acute_chronic_ratio": 0.9,
        "knee_soreness": 1, "session_rpe": 5.0,
        "last_7_days_load": [200, 195, 190, 185, 182, 180, 178],
        "last_7_days_soreness": [2, 2, 1, 2, 1, 1, 1],
    }
    r = client.post("/analyze/", json=low_risk)
    assert r.json()["composite_risk_level"] in ("LOW", "MEDIUM")
