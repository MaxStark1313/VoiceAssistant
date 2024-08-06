import asyncio
import websockets

async def send_message():
    async with websockets.connect('ws://localhost:8766') as websocket:
        await websocket.send('Hello from client!')
        response = await websocket.recv()
        print(f'Received response: {response}')

asyncio.run(send_message())