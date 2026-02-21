from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd
import os
from datetime import datetime, timedelta

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/wearable_data_cleaned")

@router.get("/exercise")
def get_exercise_data(
    athlete_id: str,
    days: int = Query(7, description="Number of days to retrieve"),
    limit: int = Query(50, description="Max records to return")
):
    """Simulate Samsung Watch exercise session data"""
    df = pd.read_csv(f"{DATA_DIR}/exercise_clean.csv")
    df = df.head(limit)
    
    return {
        "athlete_id": athlete_id,
        "device": "Samsung Galaxy Watch",
        "data_type": "exercise_sessions",
        "records": df.to_dict(orient="records"),
        "count": len(df)
    }

@router.get("/heart-rate")
def get_heart_rate_data(
    athlete_id: str,
    hours: int = Query(24, description="Hours of data to retrieve"),
    limit: int = Query(100, description="Max records to return")
):
    """Simulate Samsung Watch heart rate data"""
    df = pd.read_csv(f"{DATA_DIR}/heart_rate_clean.csv")
    df = df.head(limit)
    
    return {
        "athlete_id": athlete_id,
        "device": "Samsung Galaxy Watch",
        "data_type": "heart_rate",
        "records": df.to_dict(orient="records"),
        "count": len(df)
    }

@router.get("/activity")
def get_activity_data(
    athlete_id: str,
    days: int = Query(7, description="Number of days to retrieve")
):
    """Simulate Samsung Watch daily activity summary"""
    df = pd.read_csv(f"{DATA_DIR}/activity_clean.csv")
    df = df.head(days)
    
    return {
        "athlete_id": athlete_id,
        "device": "Samsung Galaxy Watch",
        "data_type": "daily_activity",
        "records": df.to_dict(orient="records"),
        "count": len(df)
    }

@router.get("/cycle")
def get_cycle_data(athlete_id: str):
    """Simulate menstrual cycle tracking data"""
    cycle_df = pd.read_csv(f"{DATA_DIR}/cycle_clean.csv")
    flow_df = pd.read_csv(f"{DATA_DIR}/cycle_flow_clean.csv")
    mood_df = pd.read_csv(f"{DATA_DIR}/cycle_mood_clean.csv")
    
    return {
        "athlete_id": athlete_id,
        "data_type": "menstrual_cycle",
        "cycle_predictions": cycle_df.to_dict(orient="records"),
        "flow_logs": flow_df.head(30).to_dict(orient="records"),
        "mood_logs": mood_df.head(30).to_dict(orient="records")
    }

@router.get("/latest")
def get_latest_metrics(athlete_id: str):
    """Get latest metrics for quick analysis - simulates real-time watch sync"""
    
    # Latest exercise session
    exercise_df = pd.read_csv(f"{DATA_DIR}/exercise_clean.csv")
    latest_exercise = exercise_df.iloc[0].to_dict() if len(exercise_df) > 0 else None
    
    # Latest activity
    activity_df = pd.read_csv(f"{DATA_DIR}/activity_clean.csv")
    latest_activity = activity_df.iloc[0].to_dict() if len(activity_df) > 0 else None
    
    # Recent heart rate
    hr_df = pd.read_csv(f"{DATA_DIR}/heart_rate_clean.csv")
    recent_hr = hr_df.head(10).to_dict(orient="records")
    
    # Current cycle phase (mock calculation)
    cycle_df = pd.read_csv(f"{DATA_DIR}/cycle_clean.csv")
    current_cycle = cycle_df.iloc[0].to_dict() if len(cycle_df) > 0 else None
    
    return {
        "athlete_id": athlete_id,
        "device": "Samsung Galaxy Watch",
        "sync_time": datetime.now().isoformat(),
        "latest_exercise": latest_exercise,
        "latest_activity": latest_activity,
        "recent_heart_rate": recent_hr,
        "current_cycle": current_cycle
    }
