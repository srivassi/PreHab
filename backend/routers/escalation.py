from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import EscalationCreate
from db import get_db
from services import billing

router = APIRouter()

@router.post("/trigger")
def trigger_escalation(data: EscalationCreate, db: Session = Depends(get_db)):
    """
    Trigger an escalation alert to coach/physio.
    In MVP this is mocked — replace with real email/notification service.
    """

    # TODO: replace with real email service (SendGrid, Resend, etc.)
    mock_notification = {
        "status": "sent",
        "to": data.coach_email or data.physio_email or "coach@prehab.app",
        "subject": f"⚠️ PreHab Alert — {data.risk_level} risk for athlete {data.athlete_id}",
        "body": f"Athlete {data.athlete_id} has been flagged at {data.risk_level} risk. "
                f"Please review analysis ID: {data.analysis_id}"
    }

    # Log escalation signal to Paid.ai
    billing.record_signal(
        event_name="escalation_triggered",
        athlete_id=data.athlete_id,
        risk_level=data.risk_level,
        plan_adjusted=False
    )

    return mock_notification

