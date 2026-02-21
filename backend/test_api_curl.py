"""
API Endpoint Test - Use this to test the live FastAPI server
"""

# HIGH RISK TEST CASE
high_risk_payload = {
    "athlete_id": "athlete_001",
    "cycle_phase": 2,
    "acute_chronic_ratio": 1.67,
    "knee_soreness": 8,
    "hamstring_soreness": 7,
    "groin_soreness": 5,
    "session_rpe": 8.5,
    "weekly_load": 380,
    "days_since_last_rest": 6,
    "last_7_days_soreness": [3, 4, 5, 6, 7, 8, 8],
    "last_7_days_load": [200, 220, 250, 280, 320, 360, 380]
}

# LOW RISK TEST CASE
low_risk_payload = {
    "athlete_id": "athlete_002",
    "cycle_phase": 0,
    "acute_chronic_ratio": 0.95,
    "knee_soreness": 1,
    "hamstring_soreness": 2,
    "groin_soreness": 0,
    "session_rpe": 5.0,
    "weekly_load": 180,
    "days_since_last_rest": 2,
    "last_7_days_soreness": [2, 2, 1, 1, 1, 2, 1],
    "last_7_days_load": [200, 195, 190, 185, 180, 180, 180]
}

print("=" * 70)
print("CURL COMMANDS TO TEST /analyze ENDPOINT")
print("=" * 70)

print("\n1. Start the server:")
print("   cd backend")
print("   uvicorn main:app --reload --port 8000")

print("\n2. Test HIGH RISK case:")
print('   curl -X POST http://localhost:8000/analyze/ \\')
print('     -H "Content-Type: application/json" \\')
print(f'     -d \'{high_risk_payload}\'')

print("\n3. Test LOW RISK case:")
print('   curl -X POST http://localhost:8000/analyze/ \\')
print('     -H "Content-Type: application/json" \\')
print(f'     -d \'{low_risk_payload}\'')

print("\n4. Check health endpoint:")
print("   curl http://localhost:8000/health")

print("\n" + "=" * 70)
print("PYTHON TEST (if you have requests installed)")
print("=" * 70)

print("""
import requests
import json

response = requests.post(
    'http://localhost:8000/analyze/',
    json={
        "athlete_id": "test_001",
        "cycle_phase": 2,
        "acute_chronic_ratio": 1.67,
        "knee_soreness": 8,
        "hamstring_soreness": 7,
        "groin_soreness": 5,
        "session_rpe": 8.5,
        "weekly_load": 380,
        "days_since_last_rest": 6,
        "last_7_days_soreness": [3, 4, 5, 6, 7, 8, 8],
        "last_7_days_load": [200, 220, 250, 280, 320, 360, 380]
    }
)

print(json.dumps(response.json(), indent=2))
""")
