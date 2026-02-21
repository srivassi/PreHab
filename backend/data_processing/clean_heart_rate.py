import pandas as pd
import hashlib
from datetime import timedelta
import random

df = pd.read_csv('../data/com.samsung.shealth.tracker.heart_rate.20260221152104.csv', skiprows=1)
time_col = [c for c in df.columns if 'time' in c.lower() and 'update' not in c.lower() and 'create' not in c.lower()][0]
hr_col = [c for c in df.columns if 'heart_rate' in c.lower() and 'max' not in c.lower() and 'min' not in c.lower()][0]
uuid_col = [c for c in df.columns if 'uuid' in c.lower()][-1]

df_clean = pd.DataFrame({
    'timestamp': pd.to_datetime(df[time_col], errors='coerce'),
    'heart_rate': pd.to_numeric(df[hr_col], errors='coerce'),
    'hr_id': df[uuid_col].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

shift = random.randint(30, 60)
df_clean['timestamp'] = df_clean['timestamp'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(x) else None)
df_clean = df_clean.dropna(subset=['timestamp', 'heart_rate']).sort_values('timestamp').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/heart_rate_clean.csv', index=False)
print(f"[DONE] Heart rate: {len(df_clean)} records")
