from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import AthleteInput, AnalysisResponse
from services import risk_engine, planner, explainer, billing
from db import get_db, RiskAnalysis
import uuid, json

router = APIRouter()

@router.post("/", response_model=AnalysisResponse)
def analyse(data: AthleteInput, db: Session = Depends(get_db)):
    """
    Core agent endpoint.
    1. Score risk (risk_engine)
    2. Detect trends (risk_engine)
    3. Generate explanation (explainer -> Crusoe)
    4. Log to Paid.ai (billing)
    5. Return full analysis blob
    """

    # ── Step 1+2: Run the full risk analysis ──────────────────
    analysis = risk_engine.run(data)

    # ── Step 3: Generate plain-English explanation via Crusoe ─
    explanation = explainer.generate(analysis)
    analysis["explanation"] = explanation

    # ── Step 4: Persist to DB ─────────────────────────────────
    record = RiskAnalysis(
        id=str(uuid.uuid4()),
        athlete_id=data.athlete_id,
        analysis=analysis,
        explanation=explanation
    )
    db.add(record)
    db.commit()

    # ── Step 5: Log signal to Paid.ai ─────────────────────────
    billing.record_signal(
        event_name="risk_assessment_completed",
        athlete_id=data.athlete_id,
        risk_level=analysis["composite_risk_level"],
        plan_adjusted=len(analysis["recommended_actions"]) > 0
    )

    return analysis

