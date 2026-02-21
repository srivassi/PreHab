import pandas as pd
import hashlib
from datetime import timedelta
import random

# Read without header first to see structure
df = pd.read_csv('../data/com.samsung.shealth.cycle.prediction.20260221152104.csv', skiprows=2, header=None)

# Columns based on actual CSV: period,source,fertile_window_start_date,update_time,create_time,data_version,ovulation_status,cycle,menstruation_start_date,deviceuuid,original_period_prediction_date,ovulation_date,menstruation_end_date,unrealistic_menstruation,pkg_name,datauuid,fertile_window_end_date
df_clean = pd.DataFrame({
    'period_length_days': pd.to_numeric(df[0], errors='coerce'),
    'cycle_number': pd.to_numeric(df[7], errors='coerce'),
    'period_start': pd.to_datetime(df[8], errors='coerce'),
    'period_end': pd.to_datetime(df[12], errors='coerce'),
    'ovulation_date': pd.to_datetime(df[11], errors='coerce'),
    'fertile_start': pd.to_datetime(df[2], errors='coerce'),
    'fertile_end': pd.to_datetime(df[16], errors='coerce'),
    'cycle_id': df[15].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None)
})

shift = random.randint(30, 60)
for col in ['period_start', 'period_end', 'ovulation_date', 'fertile_start', 'fertile_end']:
    df_clean[col] = df_clean[col].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)

df_clean = df_clean.dropna(subset=['period_start']).sort_values('period_start').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/cycle_clean.csv', index=False)
print(f"[DONE] Cycle: {len(df_clean)} records")
