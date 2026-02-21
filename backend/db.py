from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./prehab.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id            = Column(String, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True)
    name          = Column(String)
    sport         = Column(String)
    created_at    = Column(DateTime, default=datetime.datetime.utcnow)


class TrainingLog(Base):
    __tablename__ = "training_logs"
    id            = Column(String, primary_key=True, index=True)
    athlete_id    = Column(String, index=True)
    date          = Column(String)
    sport         = Column(String)
    duration_mins = Column(Integer)
    intensity     = Column(Float)
    rpe           = Column(Float)
    knee_soreness      = Column(Integer, default=0)
    hamstring_soreness = Column(Integer, default=0)
    groin_soreness     = Column(Integer, default=0)
    created_at    = Column(DateTime, default=datetime.datetime.utcnow)


class CycleLog(Base):
    __tablename__ = "cycle_logs"
    id                  = Column(String, primary_key=True, index=True)
    athlete_id          = Column(String, index=True)
    cycle_start_date    = Column(String)
    cycle_length_days   = Column(Integer)
    menstruation_length = Column(Integer)
    on_contraceptive    = Column(Integer, default=0)  # 0=no, 1=yes
    created_at          = Column(DateTime, default=datetime.datetime.utcnow)


class RiskAnalysis(Base):
    __tablename__ = "risk_analyses"
    id            = Column(String, primary_key=True, index=True)
    athlete_id    = Column(String, index=True)
    analysis      = Column(JSON)   # full JSON blob from /analyze
    explanation   = Column(String) # Crusoe-generated text
    created_at    = Column(DateTime, default=datetime.datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
