# PreHab ML Backend - Implementation Complete ✓

## What Was Built

### ✅ Dev 1 Work - ML Models (COMPLETE)
All models trained and saved to `backend/ml/models/`:

1. **acl_model.pkl** - ACL injury risk predictor (Logistic Regression)
2. **soft_tissue_model.pkl** - Soft tissue injury risk predictor (Logistic Regression)
3. **overot_model.pkl** - Overtraining risk predictor (Logistic Regression)
4. **rf_importance.pkl** - Random Forest for feature importance ranking

**Training Results:**
- Dataset: 3,000 synthetic records calibrated to literature
- ACL injury rate: 12.9%
- Soft tissue injury rate: 20.3%
- Overtraining rate: 19.6%

**Feature Importances (from Random Forest):**
1. acute_chronic_ratio: 0.225
2. session_rpe: 0.199
3. weekly_load: 0.197
4. hamstring_soreness: 0.109
5. knee_soreness: 0.105
6. days_since_last_rest: 0.099
7. cycle_phase: 0.066

### ✅ Dev 2 Work - Analysis Layer (COMPLETE)
The `/analyse` endpoint is fully implemented in `backend/routers/analyse.py` and uses:

**Risk Engine** (`services/risk_engine.py`):
- Loads all 4 trained models
- Computes risk scores (ACL, soft tissue, overtraining)
- Detects trends (load trajectory, soreness trajectory)
- Identifies cycle risk windows
- Ranks contributing factors
- Generates recommended actions
- Forecasts injury risk windows (3/7/14 days)

**Integration Points:**
- ✅ Explainer service (Crusoe) - ready for LLM integration
- ✅ Billing service (Paid.ai) - ready for signal tracking
- ✅ Database persistence - saves all analyses

---

## API Contract - POST /analyse

### Input Schema (AthleteInput)
```json
{
  "athlete_id": "string",
  "cycle_phase": 0-3,  // 0=menstrual, 1=follicular, 2=ovulatory, 3=luteal
  "acute_chronic_ratio": 0.4-2.5,
  "knee_soreness": 0-10,
  "hamstring_soreness": 0-10,
  "groin_soreness": 0-10,
  "session_rpe": 1.0-10.0,
  "weekly_load": 50-600,
  "days_since_last_rest": 0-10,
  "last_7_days_soreness": [int, int, ...],  // 7 values
  "last_7_days_load": [float, float, ...]   // 7 values
}
```

### Output Schema (AnalysisResponse)
```json
{
  "risk_profile": {
    "acl_risk": 0.0-1.0,
    "soft_tissue_risk": 0.0-1.0,
    "overtraining_risk": 0.0-1.0,
    "recovery_status": 0.0-1.0,
    "performance_readiness": 0.0-1.0
  },
  "trend_analysis": {
    "load_trajectory": "flat|rising|spiking|falling",
    "soreness_trajectory": "stable|rising_N_days|falling",
    "cycle_risk_window": "safe|approaching|entering_peak|peak",
    "acute_chronic_ratio": float
  },
  "contributing_factors": [
    {
      "factor": "string",
      "contribution": 0.0-1.0,
      "label": "human-readable description"
    }
  ],
  "confidence": 0.0-1.0,
  "composite_risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "recommended_actions": ["action1", "action2", ...],
  "injury_window_forecast": {
    "next_3_days": "low|moderate|high|critical",
    "next_7_days": "low|moderate|high|critical",
    "next_14_days": "low|moderate|high|critical"
  },
  "explanation": "string (Crusoe-generated)"
}
```

---

## How to Run

### 1. Start the Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

Server will be available at: `http://localhost:8000`

### 2. Test the Endpoint

**Option A - Using Python:**
```bash
python test_analyse_endpoint.py
```

**Option B - Using curl:**
```bash
curl -X POST http://localhost:8000/analyse/ \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Option C - Using the API docs:**
Navigate to `http://localhost:8000/docs` for interactive Swagger UI

---

## Handoff to Dev 3 (Crusoe Integration)

### Endpoint URL
```
POST http://localhost:8000/analyse/
```

### Crusoe Prompt Template
The analysis blob is already being passed to `services/explainer.py`. Update that file to call Crusoe:

```python
import openai

client = openai.OpenAI(
    api_key=CRUSOE_API_KEY,
    base_url="https://api.crusoe.ai/v1"
)

def generate(analysis: dict) -> str:
    prompt = f'''
You are PreHab's injury prevention agent. Here is a female athlete's full risk analysis:

{json.dumps(analysis, indent=2)}

Write a clear, empathetic 3-4 sentence explanation for the athlete:
- What her main risks are and why
- What has been changed in her training plan
- What she should watch for this week

Be specific. Use the actual numbers. Sound like a knowledgeable physio.
'''
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

---

## Risk Thresholds & Logic

### Composite Risk Level
```python
max_risk = max(acl_risk, soft_tissue_risk, overtraining_risk)

if max_risk >= 0.75: return "CRITICAL"
if max_risk >= 0.55: return "HIGH"
if max_risk >= 0.35: return "MEDIUM"
return "LOW"
```

### Load Trajectory Detection
```python
delta = last_7_days_load[-1] - last_7_days_load[0]

if delta > 20:  return "spiking"   # dangerous
if delta > 8:   return "rising"    # watch closely
if delta < -8:  return "falling"   # recovering
return "flat"                       # stable
```

### Cycle Risk Windows
```python
if phase == 2 (ovulatory) and ACR > 1.3:  return "peak"          # CRITICAL
if phase == 2:                             return "entering_peak" # HIGH
if phase == 1 (follicular) and ACR > 1.5: return "approaching"   # MEDIUM
return "safe"                                                     # LOW
```

### Recommended Actions
- **reduce_plyometrics** - triggered when risk is HIGH or CRITICAL
- **flag_physio** - triggered when risk is CRITICAL
- **add_stability** - triggered during ovulatory phase (phase 2)
- **reduce_sprint_intensity** - triggered when soreness is rising
- **maintain_plan** - triggered when risk is LOW

---

## File Structure

```
backend/
├── ml/
│   ├── models/
│   │   ├── acl_model.pkl              ✓ Trained
│   │   ├── soft_tissue_model.pkl      ✓ Trained
│   │   ├── overot_model.pkl           ✓ Trained
│   │   └── rf_importance.pkl          ✓ Trained
│   └── train.py                       ✓ Complete
├── routers/
│   └── analyse.py                     ✓ Complete
├── services/
│   ├── risk_engine.py                 ✓ Complete
│   ├── explainer.py                   → Needs Crusoe API key
│   └── billing.py                     → Needs Paid.ai API key
├── schemas.py                         ✓ Complete
├── main.py                            ✓ Complete
├── test_analyse_endpoint.py           ✓ Test script
└── test_api_curl.py                   ✓ API test examples
```

---

## Next Steps

### For Dev 3 (Crusoe Integration):
1. Get Crusoe API key from Intelligence Foundry
2. Update `backend/services/explainer.py` with the prompt template above
3. Test with: `curl http://localhost:8000/analyse/` and verify `explanation` field is populated

### For Frontend (Lovable):
1. Call `POST http://localhost:8000/analyse/` with athlete data
2. Display the returned JSON in the dashboard
3. Show risk levels, trends, and recommended actions
4. Display the Crusoe-generated explanation prominently

### For Paid.ai Integration:
1. Get Paid.ai API key
2. Update `backend/services/billing.py` to record signals
3. Track: risk_assessment_completed, plan_adjusted, escalation_triggered

---

## Testing Checklist

- [x] Models trained successfully
- [x] Models load without errors
- [x] /analyse endpoint returns correct JSON shape
- [x] Risk scores are computed from real models
- [x] Trend detection works (load, soreness, cycle)
- [x] Contributing factors ranked correctly
- [x] Recommended actions generated
- [x] Injury window forecast populated
- [ ] Crusoe explanation generated (needs API key)
- [ ] Paid.ai signals recorded (needs API key)
- [ ] Frontend integration tested

---

## Known Issues & Notes

1. **Model Accuracy**: Current models are trained on synthetic data. Replace with real Kaggle datasets for production.

2. **Risk Scores**: The synthetic data produces conservative risk scores. This is intentional to avoid false positives during demo.

3. **Feature Names Warning**: sklearn warns about feature names vs arrays. This is cosmetic and doesn't affect predictions.

4. **Unicode Encoding**: Some print statements had Unicode characters that don't work on Windows console. Fixed with ASCII equivalents.

---

## Demo Script

**Scenario 1 - High Risk Athlete:**
- Ovulatory phase (cycle_phase=2)
- Load spike (ACR=1.67)
- Rising soreness (8/10 knee)
- Expected: CRITICAL or HIGH risk, multiple action recommendations

**Scenario 2 - Low Risk Athlete:**
- Menstrual phase (cycle_phase=0)
- Safe load (ACR=0.95)
- Low soreness (1-2/10)
- Expected: LOW risk, maintain_plan action

---

## Contact & Support

All models and analysis logic are complete and tested. The endpoint is ready for:
- Frontend integration
- Crusoe LLM explanation generation
- Paid.ai billing signal tracking

**Endpoint is live and ready to demo!** 🚀

