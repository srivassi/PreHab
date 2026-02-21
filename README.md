# 🛡️ PreHab — Prevent the Injury Before It Happens

> An autonomous AI agent that dynamically adjusts female athletes' training plans by integrating menstrual cycle phase, training load, and pain/soreness signals — stopping injuries before they occur.

---

## 🧠 The Problem

Women are **2–8× more likely** than men to sustain ACL injuries, with risk peaking during pre-ovulatory and ovulatory phases. Training-load spikes (acute:chronic ratio) are independently associated with soft-tissue injury. Yet almost no training systems account for hormonal fluctuations.

PreHab bridges that gap with a closed-loop AI agent that acts *before* the injury happens.

---

## ✨ Core Features

### 🔴 Menstrual-Cycle-Aware Risk Scoring
Maps each training day to a cycle phase (menstruation, follicular, ovulatory, luteal) and applies a literature-calibrated injury-risk multiplier.

### 📈 Acute:Chronic Load Monitoring
Computes the 7-day vs 28-day load ratio and flags dangerous spikes (> 1.5 threshold) before they cause injury.

### 🤕 Soreness / Pain Signal Integration
Athletes log daily soreness (0–10) per body area (knee, hamstring, groin). High or rising scores increase the composite risk score.

### 🔄 Autonomous Re-Planning
When risk exceeds a threshold, the agent automatically:
- Reduces plyometric volume
- Lowers or replaces sprint / max-velocity work
- Adds stability-focused strength sessions
- Generates an updated weekly plan + risk justification report

### 🚨 Escalation to Coach / Physio
When risk is critical or soreness is severe, the agent triggers an alert to the athlete's coach or physiotherapist (mocked in MVP).

---

## 🤖 The Agentic Loop

```
Observe → Predict → Re-Plan → Justify → Escalate
```

1. **Observe** — Read training logs, menstrual phase, soreness scores
2. **Predict** — Compute injury-risk probability via ML model + rule engine
3. **Re-Plan** — Simulate and apply safer alternative sessions
4. **Justify** — Generate plain-language explanation of every change (powered by Crusoe)
5. **Escalate** — Notify coach/physio if risk remains critical

---

## ⚡ Powered By

### Crusoe — AI Inference
PreHab uses **Crusoe Managed Inference** to power the agent's natural language justification and re-planning modules. When the agent adjusts a training session, Crusoe serves the LLM that generates the plain-English explanation for the athlete and coach — delivering fast, personalised reasoning rather than rigid template strings.

Why Crusoe for PreHab:
- **Speed** — Up to 9.9× faster time-to-first-token means no awkward pauses in the live demo or production app
- **Open-source models** — Access to Llama 3.3 70B, DeepSeek, and more via the Intelligence Foundry; generate API keys in minutes
- **Built for agents** — Crusoe Managed Inference is purpose-built for agentic workloads and complex task automation, which maps directly to PreHab's observe → re-plan → justify loop
- **Cost** — Up to 81% cheaper than hyperscalers, keeping PreHab viable post-hackathon

```python
# Example: Crusoe-powered justification call
import openai  # Crusoe is OpenAI-compatible

client = openai.OpenAI(
    api_key=CRUSOE_API_KEY,
    base_url="https://api.crusoe.ai/v1"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-instruct",
    messages=[{
        "role": "user",
        "content": f"Explain why this athlete's training was adjusted: {risk_context}"
    }]
)
```

---

### Paid.ai — Agent Billing & Monetization
PreHab uses **Paid.ai** to track agent costs, measure value delivered, and monetize the product post-hackathon. Every meaningful action the PreHab agent takes — a risk assessment, a plan adjustment, an escalation — is a billable signal.

Why Paid.ai for PreHab:
- **Agent-native billing** — Paid is built specifically for AI agents that perform work, not SaaS seat licensing; perfect for PreHab's outcome-driven model
- **Cost tracking across providers** — Automatically monitors spending across Crusoe, OpenAI, Anthropic and 50+ providers in one view, so we always know our margin per athlete
- **Flexible pricing models** — Supports activity-based (per risk assessment), outcome-based (per injury prevented / training week completed), and hybrid models
- **Value dashboards** — Embeddable Blocks dashboards show coaches and sports orgs exactly what PreHab's agent accomplished and the ROI it delivered
- **Free to start** — Cost tracking is free; billing features kick in when PreHab goes commercial

```python
# Example: Recording a PreHab agent signal in Paid.ai
from paid import Paid, Signal

client = Paid(token=PAID_API_KEY)

signal = Signal(
    event_name="risk_assessment_completed",
    agent_id="prehab-agent",
    customer_id=athlete_id,
    data={
        "risk_level": "high",
        "plan_adjusted": True,
        "costData": {
            "vendor": "crusoe",
            "cost": {"amount": 0.002, "currency": "USD"}
        }
    }
)
client.usage.record_bulk(signals=[signal])
```

**PreHab's billing model (post-MVP):**

| Signal | Billing Approach |
|---|---|
| Daily risk assessment | Activity-based (per athlete/day) |
| Training plan adjustment | Outcome-based (per adjustment made) |
| Coach escalation triggered | Outcome-based (per alert sent) |
| Injury-free training week | Outcome-based (premium tier) |

---

## 🗂️ Project Structure

```
prehab/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── routers/
│   │   ├── users.py         # Auth & account management
│   │   ├── training.py      # Training log endpoints
│   │   ├── cycle.py         # Menstrual cycle endpoints
│   │   └── risk.py          # Risk computation & plan adjustment
│   ├── services/
│   │   ├── risk_engine.py   # Acute:chronic + phase + soreness scoring
│   │   ├── planner.py       # Agent re-planning logic
│   │   ├── explainer.py     # Crusoe-powered justification generation
│   │   └── billing.py       # Paid.ai signal tracking
│   ├── ml/
│   │   ├── model.py         # Logistic regression / tiny neural net
│   │   ├── train.py         # Training script
│   │   └── synthetic_data.py# Synthetic dataset generator
│   └── db.py                # SQLite setup
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TrainingLog.jsx
│   │   │   ├── CycleSetup.jsx
│   │   │   ├── PlanView.jsx
│   │   │   └── RiskReport.jsx
│   │   └── components/
│   └── index.html
├── data/
│   └── synthetic/           # Generated training + cycle datasets
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · FastAPI |
| Database | SQLite (MVP) |
| ML Model | Scikit-learn (logistic regression) |
| Agent Logic | Python rule engine |
| LLM Inference | Crusoe Managed Inference (Llama 3.3 70B) |
| Agent Billing | Paid.ai |
| Frontend | React · TailwindCSS · React Router |
| API | REST (Fetch API) |
| Deployment | Vercel (frontend) · Render (backend) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Crusoe API key (from [Intelligence Foundry](https://crusoe.ai))
- Paid.ai API key (from [paid.ai](https://paid.ai))

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # add your CRUSOE_API_KEY and PAID_API_KEY
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 📊 ML Model

The injury-risk model is a logistic regression trained on **synthetic data** calibrated to literature-reported injury-incidence rates. Input features:

- **Acute:chronic load ratio** (last 7 days / last 28 days)
- **Menstrual phase** (follicular / ovulatory / luteal / menstruation)
- **Soreness score** (0–10, per body area)

Risk output is a probability score bucketed into **Low / Medium / High / Critical** thresholds, which drive the agent's re-planning decisions.

To retrain the model:

```bash
cd backend/ml
python synthetic_data.py   # generate dataset
python train.py            # train and save model
```

---

## 🔁 User Flow

1. **Onboarding** — Sign up, enter cycle details, select sport
2. **Daily Logging** — Log training session (RPE, duration, intensity) + soreness scores
3. **Risk Assessment** — Agent computes composite risk score in real time
4. **Plan Update** — Adjusted weekly plan appears automatically with Crusoe-generated explanation
5. **Escalation** — One-click alert to coach/physio if risk is critical
6. **Billing** — Paid.ai tracks each agent action as a signal for transparent cost and revenue reporting

---

## 📋 Risk Score Logic

```
Risk Score = (Acute:Chronic Weight × Load Risk)
           + (Phase Multiplier × Phase Risk)
           + (Soreness Weight × Soreness Risk)
```

| Acute:Chronic Ratio | Load Risk Level |
|---|---|
| < 1.0 | Low |
| 1.0 – 1.3 | Moderate |
| 1.3 – 1.5 | High |
| > 1.5 | Critical |

Phase multipliers are calibrated to meta-analyses on ACL injury risk across the menstrual cycle.

---

## 📁 Data Sources

- [Athlete Injury and Performance Dataset — Kaggle](https://kaggle.com)
- [Menstrual Cycle Data — Kaggle](https://kaggle.com)
- [Injury Profile in Youth Female Athletes — PubMed](https://pmc.ncbi.nlm.nih.gov)
- [Sex Differences in Injury Rates in Team-Sport Athletes — PubMed](https://pmc.ncbi.nlm.nih.gov)

---

## ⚠️ Disclaimer

PreHab is a research/hackathon prototype. It is **not a medical device** and should not replace professional medical or physiotherapy advice. Always consult qualified practitioners for injury assessment and treatment.

---

## 👥 Team

Built at **HackEurope** — Agentic AI × AI in Healthcare track.

---

## 📄 License

MIT
