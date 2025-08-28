import pandas as pd
from matplotlib import pyplot as plt
#df = pd.read_csv('TickData.csv', sep=',')
# Reading the data
data = pd.read_csv('TickData.csv', names=['Date_Time', 'LTP','LTQ'])
print(data.head())
data['Date_Time'] = pd.to_datetime(data['Date_Time']*1000*1000)
print(data.head())
data.set_index('Date_Time', inplace=True)
print(data.head())
# Convert the index to datetime
data.index = pd.to_datetime(data.index, format='%Y-%m-%d %H:%M:%S:%f')

# Print the last 5 rows
data.head()
data.tail()
#df = series[1]
# Resample LTP column to 15 mins bars using resample function from pandas
resample_LTP = data['LTP'].resample('10s').ohlc().ffill().bfill()
print("NEW ")
print(resample_LTP)
resample_LTQ = data['LTQ'].resample('10s').sum()
print("NEW vol")
print(resample_LTQ)


# Concatenate resampled data
resample_data = pd.concat([resample_LTP, resample_LTQ], axis=1,)

# Print the last 5 rows
print(resample_data.head())

# # import the mplfinance library
# import mplfinance as mpf
#
# # import the pandas package
# import pandas as pd
#
# # use read_csv function to read the dataset
# # data = pd.read_csv(r"C:\Users\Downloads\TATAMOTORS.csv",
# #                    parse_dates=True, index_col=1)
# # set the index column as date
# resample_data.index.name = 'Date_Time'
#
# # use the plot function of mpl finance,
# # and mention the type as candle to
# # get ohlc chart
# mpf.plot(resample_data, type='candle')
#

# import plotly graph objects
import plotly.graph_objects as go

# import python pandas package
import pandas as pd

# read the stock price dataset
# use go.OHLC function and pass the date, open,
# high, low and close price of the function
fig = go.Figure(data=go.Ohlc(x=resample_data.index,
                             open=resample_data['open'],
                             high=resample_data['high'],
                             low=resample_data['low'],
                             close=resample_data['close']))

# show the figure
fig.show()