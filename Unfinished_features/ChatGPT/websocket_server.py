import asyncio
import websockets

async def handler(websocket, path):
    print(f"Client connected: {path}")
    async for message in websocket:
        print(f"Received message: {message}")
        response = f"Response to: {message}"
        await websocket.send(response)

start_server = websockets.serve(handler, "localhost", 8766)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()