import pandas as pd
import hashlib
from datetime import timedelta
import random

df = pd.read_csv('../data/com.samsung.shealth.activity.day_summary.20260221152104.csv', skiprows=1)
df_clean = pd.DataFrame({
    'date': pd.to_datetime(df[df.columns[df.columns.str.contains('day_time|date', case=False)][0]] if any(df.columns.str.contains('day_time|date', case=False)) else None, errors='coerce'),
    'steps': pd.to_numeric(df[df.columns[df.columns.str.contains('step', case=False)][0]] if any(df.columns.str.contains('step', case=False)) else None, errors='coerce'),
    'calories': pd.to_numeric(df[df.columns[df.columns.str.contains('calorie', case=False)][0]] if any(df.columns.str.contains('calorie', case=False)) else None, errors='coerce'),
    'distance': pd.to_numeric(df[df.columns[df.columns.str.contains('distance', case=False)][0]] if any(df.columns.str.contains('distance', case=False)) else None, errors='coerce'),
    'activity_id': df[df.columns[df.columns.str.contains('datauuid', case=False)][0]].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None) if any(df.columns.str.contains('datauuid', case=False)) else None
})

shift = random.randint(30, 60)
df_clean['date'] = df_clean['date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/activity_clean.csv', index=False)
print(f"[DONE] Activity: {len(df_clean)} records")
