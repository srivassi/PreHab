# PreHab — Backend

## Quick start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # add CRUSOE_API_KEY
python ml/train.py          # Dev 1: train models
uvicorn main:app --reload   # Dev 2: run server
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /analyze/ | Core agent — returns full risk analysis |
| POST | /training/log | Log a training session |
| GET  | /training/{athlete_id} | Get last 30 sessions |
| POST | /cycle/log | Log cycle details |
| GET  | /cycle/{athlete_id}/phase | Get current phase |
| POST | /users/register | Register athlete |
| POST | /escalation/trigger | Trigger coach/physio alert |
| GET  | /health | Health check |

## Docs

Interactive docs at http://localhost:8000/docs once server is running.

## Tests

```bash
python -m pytest tests/ -v
```

## File structure

```
backend/
├── main.py              # FastAPI app
├── db.py                # SQLite models
├── schemas.py           # Pydantic schemas
├── requirements.txt
├── .env.example
├── routers/
│   ├── analyze.py       # POST /analyze — core agent endpoint
│   ├── training.py      # Training log endpoints
│   ├── cycle.py         # Cycle phase endpoints
│   ├── users.py         # User management
│   └── escalation.py    # Coach/physio alerts
├── services/
│   ├── risk_engine.py   # Risk scoring + trend detection
│   ├── explainer.py     # Crusoe/Qwen explanation generation
│   ├── planner.py       # Training plan adjustment
│   ├── billing.py       # Paid.ai signal tracking
│   └── cycle_utils.py   # Phase inference from cycle dates
├── ml/
│   ├── train.py         # Dev 1: run this to train models
│   └── models/          # .pkl files go here
└── tests/
    └── test_analyze.py
```
