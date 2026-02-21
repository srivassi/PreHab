import pandas as pd
import hashlib
from datetime import timedelta
import random

shift = random.randint(30, 60)

# Sleep stages
df = pd.read_csv('../data/com.samsung.health.sleep_stage.20260221152104.csv', skiprows=1)
df_clean = pd.DataFrame({
    'sleep_start': pd.to_datetime(df['start_time'], errors='coerce'),
    'stage': pd.to_numeric(df['stage'], errors='coerce'),
    'sleep_id': df['sleep_id'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['sleep_start'] = df_clean['sleep_start'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['sleep_start']).sort_values('sleep_start').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/sleep_stage_clean.csv', index=False)
print(f"Sleep stages: {len(df_clean)}")

# Heart rate
df = pd.read_csv('../data/com.samsung.shealth.tracker.heart_rate.20260221152104.csv', skiprows=1)
time_col = [c for c in df.columns if 'time' in c.lower() and 'update' not in c.lower() and 'create' not in c.lower()][0]
hr_col = [c for c in df.columns if 'heart_rate' in c.lower() and 'max' not in c.lower() and 'min' not in c.lower()][0]
df_clean = pd.DataFrame({
    'timestamp': pd.to_datetime(df[time_col], errors='coerce'),
    'heart_rate': pd.to_numeric(df[hr_col], errors='coerce'),
    'hr_id': df['com.samsung.health.heart_rate.datauuid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['timestamp'] = df_clean['timestamp'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/heart_rate_clean.csv', index=False)
print(f"Heart rate: {len(df_clean)}")

# Mood
df = pd.read_csv('../data/com.samsung.health.cycle.mood.20260221152104.csv', skiprows=1)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df['date'], errors='coerce'),
    'mood': df['mood'],
    'mood_id': df['datauuid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/cycle_mood_clean.csv', index=False)
print(f"Mood: {len(df_clean)}")

# Flow
df = pd.read_csv('../data/com.samsung.health.cycle.flow.20260221152104.csv', skiprows=1)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df['date'], errors='coerce'),
    'flow_level': df['flow'],
    'flow_id': df['datauuid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/cycle_flow_clean.csv', index=False)
print(f"Flow: {len(df_clean)}")

print("[DONE] All additional datasets cleaned")
