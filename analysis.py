import pandas as pd

# 1. Load the 1-minute stock index data (assumed to have columns: ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
#data = pd.read_csv('D:/NIFTY 50 - Minute data.csv/NIFTY 50 - Minute data.csv', parse_dates=['Timestamp'])
data = pd.read_csv('D:/NIFTY 50 - Minute data.csv/NIFTY 50 - Minute data.csv', parse_dates=['Timestamp'], date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S'))

# 2. Resample to 15-minute data
#data.set_index('Timestamp', inplace=True)
print(data.head()) 
print(data.tail()) 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data and ensure all timestamps are accounted for
data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%Y-%m-%d %H:%M:%S')
data.set_index('Timestamp', inplace=True)

# Ensure there is no missing data and that the time range is correct
print(f"Data range: {data.index.min()} to {data.index.max()}")
print(f"Total number of rows: {len(data)}")

# Filter data to trading hours
data = data.between_time('09:15', '15:30')

# Check if we still have data after filtering
print(f"Data after filtering for trading hours: {len(data)} rows")

# Modified function to check reversals by time of day
def check_reversal_by_time_of_day(df, begin_month_days=5, end_month_days=5):
    reversal_count_by_time = {}
    success_count_by_time = {}

    for day, day_data in df.groupby(df.index.date):  # Group by trading day
        day_of_week = day_data.index[0].dayofweek  # Get the day of the week (0 = Monday, 4 = Friday)

        day_data = day_data.between_time('09:15', '15:30')

        is_beginning_of_month = day_data.index[0].day <= begin_month_days
        is_end_of_month = day_data.index[0].day >= (day_data.index[-1].daysinmonth - end_month_days)

        for start_time in day_data.index:
            window_15min = day_data.loc[start_time:start_time + pd.Timedelta('15 minutes')]

            if len(window_15min) < 15:
                continue

            first_12min = window_15min.iloc[:12]
            if all(first_12min['Close'] < first_12min['Open']):
                price_12th = first_12min.iloc[-1]['Close']
                low_15min = window_15min['Low'].min()
                if price_12th <= low_15min * 1.05:
                    last_4min = window_15min.iloc[12:16]

                    if len(last_4min) == 4 and last_4min['Close'].iloc[-1] > last_4min['Open'].iloc[0]:
                        time_block = f"{start_time.time().strftime('%H:%M')}-{(start_time + pd.Timedelta('15 minutes')).time().strftime('%H:%M')}"
                        day_block = f"{day_of_week}-{time_block}"

                        # Ensure counts are accumulating correctly
                        reversal_count_by_time[day_block] = reversal_count_by_time.get(day_block, 0) + 1
                        success_count_by_time[day_block] = success_count_by_time.get(day_block, 0)

                        next_window = day_data.loc[start_time + pd.Timedelta('15 minutes'): start_time + pd.Timedelta('30 minutes')]
                        if not next_window.empty and next_window['Close'].iloc[-1] > window_15min['Close'].iloc[-1]:
                            success_count_by_time[day_block] += 1

    success_rate_by_time = {
        day_block: (success_count_by_time[day_block] / reversal_count_by_time[day_block]) if reversal_count_by_time[day_block] > 0 else 0
        for day_block in reversal_count_by_time
    }

    return success_rate_by_time, reversal_count_by_time, success_count_by_time

# Run the reversal analysis
success_rate_by_time, reversal_count_by_time, success_count_by_time = check_reversal_by_time_of_day(data, begin_month_days=5, end_month_days=5)

# Convert results to DataFrame for easier plotting
reversal_df = pd.DataFrame({
    'Day-Block': list(reversal_count_by_time.keys()),
    'Reversals': list(reversal_count_by_time.values()),
    'Successes': list(success_count_by_time.values()),
    'Success Rate (%)': [rate * 100 for rate in success_rate_by_time.values()]
})

# Ensure 'Day-Block' splits correctly into 'Day of Week' and 'Time Block'
reversal_df[['Day of Week', 'Time Block']] = reversal_df['Day-Block'].str.split('-', n=1, expand=True)

# Map day numbers to actual day names
reversal_df['Day of Week'] = reversal_df['Day of Week'].map({
    '0': 'Monday', '1': 'Tuesday', '2': 'Wednesday', '3': 'Thursday', '4': 'Friday'
})

# Ensure Time Block categories are unique and sorted
unique_time_blocks = sorted(reversal_df['Time Block'].unique())

# Assign 'Time Block' as a categorical variable with ordered time blocks
reversal_df['Time Block'] = pd.Categorical(reversal_df['Time Block'], categories=unique_time_blocks, ordered=True)

# Sort the DataFrame by 'Day of Week' and 'Time Block'
reversal_df = reversal_df.sort_values(['Day of Week', 'Time Block'])

# Check for any inconsistencies
print(reversal_df.groupby('Day of Week')['Reversals'].sum())

# Plotting Success Rate by Day of Week and Time Block
plt.figure(figsize=(16, 8))
sns.barplot(x='Time Block', y='Success Rate (%)', hue='Day of Week', data=reversal_df, palette='coolwarm')

plt.title('Reversal Success Rate by Day of Week and 15-Minute Time Block', fontsize=14)
plt.xticks(rotation=90)
plt.xlabel('Time Block')
plt.ylabel('Success Rate (%)')
plt.legend(title='Day of Week', loc='upper left')
plt.tight_layout()
plt.show()

# Plotting Total Reversals by Day of Week and Time Block
plt.figure(figsize=(16, 8))
sns.lineplot(x='Time Block', y='Reversals', hue='Day of Week', data=reversal_df, marker='o', palette='viridis')

plt.title('Total Reversals Detected by Day of Week and 15-Minute Time Block', fontsize=14)
plt.xticks(rotation=90)
plt.xlabel('Time Block')
plt.ylabel('Number of Reversals')
plt.legend(title='Day of Week', loc='upper left')
plt.tight_layout()
plt.show()
