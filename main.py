import os
import math
from collections import defaultdict

import numpy as np
import pandas as pd


def get_change(current, previous):
  # Returns the change in the current value from the previous value
  if current == previous:
    return 0
  try:
    diff = (abs(current - previous) / previous) * 100.0
    return round(-1 * diff, 1) if current <= previous else round(diff, 1)
  except ZeroDivisionError:
    return float('inf')


def convert_seconds_to_hours_minutes(seconds):
  hours = seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = seconds % 60
  return hours, minutes


key_metrics = defaultdict(lambda: defaultdict(list))
workouts = defaultdict()

df_map = {
  './data/oura': [],
  './data/health': [],
  './data/workouts': [],
  './data/levels': [],
  './data/misc': []
}
vo2_df = None
for file_dir in df_map.keys():
  df_list = []

  # create dataframes for each file in the df_map
  if os.path.isdir(file_dir):
    for filename in os.listdir(file_dir):
      f = os.path.join(file_dir, filename)
      if os.path.isfile(f) and f.endswith('.csv'):
        df = pd.read_csv(f)
        if 'Vo2Max' in filename:
          if vo2_df is None:
            vo2_df = df
          else:
            vo2_df = pd.concat([vo2_df, df])
          vo2_df = df
          vo2_df['Date'] = vo2_df['Date'].apply(lambda x: x.split()[0])
          vo2_df = vo2_df.groupby(vo2_df['Date']).aggregate({
            'VO2 Max(mL/min·kg)':
            'last',
            'Mindfulness(min)':
            'last'
          }).reset_index()
          vo2_df = vo2_df.fillna(0)
        else:
          df_list.append(df)

    master_df = pd.concat(df_list)

    if 'oura' in file_dir:
      file_type = 'oura'
      key = 'date'
      cols = [
        'date', 'Total Sleep Duration', 'Bedtime Start', 'Bedtime End',
        'Total Bedtime ', 'Awake Time', 'REM Sleep Duration',
        'Light Sleep Duration', 'Deep Sleep Duration', 'Restless Sleep',
        'Sleep Efficiency', 'Sleep Latency', 'Average Resting Heart Rate',
        'Lowest Resting Heart Rate', 'Average HRV',
        'Temperature Deviation (°C)', 'Respiratory Rate', 'Inactive Time',
        'Average MET'
      ]
    elif 'health' in file_dir:
      file_type = 'health'
      key = 'Date'
      cols = [
        'Date', 'Active energy burned(Cal)', 'Apple Watch stand hours(hr)',
        'Basal energy burned(Cal)', 'Exercise time(min)',
        'Flights climbed(count)', 'Resting heart rate(count/min)',
        'Stand time(min)', 'Step count(count)', 'VO2 Max(mL/min·kg)',
        'Mindfulness(min)'
      ]
      if vo2_df is not None:
        master_df = pd.merge(master_df, vo2_df, how='left', on='Date')
    elif 'workouts' in file_dir:
      file_type = 'workouts'
      key = 'Date'
      cols = [
        'Date', 'Active energy burned(Cal)', 'Activity', 'Duration(s)',
        'Heart rate zone: A Easy (<115bpm)(%)',
        'Heart rate zone: B Fat Burn (115-135bpm)(%)',
        'Heart rate zone: C Moderate Training (135-155bpm)(%)',
        'Heart rate zone: D Hard Training (155-175bpm)(%)',
        'Heart rate zone: E Extreme Training (>175bpm)(%)',
        'Heart rate: Average(count/min)', 'Heart rate: Maximum(count/min)',
        'METs Average(kcal/hr·kg)'
      ]
      master_df['Date'] = master_df['Date'].apply(
        lambda x: ' '.join(x.split()[:2]))
    elif 'levels' in file_dir:
      file_type = 'levels'
      key = 'Time (Local)'
      cols = ['Time (Local)', 'Type', 'Notes', 'Photo Link']
      master_df = master_df[(master_df['Type'] != 'exercise')
                            & (master_df['Type'] != 'sleep')]
    elif 'misc' in file_dir:
      file_type = 'misc'
      key = 'Date'
      cols = ['Date', 'Weight (lb)']
      master_df['Date'] = master_df['Date'].apply(lambda x: x.split()[0])

    master_df = master_df.drop_duplicates(subset=[key], keep="last")

    master_df[key] = pd.to_datetime(master_df[key])
    master_df = master_df[cols]

    outdir = f'./out/{file_type}/'
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    master_df.to_csv(f'{outdir}/master.csv', index=False)

    for freq in ['W', 'M', 'Q', 'Y']:
      dfs = [
        group for _, group in master_df.groupby(pd.Grouper(key=key, freq=freq))
      ]

      for df in dfs:
        if not df.empty:
          name = str(df.iloc[0][key])[:10]
          outdir = f'./out/{file_type}/{freq}/{name}'
          if not os.path.exists(outdir):
            os.makedirs(outdir)
          df.to_csv(f'{outdir}/data.csv', index=False)

          with open(f'./out/{file_type}/{freq}/story.txt', "a") as f:
            print(file_type, freq, name, file=f)

            if file_type == 'oura':
              print('{:,} days of tracked sleep for {} {}'.format(
                len(df), freq, name),
                    file=f)
              for metric, d in {
                  'Total Sleep Duration': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Total Bedtime ': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Awake Time': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'REM Sleep Duration': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Light Sleep Duration': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Deep Sleep Duration': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Restless Sleep': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Average Resting Heart Rate': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Lowest Resting Heart Rate': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Average HRV': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Inactive Time': {
                    'type': 'time_duration',
                    'precision': None,
                    'drop': 'any'
                  },
                  'Average MET': {
                    'type': 'number',
                    'precision': 2,
                    'drop': 'any'
                  }
              }.items():
                n = len(df[metric].dropna(how=d['drop']))
                curr = df[metric].dropna(how=d['drop']).mean()
                if d['type'] == 'number':
                  curr_str = round(curr, d['precision'])
                elif d['type'] == 'time_duration':
                  hours, minutes = convert_seconds_to_hours_minutes(curr)
                  curr_str = f'{round(hours)}h {round(minutes)}m'

                try:
                  prev = key_metrics[metric][freq][-1]
                  if d['type'] == 'number':
                    prev_str = round(prev, d['precision'])
                  elif d['type'] == 'time_duration':
                    hours, minutes = convert_seconds_to_hours_minutes(prev)
                    prev_str = f'{round(hours)}h {round(minutes)}m'
                  diff = get_change(curr, prev)
                except (IndexError, KeyError) as e:
                  diff = 'n/a'
                  prev_str = 'n/a'

                key_metrics[metric][freq].append(curr)
                print('{} {} {}% {}o{} (prev: {}), (n={})'.format(
                  curr_str, metric, diff, freq, freq, prev_str, n),
                      file=f)

            elif file_type == 'health':
              print('{:,} days of tracked health for {} {}'.format(
                len(df), freq, name),
                    file=f)
              for metric, d in {
                  'Active energy burned(Cal)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Basal energy burned(Cal)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Exercise time(min)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Flights climbed(count)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Resting heart rate(count/min)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'Step count(count)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  },
                  'VO2 Max(mL/min·kg)': {
                    'type': 'number',
                    'precision': 2,
                    'drop': 'any'
                  },
                  'Mindfulness(min)': {
                    'type': 'number',
                    'precision': 0,
                    'drop': 'any'
                  }
              }.items():
                n = len(df[metric].dropna(how=d['drop']))
                if d['type'] == 'number':
                  curr = df[metric].dropna(how=d['drop']).mean()
                  curr_str = round(curr, d['precision'])

                try:
                  prev = key_metrics[metric][freq][-1]
                  prev_str = round(prev, d['precision'])
                  diff = get_change(curr, prev)
                except (IndexError, KeyError) as e:
                  diff = 'n/a'

                key_metrics[metric][freq].append(curr)
                print('{} {} {}% {}o{} (prev: {}), (n={})'.format(
                  curr_str, metric, diff, freq, freq, prev_str, n),
                      file=f)

            elif file_type == 'workouts':
              print('{:,} tracked workouts for {} {}'.format(
                len(df), freq, name),
                    file=f)
              value_count = df['Activity'].value_counts()
              for x, y in value_count.items():
                workouts[x] = {'count': y}

              value_agg = df.groupby('Activity').agg({
                'Active energy burned(Cal)':
                np.mean,
                'Heart rate zone: A Easy (<115bpm)(%)':
                np.mean,
                'Heart rate zone: B Fat Burn (115-135bpm)(%)':
                np.mean,
                'Heart rate zone: C Moderate Training (135-155bpm)(%)':
                np.mean,
                'Heart rate zone: D Hard Training (155-175bpm)(%)':
                np.mean,
                'Heart rate zone: E Extreme Training (>175bpm)(%)':
                np.mean,
                'Heart rate: Average(count/min)':
                np.mean,
                'Heart rate: Maximum(count/min)':
                np.mean,
                'METs Average(kcal/hr·kg)':
                'sum',
                'Duration(s)':
                'sum'
              })
              for x, y in value_agg.iterrows():
                workouts[x].update(y.to_dict())

              for workout, d in workouts.items():
                if not math.isnan(d['Heart rate: Average(count/min)']):
                  print(
                    f"""{d['count']} bouts of {workout} for {round(d['Duration(s)']//3600)} hours {round(d['Duration(s)']//60)%60} minutes. Avg calories: {round(d['Active energy burned(Cal)'])}, METs: {round(d['METs Average(kcal/hr·kg)'], 2)}, Avg HR: {round(d['Heart rate: Average(count/min)'])}, Max HR: {round(d['Heart rate: Maximum(count/min)'])}.
                                          {round(d['Heart rate zone: A Easy (<115bpm)(%)'], 2)} zone 1, {round(d['Heart rate zone: B Fat Burn (115-135bpm)(%)'], 2)} zone 2, {round(d['Heart rate zone: C Moderate Training (135-155bpm)(%)'], 2)} zone 3, {round(d['Heart rate zone: D Hard Training (155-175bpm)(%)'], 2)} zone 4, {round(d['Heart rate zone: E Extreme Training (>175bpm)(%)'], 2)} zone 5""",
                    file=f)

            elif file_type == 'levels':
              print('{:,} logs for {} {}'.format(len(df), freq, name), file=f)
              food_df = df[df['Type'] == 'food']

            elif file_type == 'misc':
              print('{:,} tracked misc logs for {} {}'.format(
                len(df), freq, name),
                    file=f)
              for metric, d in {
                  'Weight (lb)': {
                    'type': 'number',
                    'precision': 1,
                    'drop': 'any'
                  }
              }.items():

                n = len(df[metric].dropna(how=d['drop']))
                if d['type'] == 'number':
                  curr = df[metric].dropna(how=d['drop']).mean()
                  curr_str = round(curr, d['precision'])

                try:
                  prev = key_metrics[metric][freq][-1]
                  prev_str = round(prev, d['precision'])
                  diff = get_change(curr, prev)
                except (IndexError, KeyError) as e:
                  diff = 'n/a'

                key_metrics[metric][freq].append(curr)
                print('{} {} {}% {}o{} (prev: {}), (n={})'.format(
                  curr_str, metric, diff, freq, freq, prev_str, n),
                      file=f)
