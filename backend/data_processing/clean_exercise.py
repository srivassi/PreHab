import pandas as pd
import hashlib
from datetime import datetime, timedelta
import random

# Read exercise data
df = pd.read_csv('../data/com.samsung.shealth.exercise.20260221152104.csv', skiprows=1)

print(f"Total rows: {len(df)}")

# Find columns by keyword
def find_col(keyword, exclude=None):
    exclude = exclude or []
    for col in df.columns:
        if keyword in col.lower() and not any(ex in col.lower() for ex in exclude):
            return col
    return None

# Map columns
cols_to_extract = {
    find_col('start_time'): 'start_time',
    find_col('end_time'): 'end_time',
    find_col('duration'): 'duration_ms',
    find_col('exercise_type'): 'exercise_type',
    find_col('calorie', ['mean', 'max', 'burn']): 'calories',
    find_col('distance', ['incline', 'decline']): 'distance_m',
    find_col('mean_heart_rate'): 'mean_hr',
    find_col('max_heart_rate'): 'max_hr',
    find_col('min_heart_rate'): 'min_hr',
    find_col('mean_speed'): 'mean_speed',
    find_col('datauuid'): 'session_id'
}

# Remove None keys
cols_to_extract = {k: v for k, v in cols_to_extract.items() if k is not None}

# Extract and rename
df_clean = df[list(cols_to_extract.keys())].copy()
df_clean.columns = list(cols_to_extract.values())

print(f"Extracted columns: {df_clean.columns.tolist()}")

# Anonymize session IDs
def anonymize_id(val):
    if pd.isna(val) or str(val).strip() == '':
        return None
    return hashlib.sha256(str(val).encode()).hexdigest()[:16]

if 'session_id' in df_clean.columns:
    df_clean['session_id'] = df_clean['session_id'].apply(anonymize_id)

# Shift dates
date_shift = random.randint(30, 60)

def shift_date(date_str):
    if pd.isna(date_str) or str(date_str).strip() == '':
        return None
    try:
        dt = pd.to_datetime(date_str)
        return (dt + timedelta(days=date_shift)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

if 'start_time' in df_clean.columns:
    df_clean['start_time'] = df_clean['start_time'].apply(shift_date)
if 'end_time' in df_clean.columns:
    df_clean['end_time'] = df_clean['end_time'].apply(shift_date)

# Convert duration to minutes
if 'duration_ms' in df_clean.columns:
    df_clean['duration_min'] = pd.to_numeric(df_clean['duration_ms'], errors='coerce') / 60000
    df_clean = df_clean.drop('duration_ms', axis=1)

# Remove rows with missing critical data
df_clean = df_clean.dropna(subset=['start_time'], how='all')

# Sort by date
if 'start_time' in df_clean.columns:
    df_clean = df_clean.sort_values('start_time').reset_index(drop=True)

# Save
df_clean.to_csv('../data/cleaned/exercise_clean.csv', index=False)
print(f"[DONE] Exercise data cleaned: {len(df_clean)} records")
if len(df_clean) > 0 and 'start_time' in df_clean.columns:
    print(f"  Date range: {df_clean['start_time'].min()} to {df_clean['start_time'].max()}")
