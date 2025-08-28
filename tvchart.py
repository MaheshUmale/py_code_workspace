
import pandas as pd
from lightweight_charts import Chart,JupyterChart
from tvDatafeed import TvDatafeed,Interval


tv = TvDatafeed()
nifty_data=tv.get_hist('NIFTY','NSE',interval=Interval.in_1_minute,n_bars=100)

def calculate_sma(df, period: int = 50):
    return pd.DataFrame({
        'time': df.index,
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()

# if __name__ == '__main__':
    
#     # chart = Chart()
#     # line = chart.create_line(name='SMA 50')
    
#     # Columns: time','open','high','low','close','volume 
#     # df = pd.read_csv('niftyData.csv', usecols = ['datetime','open','high','low','close','volume' ], header=0 )
   


#     tv = TvDatafeed()
#     nifty_data=tv.get_hist('NIFTY','NSE',interval=Interval.in_1_minute,n_bars=100)
#     df = nifty_data.copy()
#     df.rename(columns={'datetime': 'time'}, inplace=True)
        
#     chart.set(df)
       
#     # sma_df = calculate_sma(df, period=50)
#     # line.set(sma_df)
#     chart.show(block=True)

#     # img = chart.screenshot()
#     # with open('screenshot.png', 'wb') as f:
#     #     f.write(img)
    

if __name__ == '__main__':
    chart = Chart(inner_width=0.5, inner_height=0.5)
    chart2 = chart.create_subchart(position='right', width=0.5, height=0.5)
    chart3 = chart.create_subchart(position='left', width=0.5, height=0.5)
    chart4 = chart.create_subchart(position='right', width=0.5, height=0.5, sync=True)

    chart.watermark('1')
    chart2.watermark('2')
    chart3.watermark('3')
    chart4.watermark('4')

    df = nifty_data#pd.read_csv('ohlcv.csv')
    chart.set(df)
    chart2.set(df)
    chart3.set(df)
    chart4.set(df)
    sma_df = calculate_sma(df, period=50)
    line = chart.create_line(name='SMA 50')
    line.set(sma_df)

    chart.show(block=True)
