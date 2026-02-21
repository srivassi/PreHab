from pydantic import BaseModel
from typing import List, Optional

# ── Input schemas ────────────────────────────────────────────

class AthleteInput(BaseModel):
    athlete_id:            str
    cycle_phase:           int    # 0=menstrual, 1=follicular, 2=ovulatory, 3=luteal
    acute_chronic_ratio:   float
    knee_soreness:         int    # 0-10
    hamstring_soreness:    int    # 0-10
    groin_soreness:        int    # 0-10
    session_rpe:           float  # 1-10
    weekly_load:           float
    days_since_last_rest:  int
    last_7_days_soreness:  List[int]    # for trend detection
    last_7_days_load:      List[float]  # for trend detection

class TrainingLogCreate(BaseModel):
    athlete_id:    str
    date:          str
    sport:         str
    duration_mins: int
    intensity:     float
    rpe:           float
    knee_soreness:      Optional[int] = 0
    hamstring_soreness: Optional[int] = 0
    groin_soreness:     Optional[int] = 0

class CycleLogCreate(BaseModel):
    athlete_id:          str
    cycle_start_date:    str
    cycle_length_days:   int
    menstruation_length: int
    on_contraceptive:    Optional[int] = 0

class UserCreate(BaseModel):
    email: str
    name:  str
    sport: str

class EscalationCreate(BaseModel):
    athlete_id:    str
    risk_level:    str
    analysis_id:   str
    coach_email:   Optional[str] = None
    physio_email:  Optional[str] = None

# ── Output schemas ───────────────────────────────────────────

class RiskProfile(BaseModel):
    acl_risk:               float
    soft_tissue_risk:       float
    overtraining_risk:      float
    recovery_status:        float
    performance_readiness:  float

class TrendAnalysis(BaseModel):
    load_trajectory:      str
    soreness_trajectory:  str
    cycle_risk_window:    str
    acute_chronic_ratio:  float

class ContributingFactor(BaseModel):
    factor:       str
    contribution: float
    label:        str

class InjuryWindowForecast(BaseModel):
    next_3_days:  str
    next_7_days:  str
    next_14_days: str

class AnalysisResponse(BaseModel):
    risk_profile:            RiskProfile
    trend_analysis:          TrendAnalysis
    contributing_factors:    List[ContributingFactor]
    confidence:              float
    composite_risk_level:    str   # LOW / MEDIUM / HIGH / CRITICAL
    recommended_actions:     List[str]
    injury_window_forecast:  InjuryWindowForecast
    explanation:             Optional[str] = None  # Crusoe-generated
