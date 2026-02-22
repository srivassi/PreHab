# PreHab — Backend API

AI-powered injury prevention backend for female athletes. Provides risk scoring, cycle-aware plan adjustment, coach escalation, wearable data integration, and a scientific evidence base.

Built for HackEurope 2026.

---

## Quick start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # add keys (see Environment variables below)
python ml/train.py          # train XGBoost risk model
uvicorn main:app --reload   # start server on :8000
```

Interactive docs: http://localhost:8000/docs

---

## Environment variables

```env
CRUSOE_API_KEY=      # Crusoe/Qwen LLM for plan explanations
PAID_API_KEY=        # Paid.ai usage billing signals
QWEN_MODEL=          # model ID for explainer
```

---

## Endpoints

### Core

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyse/` | Main agent — risk score, plan adjustment, escalation trigger, Paid.ai signal |
| GET | `/health` | Health check |
| GET | `/evidence` | Peer-reviewed citations backing the risk model |

### Training

| Method | Path | Description |
|--------|------|-------------|
| POST | `/training/log` | Log a training session (RPE, duration, soreness) |
| GET | `/training/{athlete_id}` | Get last 30 sessions |

### Cycle

| Method | Path | Description |
|--------|------|-------------|
| POST | `/cycle/log` | Log cycle details |
| GET | `/cycle/{athlete_id}/phase` | Get current phase |

### Wearable (Samsung Health)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/wearable/cycle?athlete_id=` | Cycle history + computed current phase from Samsung Health data |
| GET | `/wearable/latest?athlete_id=` | Latest cycle phase summary |

> Note: only cycle data is valid from the Samsung Health export. Exercise, heart rate, and activity CSVs contain corrupt timestamps and are not served.

### Users & Escalation

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/register` | Register athlete |
| POST | `/escalation/trigger` | Trigger coach/physio alert |

---

## Agent loop (`POST /analyse/`)

```
OBSERVE  — fetch training sessions, soreness, cycle phase, wearable data
THINK    — score injury risk (XGBoost), compute acute:chronic workload ratio
ACT      — adjust weekly plan if risk elevated (phase multipliers applied)
LOG      — persist risk analysis + explanation to DB; emit Paid.ai billing signal
REFLECT  — evaluate coach feedback history, update autonomy policy
```

**Autonomy modes** (based on coach acceptance rate):
- `Full Autonomy` — applies plan changes automatically
- `Dampened` — applies changes but flags for review
- `Suggest-Only` — recommends changes, waits for coach approval

**Risk bands:**

| Band | Score |
|------|-------|
| CRITICAL | ≥ 75% |
| HIGH | ≥ 55% |
| MEDIUM | ≥ 35% |
| LOW | < 35% |

**Cycle phase multipliers applied to training load:**

| Phase | Multiplier |
|-------|-----------|
| Menstruation | 0.72× |
| Follicular | 1.00× |
| Ovulatory | 1.12× |
| Luteal | 0.88× |

---

## Evidence base (`GET /evidence`)

Returns all risk factors with peer-reviewed citations, statistical multipliers (RR/IIRR), and self-report methods. Sources include:

- Wojtys et al. (1998) — ACL injury frequency during ovulatory phase (RR ≈ 1.61)
- Barlow et al., *Med Sci Sports Exerc* (2024) — muscle injury rate 6.07× higher in late luteal phase
- Herzberg et al., *Orthop J Sports Med* (2017) — OC use reduces ACL risk (RR 0.82)
- Kim et al. (2021) — ACWR > 1.5 as injury danger zone

---

## File structure

```
backend/
├── main.py                      # FastAPI app + /health + /evidence
├── db.py                        # SQLAlchemy models (SQLite)
├── schemas.py                   # Pydantic request/response schemas
├── requirements.txt
├── .env.example
├── routers/
│   ├── analyse.py               # POST /analyse — core agent endpoint
│   ├── training.py              # Training log endpoints
│   ├── cycle.py                 # Cycle phase endpoints
│   ├── wearable.py              # Samsung Health wearable endpoints
│   ├── users.py                 # User management
│   └── escalation.py           # Coach/physio alerts
├── services/
│   ├── risk_engine.py           # Risk scoring, ACWR, trend detection
│   ├── explainer.py             # LLM explanation generation (Crusoe/Qwen)
│   ├── planner.py               # Training plan adjustment logic
│   ├── billing.py               # Paid.ai usage signal emission
│   └── cycle_utils.py          # Phase inference from cycle dates
├── ml/
│   ├── train.py                 # Train XGBoost risk model
│   ├── generate_synthetic_data.py
│   ├── clean_raw_data.py
│   └── models/                  # .pkl model files
├── data/
│   └── wearable_data_cleaned/   # Samsung Health export (cycle data only is valid)
├── training_data/
│   └── thresholds_data.json     # Evidence base + citations
└── tests/
    └── test_analyze.py
```

---

## Tests

```bash
python -m pytest tests/ -v
```
