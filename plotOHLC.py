import asyncio
import websockets
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Initialize an empty DataFrame to store OHLC data
ohlc_df = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])

# Function to handle incoming WebSocket messages
async def handle_message(message):
    global ohlc_df
    data = json.loads(message)
    if 'k' in data:
        kline = data['k']
        ohlc_data = {
            'Time': datetime.fromtimestamp(kline['t'] / 1000),
            'Open': float(kline['o']),
            'High': float(kline['h']),
            'Low': float(kline['l']),
            'Close': float(kline['c']),
            'Volume': float(kline['v'])
        }
        new_row = pd.DataFrame([ohlc_data])
        ohlc_df = pd.concat([ohlc_df, new_row], ignore_index=True)
        # Keep only the last 100 data points for better visualization
        if len(ohlc_df) > 100:
            ohlc_df = ohlc_df.tail(100)

# Function to connect to WebSocket and receive messages
async def connect_to_websocket():
    url = "ws://localhost:8765  "
    async with websockets.connect(url) as websocket:
        while True:
            message = await websocket.recv()
            await handle_message(message)

# Function to update the plot
def update_plot(frame):
    plt.clf()
    plt.plot(ohlc_df['Time'], ohlc_df['Close'], label='Close')
    plt.title('Real-Time OHLC Data')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)

# Function to start the event loop and plotting
async def main():
    # Set up the plot
    fig, ax = plt.subplots()
    ani = FuncAnimation(fig, update_plot, interval=1000, cache_frame_data=False)

    # Create a task for the WebSocket connection
    websocket_task = asyncio.create_task(connect_to_websocket())

    # Show the plot in a non-blocking way
    plt.show(block=False)

    # Run the WebSocket connection task
    await websocket_task

# Entry point of the script
if __name__ == "__main__":
    asyncio.run(main())
