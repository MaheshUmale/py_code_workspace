import pandas as pd
import mplfinance as mpf
import datetime
import pytz
# Read the CSV file without header
dfcsv  = pd.read_csv("upstox_WSS_output_2024_07_31_03_46_10_OP.csv")
#dfcsv.columns = ["symbol","ltt","ltp","ltq"]
print(dfcsv.head())
df  = dfcsv[dfcsv['symbol'].str.contains('35415')]  #35415  35165
#df = df.tail(2000)
print(df.head())
# Add column names
df = df.drop(columns=['symbol'])
print(df.head())
df.columns = ["timestamp", "close", "volume"]  # Replace with your desired column names
#df.rename(columns={'LTQ': 'volume'}, inplace=True)
#df['timestamp']= *1000000)
# Create a datetime object from the timestamp
df['timestamp'] = pd.to_datetime(df['timestamp']+19800000, unit='ms', utc=True).dt.tz_convert('Asia/Kolkata')
#df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
    #datetime.datetime.fromtimestamp(pd.to_datetime(df['timestamp']), tz=pytz.timezone('Asia/Kolkata')).astimezone(pytz.utc).timestamp())

#df.set_index(df['timestamp'], inplace=True)
print(df.head())

df = df.set_index('timestamp')
#index column to df.index
#convert to DatetimeIndex
#df.index = pd.to_datetime(df.index, unit='ns').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
print(df)
from renkodf import Renko, RenkoWS

r = Renko(df, brick_size=4)
dfRenko = r.renko_df('wicks') # 'wicks' = default
dfRenko.head(3)
print(dfRenko.tail(3))
import mplfinance as mpf
df_wicks = r.renko_df('wicks')
df_nongap = r.renko_df('nongap')

df_wicks.to_csv('BNF_TICK_RENKO.csv')
#
# mpf.plot(dfRenko, type='candle', volume=True, style="charles",
#          title=f"renko: normal\nbrick size: 5")
# mpf.show()

df_GET = df

# API request
r = Renko(df_GET, brick_size=10)
ext_df = r.to_rws()  # Save this

# Load the file and chosen its Renko Mode
r = RenkoWS(external_df=ext_df, external_mode='wicks')
initial_df = r.initial_df
# if you need multiple dataframes of different modes as initial_df
# just add 's' to get this function:
# r.initial_dfs('normal')
# r.initial_dfs('nongap')
# etc...

fig, axes = mpf.plot(initial_df, returnfig=True, volume=True,
                    figsize=(15, 10), panel_ratios=(2, 1),
                    title='\nNIFTY', type='candle', style='charles',tz_localize=False)
ax1 = axes[0]
ax2 = axes[2]

mpf.plot(initial_df,type='candle', style='charles',ax=ax1,volume=ax2,axtitle='renko: wicks', tight_layout=True, datetime_format='%b %d, %H:%M:%S' ,tz_localize=False)
mpf.show()