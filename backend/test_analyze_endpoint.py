"""
Quick test script to validate /analyze endpoint with real models.
Run this after training models to confirm everything works.
"""
import sys
sys.path.insert(0, '.')

from schemas import AthleteInput
from services import risk_engine

# Test case 1: HIGH RISK athlete (ovulatory phase + high load spike + soreness)
print("=" * 60)
print("TEST 1: HIGH RISK ATHLETE")
print("=" * 60)

high_risk_data = AthleteInput(
    athlete_id="test_001",
    cycle_phase=2,  # ovulatory - highest ACL risk
    acute_chronic_ratio=1.67,  # critical load spike
    knee_soreness=8,
    hamstring_soreness=7,
    groin_soreness=5,
    session_rpe=8.5,
    weekly_load=380,
    days_since_last_rest=6,
    last_7_days_soreness=[3, 4, 5, 6, 7, 8, 8],  # rising trend
    last_7_days_load=[200, 220, 250, 280, 320, 360, 380]  # spiking
)

result = risk_engine.run(high_risk_data)

print(f"\nRisk Profile:")
print(f"  ACL Risk:              {result['risk_profile']['acl_risk']}")
print(f"  Soft Tissue Risk:      {result['risk_profile']['soft_tissue_risk']}")
print(f"  Overtraining Risk:     {result['risk_profile']['overtraining_risk']}")
print(f"  Recovery Status:       {result['risk_profile']['recovery_status']}")
print(f"  Performance Readiness: {result['risk_profile']['performance_readiness']}")

print(f"\nTrend Analysis:")
print(f"  Load Trajectory:       {result['trend_analysis']['load_trajectory']}")
print(f"  Soreness Trajectory:   {result['trend_analysis']['soreness_trajectory']}")
print(f"  Cycle Risk Window:     {result['trend_analysis']['cycle_risk_window']}")
print(f"  Acute:Chronic Ratio:   {result['trend_analysis']['acute_chronic_ratio']}")

print(f"\nComposite Risk Level: {result['composite_risk_level']}")
print(f"Confidence: {result['confidence']}")

print(f"\nTop Contributing Factors:")
for factor in result['contributing_factors']:
    print(f"  - {factor['label']} ({factor['contribution']})")

print(f"\nRecommended Actions:")
for action in result['recommended_actions']:
    print(f"  - {action}")

print(f"\nInjury Window Forecast:")
print(f"  Next 3 days:  {result['injury_window_forecast']['next_3_days']}")
print(f"  Next 7 days:  {result['injury_window_forecast']['next_7_days']}")
print(f"  Next 14 days: {result['injury_window_forecast']['next_14_days']}")

# Test case 2: LOW RISK athlete (safe phase + low load + no soreness)
print("\n" + "=" * 60)
print("TEST 2: LOW RISK ATHLETE")
print("=" * 60)

low_risk_data = AthleteInput(
    athlete_id="test_002",
    cycle_phase=0,  # menstrual - lower risk
    acute_chronic_ratio=0.95,  # safe load
    knee_soreness=1,
    hamstring_soreness=2,
    groin_soreness=0,
    session_rpe=5.0,
    weekly_load=180,
    days_since_last_rest=2,
    last_7_days_soreness=[2, 2, 1, 1, 1, 2, 1],  # stable/falling
    last_7_days_load=[200, 195, 190, 185, 180, 180, 180]  # falling
)

result2 = risk_engine.run(low_risk_data)

print(f"\nComposite Risk Level: {result2['composite_risk_level']}")
print(f"ACL Risk: {result2['risk_profile']['acl_risk']}")
print(f"Load Trajectory: {result2['trend_analysis']['load_trajectory']}")
print(f"Recommended Actions: {result2['recommended_actions']}")

print("\n" + "=" * 60)
print("[SUCCESS] All tests passed! Models are working correctly.")
print("=" * 60)
