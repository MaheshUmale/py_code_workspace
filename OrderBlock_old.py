import numpy as np
import pandas as pd
import websocket
import json
import mplfinance as mpf
from datetime import datetime

class OrderBlockDetector:
    def __init__(self, sensitivity=28, mitigation_type='Close'):
        self.sensitivity = sensitivity / 100
        self.mitigation_type = mitigation_type
        self.order_blocks = {
            'bullish': [],
            'bearish': []
        }

    def calculate_roc(self, open_prices):
        return (open_prices - np.roll(open_prices, 4)) / np.roll(open_prices, 4) * 100

    def detect_order_blocks(self, open_prices, close_prices, high_prices, low_prices):
        pc = self.calculate_roc(open_prices)
        bullish_blocks, bearish_blocks = [], []
        
        for i in range(4, len(pc)):
            if pc[i] > self.sensitivity:
                bearish_blocks.append(i)
            elif pc[i] < -self.sensitivity:
                bullish_blocks.append(i)
        
        self.order_blocks['bullish'] = self.create_blocks(bullish_blocks, open_prices, close_prices, high_prices, low_prices, 'bullish')
        self.order_blocks['bearish'] = self.create_blocks(bearish_blocks, open_prices, close_prices, high_prices, low_prices, 'bearish')
        
    def create_blocks(self, indices, open_prices, close_prices, high_prices, low_prices, block_type):
        blocks = []
        for idx in indices:
            if block_type == 'bullish':
                last_red_idx = self.find_last_red_candle(idx, open_prices, close_prices)
                if last_red_idx is not None:
                    block = {
                        'left': last_red_idx,
                        'right': idx,
                        'top': high_prices[last_red_idx],
                        'bottom': low_prices[last_red_idx]
                    }
                    blocks.append(block)
            elif block_type == 'bearish':
                last_green_idx = self.find_last_green_candle(idx, open_prices, close_prices)
                if last_green_idx is not None:
                    block = {
                        'left': last_green_idx,
                        'right': idx,
                        'top': high_prices[last_green_idx],
                        'bottom': low_prices[last_green_idx]
                    }
                    blocks.append(block)
        return blocks

    def find_last_red_candle(self, idx, open_prices, close_prices):
        for i in range(idx-1, max(idx-15, -1), -1):
            if close_prices[i] < open_prices[i]:
                return i
        return None

    def find_last_green_candle(self, idx, open_prices, close_prices):
        for i in range(idx-1, max(idx-15, -1), -1):
            if close_prices[i] > open_prices[i]:
                return i
        return None

    def check_mitigation(self, close_prices, high_prices, low_prices):
        mitigated_bullish, mitigated_bearish = [], []
        for block in self.order_blocks['bullish']:
            if self.mitigation_type == 'Close' and close_prices[-1] < block['bottom']:
                mitigated_bullish.append(block)
            elif self.mitigation_type == 'Wick' and low_prices[-1] < block['bottom']:
                mitigated_bullish.append(block)
        
        for block in self.order_blocks['bearish']:
            if self.mitigation_type == 'Close' and close_prices[-1] > block['top']:
                mitigated_bearish.append(block)
            elif self.mitigation_type == 'Wick' and high_prices[-1] > block['top']:
                mitigated_bearish.append(block)
        
        return mitigated_bullish, mitigated_bearish

def on_message(ws, message):
    print('On msg')
    global df
    data = json.loads(message)
    candle = data['k']
    timestamp = candle['t'] // 1000
    date_time = datetime.fromtimestamp(timestamp)
    
    df = df.append({
        'Date': date_time,
        'Open': float(candle['o']),
        'High': float(candle['h']),
        'Low': float(candle['l']),
        'Close': float(candle['c']),
        'Volume': float(candle['v'])
    }, ignore_index=True)
    
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    
    # Update the OrderBlockDetector
    detector.detect_order_blocks(df['Open'].values, df['Close'].values, df['High'].values, df['Low'].values)
    mitigated_bullish, mitigated_bearish = detector.check_mitigation(df['Close'].values, df['High'].values, df['Low'].values)
    
    plot_chart(df, detector)

def plot_chart(df, detector):
    ap = []
    
    # Plot Bullish Order Blocks
    for block in detector.order_blocks['bullish']:
        ap.append(mpf.make_addplot(
            [block['top'], block['top']], 
            panel=0, 
            color='green', 
            linestyle='--'))
        ap.append(mpf.make_addplot(
            [block['bottom'], block['bottom']], 
            panel=0, 
            color='green', 
            linestyle='--'))
    
    # Plot Bearish Order Blocks
    for block in detector.order_blocks['bearish']:
        ap.append(mpf.make_addplot(
            [block['top'], block['top']], 
            panel=0, 
            color='red', 
            linestyle='--'))
        ap.append(mpf.make_addplot(
            [block['bottom'], block['bottom']], 
            panel=0, 
            color='red', 
            linestyle='--'))
    
    mpf.plot(df, type='candle', addplot=ap, style='charles')
    

def on_open(ws):
    print("WebSocket opened")

def on_close(ws):
    print("WebSocket closed")

if __name__ == "__main__":
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    detector = OrderBlockDetector(sensitivity=28, mitigation_type='Close')
    
    ws = websocket.WebSocketApp(
        "ws://localhost:8765",
        on_open=on_open,
        on_message=on_message,
        on_close=on_close
    )
    
    ws.run_forever()
