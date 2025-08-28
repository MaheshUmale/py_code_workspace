import asyncio
import websockets

async def receive_data():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

if __name__ == "__main__":
    asyncio.run(receive_data())
