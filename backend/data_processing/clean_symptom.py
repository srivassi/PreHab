import pandas as pd
import hashlib
from datetime import timedelta
import random

df = pd.read_csv('../data/com.samsung.health.cycle.symptom.20260221152104.csv', skiprows=1)
print(f"Total rows: {len(df)}")

# Find relevant columns
symptom_cols = [col for col in df.columns if 'symptom' in col.lower() or 'date' in col.lower() or 'uuid' in col.lower()]
print(f"Symptom columns: {symptom_cols[:10]}")

# Extract key columns
df_clean = pd.DataFrame({
    'log_date': pd.to_datetime(df[df.columns[df.columns.str.contains('date', case=False)][0]] if any(df.columns.str.contains('date', case=False)) else None, errors='coerce'),
    'symptom_type': df[df.columns[df.columns.str.contains('symptom', case=False)][0]] if any(df.columns.str.contains('symptom', case=False)) else None,
    'symptom_id': df[df.columns[df.columns.str.contains('datauuid', case=False)][0]].apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest()[:16] if pd.notna(x) else None) if any(df.columns.str.contains('datauuid', case=False)) else None
})

shift = random.randint(30, 60)
df_clean['log_date'] = df_clean['log_date'].apply(lambda x: (x + timedelta(days=shift)).strftime('%Y-%m-%d') if pd.notna(x) else None)

df_clean = df_clean.dropna(subset=['log_date']).sort_values('log_date').reset_index(drop=True)
df_clean.to_csv('../data/cleaned/symptom_clean.csv', index=False)
print(f"[DONE] Symptom: {len(df_clean)} records")
