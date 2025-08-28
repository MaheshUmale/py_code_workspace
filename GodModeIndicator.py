import websocket
import json
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Global variables to store the incoming data
ohlcv_data = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
data_lock = False


# Functions to calculate indicators (from previous response)
def ttsi(_src, _len0, _len1):
    pc = np.diff(_src) / pd.Series(_src).rolling(window=2).mean().shift(1)
    ma0 = pc.ewm(span=_len0).mean()
    ma1 = ma0.ewm(span=_len1).mean()
    apc = np.abs(np.diff(_src))
    ma2 = pd.Series(apc).ewm(span=_len0).mean()
    ma3 = ma2.ewm(span=_len1).mean()
    ttsi = 100 * (ma1 / ma3)
    return ttsi


def tci(_src, len0, len1):
    ema_src = _src.ewm(span=len0).mean()
    tci = (_src - ema_src) / (0.025 * _src.sub(ema_src).abs().ewm(span=len0).mean())
    return tci.ewm(span=len1).mean() + 50


def mf(_src, A, len2):
    gain = A * np.where(_src.diff() <= 0, 0, _src)
    loss = A * np.where(_src.diff() >= 0, 0, _src)
    mf = 100 - 100 / (1 + pd.Series(gain).rolling(window=len2).sum() / pd.Series(loss).rolling(window=len2).sum())
    return mf


def willy(_src, len1):
    highest_high = _src.rolling(window=len1).max()
    lowest_low = _src.rolling(window=len1).min()
    willy = 60 * (_src - highest_high) / (highest_high - lowest_low) + 80
    return willy


def csi(_src, len2, len0, len1):
    rsi = pd.Series(_src).rolling(window=len2).apply(lambda x: np.mean(x))
    ttsi_val = ttsi(_src, len0, len1) * 50 + 50
    csi = (rsi + ttsi_val) / 2
    return csi


def godmode(_src, A, len0, len1, len2):
    tci_val = tci(_src, len0, len1)
    csi_val = csi(_src, len2, len0, len1)
    mf_val = mf(_src, A, len2)
    willy_val = willy(_src, len1)
    godmode_val = (tci_val + csi_val + mf_val + willy_val) / 4
    return godmode_val


def tradition(_src, A, len0, len1, len2):
    tci_val = tci(_src, len0, len1)
    mf_val = mf(_src, A, len2)
    rsi_val = pd.Series(_src).rolling(window=len2).apply(lambda x: np.mean(x))
    tradition_val = (tci_val + mf_val + rsi_val) / 3
    return tradition_val


def calc(src0, len0, len1, len2, cou0, smo0, high, low, volume):
    src1 = src0
    h = high
    l = low

    godmode_1 = godmode(src1, volume, len0, len1, len2)
    tradition_1 = tradition(src1, volume, len0, len1, len2)
    wt0 = godmode_1
    swt0 = wt0.rolling(window=len0).mean()

    gm = swt0 if smo0 else wt0

    gr = 0
    incrementer_up = gm > 70
    gr = (gr.shift(1).fillna(0) + 1) * incrementer_up if incrementer_up.any() else 0

    grH = h if gr >= cou0 else np.nan
    grL = l if gr >= cou0 else np.nan
    grh = grH.ffill().bfill()
    grl = grL.ffill().bfill()

    gs = 0
    incrementer_down = gm < 30
    gs = (gs.shift(1).fillna(0) + 1) * incrementer_down if incrementer_down.any() else 0

    gsH = h if gs >= cou0 else np.nan
    gsL = l if gs >= cou0 else np.nan
    gsh = gsH.ffill().bfill()
    gsl = gsL.ffill().bfill()

    gsdx = 0
    incrementer_both = (gm > 70) | (gm < 30)
    gsdx = (gsdx.shift(1).fillna(0) + 1) * incrementer_both if incrementer_both.any() else 0

    gsdH = h if gsdx >= cou0 else np.nan
    gsdL = l if gsdx >= cou0 else np.nan
    gsdh = gsdH.ffill().bfill()
    gsdl = gsdL.ffill().bfill()

    return gsh, gsl, grh, grl, gsdh, gsdl


# Websocket callback functions
def on_message(ws, message):
    global ohlcv_data, data_lock
    data = json.loads(message)
    new_row = {
        'timestamp': data['datetime'],
        'open': data['open'],
        'high': data['high'],
        'low': data['low'],
        'close': data['close'],
        'volume': data['volume']
    }
    if not data_lock:
        data_lock = True
        ohlcv_data = pd.concat([ohlcv_data, pd.DataFrame([new_row])], ignore_index=True)

        #ohlcv_data = ohlcv_data._append(new_row, ignore_index=True)
        data_lock = False


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    print("### opened ###")


# Plotting setup
fig, ax = plt.subplots()
plt.ion()
len0, len1, len2, cou0, smo0 = 9, 26, 13, 5, False


def update_plot(frame):
    global ohlcv_data, data_lock
    if not data_lock and not ohlcv_data.empty:
        data_lock = True
        ax.clear()  # Clear previous plots

        mpf.plot(ohlcv_data, type='candle', ax=ax)

        calc_results = calc(
            ohlcv_data['close'], len0, len1, len2, cou0, smo0,
            ohlcv_data['high'], ohlcv_data['low'], ohlcv_data['volume']
        )

        gsh, gsl, grh, grl, gsdh, gsdl = calc_results

        ax.plot(ohlcv_data['timestamp'], gsh, label='GSH', color='green')
        ax.plot(ohlcv_data['timestamp'], gsl, label='GSL', color='red')
        ax.plot(ohlcv_data['timestamp'], grh, label='GRH', color='blue')
        ax.plot(ohlcv_data['timestamp'], grl, label='GRL', color='orange')
        ax.plot(ohlcv_data['timestamp'], gsdh, label='GSDH', color='purple')
        ax.plot(ohlcv_data['timestamp'], gsdl, label='GSDL', color='brown')

        ax.legend()
        data_lock = False
    plt.draw()


# Run websocket and plot
if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "ws://localhost:8765",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ani = FuncAnimation(fig, update_plot, interval=1000)
    plt.show()

    ws.run_forever()
