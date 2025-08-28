import asyncio
import websockets
import json
import pandas as pd
import numpy as np

import dash
import dash as dcc
#import dash_html_components as html
from dash import html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__)

# Data container for live updates
live_data = pd.DataFrame(columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])

len0, len1, len2, cou0, smo0 = 9, 26, 13, 5, False
async def fetch_data():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            # Process the incoming message (assuming it's JSON)
            data = json.loads(message)
            global live_data
            new_row = {
                'datetime': data['datetime'],
                'open': data['open'],
                'high': data['high'],
                'low': data['low'],
                'close': data['close'],
                'volume': data['volume']
            }
            #live_data = live_data.append(new_row, ignore_index=True)
            live_data = pd.concat([live_data, pd.DataFrame([new_row])], ignore_index=True)
            live_data = live_data.tail(500)  # Limit the number of rows if necessary

# Run the WebSocket client
loop = asyncio.get_event_loop()
loop.run_until_complete(fetch_data())

app.layout = html.Div([
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # Update every 1 second
        n_intervals=0
    )
])

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


@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
# Functions to calculate indicators (from previous response)
def update_graph(n):
    global live_data
    if live_data.empty:
        return {
            'data': [],
            'layout': go.Layout(
                title='No Data Available',
                xaxis_title='Datetime',
                yaxis_title='Price'
            )
        }

    # Calculate indicators


    gsh, gsl, grh, grl, gsdh, gsdl = calc(live_data['close'], len0, len1, len2, cou0, smo0, live_data['high'], live_data['low'], live_data['volume'])

    trace_candlestick = go.Candlestick(
        x=live_data['datetime'],
        open=live_data['open'],
        high=live_data['high'],
        low=live_data['low'],
        close=live_data['close'],
        name='Candlestick'
    )

    trace_gsh = go.Scatter(
        x=live_data['datetime'],
        y=[gsh] * len(live_data),
        mode='lines',
        name='GSH'
    )

    trace_gsl = go.Scatter(
        x=live_data['datetime'],
        y=[gsl] * len(live_data),
        mode='lines',
        name='GSL'
    )

    # Add other indicators similarly...

    figure = {
        'data': [trace_candlestick, trace_gsh, trace_gsl],  # Add other indicators here
        'layout': go.Layout(
            title='Candlestick Chart with Indicators',
            xaxis_title='Datetime',
            yaxis_title='Price',
            xaxis=dict(
                tickformat='%Y-%m-%d %H:%M:%S'
            )
        )
    }

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
