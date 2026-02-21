from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import CycleLogCreate
from db import get_db, CycleLog
from services.cycle_utils import infer_current_phase
import uuid

router = APIRouter()

@router.post("/log")
def log_cycle(data: CycleLogCreate, db: Session = Depends(get_db)):
    """Log or update menstrual cycle details for an athlete."""
    record = CycleLog(id=str(uuid.uuid4()), **data.dict())
    db.add(record)
    db.commit()
    return {"id": record.id, "status": "logged"}

@router.get("/{athlete_id}/phase")
def get_current_phase(athlete_id: str, db: Session = Depends(get_db)):
    """
    Infer current cycle phase from most recent cycle log.
    Returns: { phase_int: 0-3, phase_name: str, day_of_cycle: int }
    """
    cycle = (
        db.query(CycleLog)
        .filter(CycleLog.athlete_id == athlete_id)
        .order_by(CycleLog.created_at.desc())
        .first()
    )
    if not cycle:
        return {"phase_int": 1, "phase_name": "follicular", "day_of_cycle": None}

    return infer_current_phase(
        cycle.cycle_start_date,
        cycle.cycle_length_days,
        cycle.menstruation_length
    )
