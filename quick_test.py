#!/usr/bin/env python3
"""
Quick test to verify the WebSocket issue and provide working version
"""

import asyncio
import websockets
import json

async def handle_websocket(websocket, path):
    print(f"🔌 Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"📨 Received: {data}")

            # Echo back
            await websocket.send(json.dumps({"type": "ECHO", "data": data}))
    except websockets.exceptions.ConnectionClosed:
        print("🔌 Client disconnected")

async def main():
    print("🧪 Testing WebSocket server...")
    server = await websockets.serve(handle_websocket, "localhost", 8082)
    print("✅ WebSocket test server running on ws://localhost:8082")
    print("🌐 Open: http://localhost:8080/speech-persistent.html")
    print("📝 Change WebSocket URL to: ws://localhost:8082")

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())