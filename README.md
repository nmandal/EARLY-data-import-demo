# EARLY import

Import your data files in the corresponding directory in `data`, run `main.py` and your data will be cleaned, transformed, and outputted into weekly, monthly, quarterly, yearly arrears as well as into plain text.

- `health` from Apple Health key columns
  - Date
  - Active energy burned(Cal)
  - Apple Watch stand hours(hr)
  - Basal energy burned(Cal)
  - Exercise time(min)
  - Flights climbed(count)
  - Resting heart rate(count/min)
  - Stand time(min)
  - Step count(count)
  - VO2 Max(mL/min·kg)
  - Mindfulness(min)


- `workouts` from Apple Workouts key columns
  - Date
  - Active energy burned(Cal)
  - Activity
  - Duration(s)
  - Heart rate zone: A Easy (<115bpm)(%)
  - Heart rate zone: B Fat Burn (115-135bpm)(%)
  - Heart rate zone: C Moderate Training (135-155bpm)(%)
  - Heart rate zone: D Hard Training (155-175bpm)(%)
  - Heart rate zone: E Extreme Training (>175bpm)(%)
  - Heart rate: Average(count/min)
  - Heart rate: Maximum(count/min)
  - METs Average(kcal/hr·kg)'

- `oura` from Oura ring columns
  - date
  - Total Sleep Duration
  - Bedtime Start
  - Bedtime End
  - Total Bedtime
  - Awake Time
  - REM Sleep Duration
  - Light Sleep Duration
  - Deep Sleep Duration
  - Restless Sleep
  - Sleep Efficiency
  - Sleep Latency
  - Average Resting Heart Rate
  - Lowest Resting Heart Rate
  - Average HRV
  - Temperature Deviation (°C)
  - Respiratory Rate
  - Inactive Time
  - Average MET

- `levels` from Levels CGM key columns
  - Time (Local)
  - Type
  - Notes
  - Photo Link


- `misc` data key columns
  - Weight (lbs)