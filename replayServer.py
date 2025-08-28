import asyncio
#import csv
import json
import pandas as pd
import websockets
#from datetime import datetime

async def replay_csv(websocket, path, csv_file='.//OutFiles//niftyData.csv') : #niftyData.csv'):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    print(df.head())
    # Ensure that the Date column is in datetime format
    if 'datetime' in df.columns:
        print(" datetime IN CSV")
        #df['timestamp'] = pd.to_datetime(df['datetime']).to_timestamp()
        # Assuming df is your DataFrame with a 'datetime' column  convert to ms
        #"%Y-%m-%d %H:%M:%S.%f%z"
        df['timestamp'] = pd.to_datetime(df['datetime']).view('int64') // 10 ** 6
        #df['timestamp'] = pd.to_datetime(df['datetime']).view('int64') // 10 ** 6
        #df['timestamp'] = int(round(pd.to_datetime(df['datetime'])))
        df.drop(['datetime'], axis=1)

    for index, row in df.iterrows():
        # Convert the row to JSON format
        data = row.to_dict()
        print(data)
        #data['Date'] = data['Date'].isoformat() if 'Date' in data else str(datetime.now())
        #dtimestamp = data['Date'].timestamp()
        print("Integer timestamp in milli seconds: ",(data['timestamp']))

        #milliseconds = int(round(data['timestamp'] * 1000))
        #data['timestamp']=milliseconds
        message = json.dumps(data)

        # Send the data to the WebSocket client
        await websocket.send(message)
        #print(f"Sent: {message}")

        # Wait for 1 second before sending the next row
        await asyncio.sleep(0.2)

async def main():
    async with websockets.serve(replay_csv, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
