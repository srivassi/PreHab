import pandas as pd
import hashlib
from datetime import timedelta
import random

df = pd.read_csv('../data/com.samsung.shealth.stress.20260221152104.csv', skiprows=1)
df_clean = pd.DataFrame({
    'timestamp': pd.to_datetime(df['start_time'], errors='coerce'),
    'stress_score': pd.to_numeric(df['score'], errors='coerce'),
    'stress_max': pd.to_numeric(df['max'], errors='coerce'),
    'stress_min': pd.to_numeric(df['min'], errors='coerce'),
    'stress_id': df['datauuid'].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

shift = random.randint(30, 60)
df_clean['timestamp'] = df_clean['timestamp'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/stress_clean.csv', index=False)
print(f"[DONE] Stress: {len(df_clean)} records")
