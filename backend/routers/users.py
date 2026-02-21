from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import UserCreate
from db import get_db, User
import uuid

router = APIRouter()

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = User(id=str(uuid.uuid4()), **data.dict())
    db.add(user)
    db.commit()
    return {"id": user.id, "status": "created"}

@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
