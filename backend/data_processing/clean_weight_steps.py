import pandas as pd
import hashlib
from datetime import timedelta
import random

shift = random.randint(30, 60)

# Weight
df = pd.read_csv('../data/com.samsung.health.weight.20260221152104.csv', skiprows=2, header=None)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df[0], errors='coerce'),
    'weight_kg': pd.to_numeric(df[1], errors='coerce'),
    'weight_id': df[7].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/weight_clean.csv', index=False)
print(f"Weight: {len(df_clean)}")

# Steps
df = pd.read_csv('../data/com.samsung.shealth.tracker.pedometer_day_summary.20260221152104.csv', skiprows=2, header=None)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df[0], errors='coerce'),
    'steps': pd.to_numeric(df[6], errors='coerce'),
    'distance_m': pd.to_numeric(df[7], errors='coerce'),
    'calories': pd.to_numeric(df[8], errors='coerce'),
    'steps_id': df[15].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/steps_clean.csv', index=False)
print(f"Steps: {len(df_clean)}")
