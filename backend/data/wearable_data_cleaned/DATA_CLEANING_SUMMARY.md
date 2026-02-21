# PreHab Wearable Data Cleaning Summary

## ✅ Successfully Cleaned Datasets

### Core Training & Activity Data
1. **Exercise Sessions** - `exercise_clean.csv`
   - 2,519 records
   - Columns: start_time, end_time, duration_min, exercise_type, calories, distance_m, mean_hr, max_hr, min_hr, mean_speed, session_id

2. **Daily Activity Summary** - `activity_clean.csv`
   - 820 records
   - Columns: date, steps, calories, distance, activity_id

3. **Heart Rate** - `heart_rate_clean.csv`
   - 8,217 records
   - Columns: timestamp, heart_rate, hr_id

### Menstrual Cycle Data
4. **Cycle Prediction** - `cycle_clean.csv`
   - 28 records
   - Columns: period_length_days, cycle_number, period_start, period_end, ovulation_date, fertile_start, fertile_end, cycle_id

5. **Cycle Symptoms** - `symptom_clean.csv`
   - 86 records
   - Columns: log_date, symptom_type, symptom_id

6. **Cycle Mood** - `cycle_mood_clean.csv`
   - 127 records
   - Columns: date, mood, mood_id

7. **Cycle Flow** - `cycle_flow_clean.csv`
   - 150 records
   - Columns: date, flow_level, flow_id

## 📊 Total Dataset Summary
- **Total Records**: 11,947 anonymized records
- **Total Datasets**: 7 cleaned datasets
- **Date Range**: All dates shifted by 30-60 days for privacy
- **IDs**: All UUIDs hashed with SHA-256 (16-char)

## 🔒 Anonymization Applied
- ✅ All personal IDs hashed (SHA-256)
- ✅ All timestamps shifted (30-60 day random offset)
- ✅ All device IDs anonymized
- ✅ All location data removed
- ✅ All external references stripped

## 📁 Output Location
All cleaned files: `backend/data/cleaned/`

## 🎯 PreHab Use Cases
These datasets support:
- Training load monitoring (exercise + activity + heart rate)
- Menstrual cycle phase tracking (cycle prediction + flow + mood)
- Injury risk assessment (combining training load with cycle phase)
- Recovery monitoring (heart rate variability, symptoms)
- Personalized training adjustments based on hormonal fluctuations

## ⚠️ Datasets Not Processed
- Sleep (main file): No valid timestamps in source data
- Stress (main file): No valid timestamps in source data
- Sleep stages: Column misalignment issues in source CSV

## 🔄 Data Processing Scripts
All cleaning scripts located in: `backend/data_processing/`
- clean_exercise.py
- clean_cycle.py
- clean_symptom.py
- clean_activity.py
- clean_final.py (heart rate, mood, flow)
