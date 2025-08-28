import pandas as pd
import numpy as np
import backtrader as bt
from sklearn.linear_model import LinearRegression
from tvDatafeed import TvDatafeed,Interval
from datetime import time

# ---------------------
# STEP 1: Load & Prepare Data
# ---------------------

# df = pd.read_csv("your_5min_data.csv", parse_dates=['Datetime'], index_col='Datetime')
tv = TvDatafeed()
nifty_data=tv.get_hist('TIMKEN','NSE',interval=Interval.in_5_minute,n_bars=1500)

df=nifty_data.copy()
# df=df.tail(900)
df = df.rename(columns={'open':'Open','high': 'High','low': 'Low','close': 'Close','volume': 'Volume'})
df['Datetime']=df.index
df.set_index('Datetime', inplace=True)
# Normalize with rolling window
# Parameters
window = 20
future_horizon = 5  # Predict 6 bars ahead

# Normalize
def normalize(series, window):
    min_val = series.rolling(window).min()
    max_val = series.rolling(window).max()
    return (series - min_val) / (max_val - min_val + 1e-6)


# Step 1: Calculate future close
df['Future_Close'] = df['Close'].shift(-future_horizon)

# Step 2: Normalize features and target
for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
    df[f'{col}_norm'] = normalize(df[col], window)

# Now normalize target
df['Future_Close_norm'] = normalize(df['Future_Close'], window)

# Step 3: Drop NaNs after all rolling + shifting
df.dropna(inplace=True)

# Step 4: Train
X = df[['Open_norm', 'High_norm', 'Low_norm', 'Volume_norm']].values
y = df['Future_Close_norm'].values


# model = LinearRegression()
# model.fit(X, y)
# df['Predicted_Future_Close_norm'] = model.predict(X)



############################################3
#######################
# Train model on training data
w = np.random.rand(X.shape[1])
b = 0
lr = 0.01
epochs = 1000

for _ in range(epochs):
    y_pred_train = X @ w + b
    error = y_pred_train - y
    dw = X.T @ error / len(X)
    db = np.sum(error) / len(X)
    w -= lr * dw
    b -= lr * db

# Predict on both sets
df['Predicted_Future_Close_norm'] = X @ w + b

y_pred_norm = df['Predicted_Future_Close_norm'] 


##############################################################33
###############################################3


# Denormalize predictions
close_min = df['Close'].rolling(window).min()
close_max = df['Close'].rolling(window).max()
df['Predicted_Future_Close'] = df['Predicted_Future_Close_norm'] * (close_max - close_min + 1e-6) + close_min

# ATR
df['H-L'] = df['High'] - df['Low']
df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
df['ATR'] = df['TR'].rolling(window=14).mean()

# Expected return & signal
df['Expected_Return'] = df['Predicted_Future_Close'] - df['Close']
df['Strong_Signal'] = df['Expected_Return'] > 1 * df['ATR']
df.dropna(inplace=True)

# Backtrader integration
class PandasDataWithPrediction(bt.feeds.PandasData):
    lines = ('Predicted_Future_Close', 'ATR', 'Strong_Signal',)
    params = (('Predicted_Future_Close', -1), ('ATR', -1), ('Strong_Signal', -1),)

class ATRFilteredStrategy(bt.Strategy):
    def __init__(self):
        self.pred = self.datas[0].Predicted_Future_Close
        self.signal = self.datas[0].Strong_Signal

    def next(self):
        current_time = self.datas[0].datetime.time(0)
        if current_time >= time(9, 20):
            if current_time >= time(15, 10):
                if self.position:
                    self.close()
                    print(f"[{self.datas[0].datetime.datetime(0)}] 🕒 EOD SELL @ {self.data.close[0]:.2f}")
                

            if not self.position and self.signal[0] and current_time < time(15, 00):
                size = self.broker.getcash() // self.data.close[0]
                self.buy(size=size)
                print(f"[{self.datas[0].datetime.datetime(0)}] ✅ BUY @ {self.data.close[0]:.2f}")
            elif self.position and self.pred[0] < self.data.close[0] :
                self.close()
                print(f"[{self.datas[0].datetime.datetime(0)}] ❌ SELL @ {self.data.close[0]:.2f}")

# Run backtest
cerebro = bt.Cerebro()
data = PandasDataWithPrediction(dataname=df)
cerebro.adddata(data)
cerebro.addstrategy(ATRFilteredStrategy)
cerebro.broker.set_cash(100000)
# cerebro.broker.setcommission(commission=0.001)
print(f"Starting Portfolio Value: ₹{cerebro.broker.getvalue():.2f}")
cerebro.run()
print(f"Final Portfolio Value: ₹{cerebro.broker.getvalue():.2f}")

 
# # ---------------------
# # STEP 3: Backtrader Strategy
# # ---------------------

# class PandasDataWithPrediction(bt.feeds.PandasData):
#     lines = ('Predicted_Close',)
#     params = (('Predicted_Close', -1),)

# class ModelStrategy(bt.Strategy):
#     def __init__(self):
#         self.predicted = self.datas[0].Predicted_Close
#         self.in_position = False
#         self.buy_price = None
#         self.size = 0
#         self.stop_loss_pct = 0.02

#     def next(self):
        
#         current_time = self.datas[0].datetime.time(0)

#         # Intraday exit logic at 3:10 PM
#         if current_time == time(15, 10):
#             if self.position:
#                 self.close(size=self.size)  # close any open position
#                 # self.in_position = False
#                 print(f"[{self.datas[0].datetime.datetime(0)}] 💼 EOD SELL @ {self.data.close[0]:.2f}")
#             return  # Skip new trades at EOD
    
#         if not self.position:
#             if self.predicted[0] > self.data.close[0]:
#                 self.size = self.broker.getcash() // self.data.close[0]
#                 self.buy_price = self.data.close[0]
#                 self.buy(size=self.size)
#                 self.in_position = True
#                 print(f"BUY @ {self.data.close[0]:.2f}")
#         else:
#             # Sell if predicted is below actual OR hit stop loss
#             if (self.predicted[0] < self.data.close[0] or self.data.close[0] <= self.buy_price * (1 - self.stop_loss_pct) )and  self.position:
#                 self.sell(size=self.size)
#                 self.in_position = False
#                 print(f"SELL @ {self.data.close[0]:.2f}")



# rolling_window =window
# future_return_horizon = 10
# volatility_window = 20
# volume_threshold = 2000

# df['volAvg'] = df['Volume'].rolling(60).mean()
# # Calculate prediction delta and rolling percentile
# df['Pred_Delta'] = df['Predicted_Close'] - df['Close']
# df['Delta_Percentile'] = df['Pred_Delta'].rolling(rolling_window).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])

# # Future return labeling
# df['Future_Close'] = df['Close'].shift(-future_return_horizon)
# df['Future_Return'] = (df['Future_Close'] - df['Close']) / df['Close']

# # Volatility filter
# df['Volatility'] = df['Close'].rolling(volatility_window).std()

# # Filter for top 30% predicted deltas with liquidity and volatility thresholds
# df_filtered = df[
#     (df['Delta_Percentile'] >= 0.7) &
#     (df['Volume'] > df['volAvg']*1.2 ) &
#     (df['Volatility'] > df['Volatility'].median() * 1.5)
# ].copy()

# df_filtered.dropna(subset=['Future_Return'], inplace=True)


# # ---------------------
# # STEP 4: Run Backtest
# # ---------------------

# data = PandasDataWithPrediction(dataname=df)

# cerebro = bt.Cerebro()
# cerebro.addstrategy(ModelStrategy)
# cerebro.adddata(data)
# cerebro.broker.set_cash(100000)
# # cerebro.broker.set_commission(commission=0.001)
# # cerebro.broker.set_slippage_perc(0.001)

# print(f"Starting Portfolio Value: ₹{cerebro.broker.getvalue():,.2f}")
# cerebro.run()
# print(f"Ending Portfolio Value: ₹{cerebro.broker.getvalue():,.2f}")

# Optional: Plot
cerebro.plot(style='candlestick')
