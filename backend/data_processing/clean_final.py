import pandas as pd
import hashlib
from datetime import timedelta
import random

shift = random.randint(30, 60)

# Sleep stages - use column index
df = pd.read_csv('../data/com.samsung.health.sleep_stage.20260221152104.csv', skiprows=2, header=None)
df_clean = pd.DataFrame({
    'sleep_start': pd.to_datetime(df[0], errors='coerce'),
    'sleep_id': df[1].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None),
    'stage': pd.to_numeric(df[6], errors='coerce')
})
df_clean['sleep_start'] = df_clean['sleep_start'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['sleep_start']).sort_values('sleep_start').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/sleep_stage_clean.csv', index=False)
print(f"Sleep stages: {len(df_clean)}")

# Heart rate
df = pd.read_csv('../data/com.samsung.shealth.tracker.heart_rate.20260221152104.csv', skiprows=2, header=None)
df_clean = pd.DataFrame({
    'timestamp': pd.to_datetime(df[1], errors='coerce'),
    'heart_rate': pd.to_numeric(df[5], errors='coerce'),
    'hr_id': df[11].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['timestamp'] = df_clean['timestamp'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/heart_rate_clean.csv', index=False)
print(f"Heart rate: {len(df_clean)}")

# Mood & Flow
df = pd.read_csv('../data/com.samsung.health.cycle.mood.20260221152104.csv', skiprows=2, header=None)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df[0], errors='coerce'),
    'mood': df[1],
    'mood_id': df[5].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/cycle_mood_clean.csv', index=False)
print(f"Mood: {len(df_clean)}")

df = pd.read_csv('../data/com.samsung.health.cycle.flow.20260221152104.csv', skiprows=2, header=None)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df[0], errors='coerce'),
    'flow_level': df[1],
    'flow_id': df[5].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/cycle_flow_clean.csv', index=False)
print(f"Flow: {len(df_clean)}")
