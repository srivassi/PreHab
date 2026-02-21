# PreHab Backend - Quick Reference Card

## 🚀 Start Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

## 🧪 Test Endpoint
```bash
python test_analyse_endpoint.py
```

## 📍 Endpoint
```
POST http://localhost:8000/analyse/
```

## 📥 Minimal Test Payload
```json
{
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
```

## 📤 Response Fields
- `risk_profile` - ACL, soft tissue, overtraining risks (0-1)
- `trend_analysis` - Load/soreness trajectories, cycle window
- `contributing_factors` - Top 3 risk drivers with weights
- `composite_risk_level` - LOW | MEDIUM | HIGH | CRITICAL
- `recommended_actions` - List of training adjustments
- `injury_window_forecast` - 3/7/14 day risk projection
- `explanation` - Crusoe-generated plain English (when integrated)

## 🎯 Risk Levels
- **CRITICAL** (≥0.75): Immediate intervention needed
- **HIGH** (≥0.55): Reduce training load
- **MEDIUM** (≥0.35): Monitor closely
- **LOW** (<0.35): Safe to continue

## 🔧 Cycle Phases
- 0 = Menstrual
- 1 = Follicular
- 2 = Ovulatory (highest ACL risk)
- 3 = Luteal

## 📊 Models Location
```
backend/ml/models/
├── acl_model.pkl
├── soft_tissue_model.pkl
├── overot_model.pkl
└── rf_importance.pkl
```

## 🔄 Retrain Models
```bash
cd backend
python ml/train.py
```

## 📚 API Docs
```
http://localhost:8000/docs
```

## ✅ Status
- [x] Models trained
- [x] Endpoint working
- [x] JSON contract complete
- [ ] Crusoe integration (needs API key)
- [ ] Paid.ai integration (needs API key)

