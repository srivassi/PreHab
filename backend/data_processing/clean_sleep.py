import pandas as pd
import hashlib
from datetime import timedelta
import random

df = pd.read_csv('../data/com.samsung.shealth.sleep.20260221152104.csv', skiprows=1)
df_clean = pd.DataFrame({
    'sleep_start': pd.to_datetime(df['com.samsung.health.sleep.start_time'], errors='coerce'),
    'sleep_end': pd.to_datetime(df['com.samsung.health.sleep.end_time'], errors='coerce'),
    'duration_min': pd.to_numeric(df['sleep_duration'], errors='coerce'),
    'sleep_score': pd.to_numeric(df['sleep_score'], errors='coerce'),
    'sleep_id': df['com.samsung.health.sleep.datauuid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

shift = random.randint(30, 60)
for col in ['sleep_start', 'sleep_end']:
    df_clean[col] = df_clean[col].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['sleep_start']).sort_values('sleep_start').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/sleep_clean.csv', index=False)
print(f"[DONE] Sleep: {len(df_clean)} records")
