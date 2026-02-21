import pandas as pd
import hashlib
from datetime import timedelta
import random

# Mood data
df_mood = pd.read_csv('../data/com.samsung.health.cycle.mood.20260221152104.csv', skiprows=1)
date_col = [c for c in df_mood.columns if 'date' in c.lower()][0]
mood_col = [c for c in df_mood.columns if 'mood' in c.lower()][0]
uuid_col = [c for c in df_mood.columns if 'uuid' in c.lower()][-1]

df_mood_clean = pd.DataFrame({
    'date': pd.to_datetime(df_mood[date_col], errors='coerce'),
    'mood': df_mood[mood_col],
    'mood_id': df_mood[uuid_col].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

# Flow data
df_flow = pd.read_csv('../data/com.samsung.health.cycle.flow.20260221152104.csv', skiprows=1)
date_col_f = [c for c in df_flow.columns if 'date' in c.lower()][0]
flow_col = [c for c in df_flow.columns if 'flow' in c.lower()][0]
uuid_col_f = [c for c in df_flow.columns if 'uuid' in c.lower()][-1]

df_flow_clean = pd.DataFrame({
    'date': pd.to_datetime(df_flow[date_col_f], errors='coerce'),
    'flow_level': df_flow[flow_col],
    'flow_id': df_flow[uuid_col_f].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

shift = random.randint(30, 60)
for df in [df_mood_clean, df_flow_clean]:
    df['date'] = df['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)

df_mood_clean = df_mood_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_flow_clean = df_flow_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)

df_mood_clean.to_csv('../data/cleaned/cycle_mood_clean.csv', index=False)
df_flow_clean.to_csv('../data/cleaned/cycle_flow_clean.csv', index=False)
print(f"[DONE] Mood: {len(df_mood_clean)} records, Flow: {len(df_flow_clean)} records")
