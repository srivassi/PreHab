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
    """Menstrual cycle tracking data with current phase calculation"""
    df = pd.read_csv(f"{DATA_DIR}/cycle_clean.csv")
    df["period_start"] = pd.to_datetime(df["period_start"])
    df["period_end"] = pd.to_datetime(df["period_end"])
    df["ovulation_date"] = pd.to_datetime(df["ovulation_date"])
    df["fertile_start"] = pd.to_datetime(df["fertile_start"])
    df["fertile_end"] = pd.to_datetime(df["fertile_end"])

    today = datetime.now().date()

    # Find the current or most recent cycle
    past_cycles = df[df["period_start"].dt.date <= today].sort_values("period_start", ascending=False)
    current_cycle = past_cycles.iloc[0] if len(past_cycles) > 0 else None

    # Compute current phase
    phase = None
    days_into_cycle = None
    days_until_next_period = None
    next_cycle = df[df["period_start"].dt.date > today].sort_values("period_start").iloc[0] if len(df[df["period_start"].dt.date > today]) > 0 else None

    if current_cycle is not None:
        period_start = current_cycle["period_start"].date()
        period_end = current_cycle["period_end"].date()
        fertile_start = current_cycle["fertile_start"].date()
        fertile_end = current_cycle["fertile_end"].date()
        ovulation_date = current_cycle["ovulation_date"].date()
        days_into_cycle = (today - period_start).days

        if period_start <= today <= period_end:
            phase = "menstrual"
        elif fertile_start <= today <= ovulation_date:
            phase = "ovulation"
        elif today > ovulation_date:
            phase = "luteal"
        else:
            phase = "follicular"

    if next_cycle is not None:
        days_until_next_period = (next_cycle["period_start"].date() - today).days

    # Serialize — convert Timestamps to strings for JSON
    def serialize_cycle(row):
        return {
            "period_length_days": int(row["period_length_days"]),
            "cycle_number": int(row["cycle_number"]),
            "period_start": str(row["period_start"].date()),
            "period_end": str(row["period_end"].date()),
            "ovulation_date": str(row["ovulation_date"].date()),
            "fertile_start": str(row["fertile_start"].date()),
            "fertile_end": str(row["fertile_end"].date()),
            "cycle_id": row["cycle_id"],
        }

    return {
        "athlete_id": athlete_id,
        "data_type": "menstrual_cycle",
        "today": str(today),
        "current_phase": phase,
        "days_into_cycle": days_into_cycle,
        "days_until_next_period": days_until_next_period,
        "current_cycle": serialize_cycle(current_cycle) if current_cycle is not None else None,
        "next_cycle": serialize_cycle(next_cycle) if next_cycle is not None else None,
        "all_cycles": [serialize_cycle(row) for _, row in df.sort_values("period_start").iterrows()],
        "count": len(df),
    }

@router.get("/latest")
def get_latest_metrics(athlete_id: str):
    """Get latest cycle phase — only valid wearable data available"""
    cycle_response = get_cycle_data(athlete_id)
    return {
        "athlete_id": athlete_id,
        "sync_time": datetime.now().isoformat(),
        "current_phase": cycle_response["current_phase"],
        "days_into_cycle": cycle_response["days_into_cycle"],
        "days_until_next_period": cycle_response["days_until_next_period"],
        "current_cycle": cycle_response["current_cycle"],
        "next_cycle": cycle_response["next_cycle"],
    }
