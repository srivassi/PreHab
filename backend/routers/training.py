from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import TrainingLogCreate
from db import get_db, TrainingLog
import uuid

router = APIRouter()

@router.post("/log")
def log_training(data: TrainingLogCreate, db: Session = Depends(get_db)):
    """Log a training session for an athlete."""
    record = TrainingLog(id=str(uuid.uuid4()), **data.dict())
    db.add(record)
    db.commit()
    return {"id": record.id, "status": "logged"}

@router.get("/{athlete_id}")
def get_training_logs(athlete_id: str, db: Session = Depends(get_db)):
    """Get last 30 training logs for an athlete."""
    logs = (
        db.query(TrainingLog)
        .filter(TrainingLog.athlete_id == athlete_id)
        .order_by(TrainingLog.date.desc())
        .limit(30)
        .all()
    )
    return logs
