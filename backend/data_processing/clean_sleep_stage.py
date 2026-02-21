import pandas as pd
import hashlib
from datetime import timedelta
import random

df = pd.read_csv('../data/com.samsung.health.sleep_stage.20260221152104.csv', skiprows=1)
start_col = [c for c in df.columns if 'start' in c.lower()][0]
end_col = [c for c in df.columns if 'end' in c.lower()][0]
stage_col = [c for c in df.columns if 'stage' in c.lower()][0]
uuid_col = [c for c in df.columns if 'uuid' in c.lower()][-1]

df_clean = pd.DataFrame({
    'sleep_start': pd.to_datetime(df[start_col], errors='coerce'),
    'sleep_end': pd.to_datetime(df[end_col], errors='coerce'),
    'stage': df[stage_col],
    'sleep_id': df[uuid_col].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

shift = random.randint(30, 60)
for col in ['sleep_start', 'sleep_end']:
    df_clean[col] = df_clean[col].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)

df_clean = df_clean.dropna(subset=['sleep_start']).sort_values('sleep_start').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/sleep_stage_clean.csv', index=False)
print(f"[DONE] Sleep stages: {len(df_clean)} records")
