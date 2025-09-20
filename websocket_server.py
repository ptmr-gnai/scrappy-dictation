#!/usr/bin/env python3
"""
WebSocket Dictation Server
Manages communication between Python controller and persistent Chrome tab
"""

import asyncio
import websockets
import json
import threading
import time
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote
import os


class RestrictedHTTPHandler(BaseHTTPRequestHandler):
    """Secure HTTP handler that only serves the speech-persistent.html file"""

    def do_GET(self):
        """Handle GET requests with file access restrictions"""
        # Normalize the path to prevent directory traversal
        path = unquote(self.path).strip('/')

        # Only allow access to the speech HTML file or root
        if path == '' or path == 'speech-persistent.html':
            try:
                # Serve the speech-persistent.html file
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'speech-persistent.html')

                with open(file_path, 'rb') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'no-cache')
                # Security headers
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('X-Frame-Options', 'DENY')
                self.send_header('Referrer-Policy', 'no-referrer')
                self.end_headers()

                self.wfile.write(content)

            except FileNotFoundError:
                self.send_error(404, "Speech recognition page not found")

        else:
            # Reject all other file requests
            self.send_error(404, "File not found")

    def log_message(self, format, *args):
        """Override to reduce log noise - only log security-relevant events"""
        if '404' in str(args):
            print(f"🚫 HTTP 404: Blocked access to {args[0]} from {self.client_address[0]}")


class DictationWebSocketServer:
    def __init__(self, ws_port=8081, http_port=8080):
        self.ws_port = ws_port
        self.http_port = http_port
        self.connected_clients = set()
        self.controller = None
        self.http_server = None
        self.http_thread = None

        # Generate session token for authentication
        self.session_token = secrets.token_urlsafe(32)
        print(f"🔐 Generated session token: {self.session_token[:8]}...")
        print(f"🔑 Full token for Chrome tab: {self.session_token}")

    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connections with authentication"""
        print(f"🔌 Connection attempt from {websocket.remote_address}")

        try:
            # First message must be authentication
            auth_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            auth_data = json.loads(auth_message)

            if auth_data.get('type') != 'AUTH' or auth_data.get('token') != self.session_token:
                await websocket.send(json.dumps({
                    'type': 'AUTH_FAILED',
                    'message': 'Invalid authentication token'
                }))
                await websocket.close()
                print(f"🚫 Authentication failed for {websocket.remote_address}")
                return

            await websocket.send(json.dumps({'type': 'AUTH_SUCCESS'}))
            print(f"🔐 Authenticated connection from {websocket.remote_address}")

        except (asyncio.TimeoutExpired, json.JSONDecodeError, KeyError):
            print(f"🚫 Authentication timeout/error for {websocket.remote_address}")
            await websocket.close()
            return

        # Authentication successful - add to connected clients
        self.connected_clients.add(websocket)

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data, websocket)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed:
            print("🔌 Authenticated client disconnected")
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def handle_message(self, data, websocket):
        """Process messages from Chrome tab"""
        msg_type = data.get('type')
        print(f"📨 Received: {msg_type}")

        if msg_type == 'READY':
            print("✅ Speech tab is ready for commands")
            await websocket.send(json.dumps({
                'type': 'ACKNOWLEDGE',
                'message': 'Controller connected'
            }))

        elif msg_type == 'TRANSCRIPT_READY':
            transcript = data.get('text', '').strip()
            if transcript:
                print(f"📝 Transcript received: '{transcript}'")

                # Pass to controller if available
                if self.controller:
                    # Run in thread since controller methods might be sync
                    threading.Thread(
                        target=self.controller.handle_transcript,
                        args=(transcript,),
                        daemon=True
                    ).start()

        elif msg_type == 'SPEECH_STARTED':
            print("🎙️  Speech recognition started")

        elif msg_type == 'SPEECH_ENDED':
            print("⏹️  Speech recognition ended")

        elif msg_type == 'SPEECH_ERROR':
            error = data.get('error', 'Unknown error')
            print(f"❌ Speech error: {error}")

        elif msg_type == 'PONG':
            print("🏓 Pong received from speech tab")

    async def send_command(self, command_type, **kwargs):
        """Send command to all connected Chrome tabs"""
        if not self.connected_clients:
            print("❌ No speech tabs connected")
            return False

        message = json.dumps({
            'type': command_type,
            'timestamp': time.time(),
            **kwargs
        })

        print(f"📤 Sending command: {command_type}")

        # Send to all connected tabs
        disconnected = set()
        sent_count = 0

        for client in self.connected_clients.copy():
            try:
                await client.send(message)
                sent_count += 1
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                print(f"❌ Error sending to client: {e}")
                disconnected.add(client)

        # Clean up disconnected clients
        self.connected_clients -= disconnected

        if sent_count > 0:
            print(f"✅ Command sent to {sent_count} tab(s)")
        else:
            print("❌ Failed to send command to any tabs")

        return sent_count > 0

    async def ping_tabs(self):
        """Ping all connected tabs to check connectivity"""
        return await self.send_command('PING')

    def start_http_server(self):
        """Start secure HTTP server with restricted file access"""
        try:
            # Bind to 127.0.0.1 instead of localhost for better security
            server_address = ('127.0.0.1', self.http_port)
            self.http_server = HTTPServer(server_address, RestrictedHTTPHandler)
            print(f"🔒 Secure HTTP server running on http://127.0.0.1:{self.http_port}")
            print(f"🛡️  File access restricted to speech-persistent.html only")
            self.http_server.serve_forever()
        except Exception as e:
            print(f"❌ HTTP server error: {e}")

    def start_servers(self):
        """Start both HTTP and WebSocket servers"""
        print("🚀 Starting WebSocket dictation servers...")

        # Start HTTP server in background thread
        self.http_thread = threading.Thread(
            target=self.start_http_server,
            daemon=True
        )
        self.http_thread.start()

        # Return WebSocket server coroutine - fix the handler signature
        return websockets.serve(
            self.handle_websocket,
            "localhost",
            self.ws_port
        )

    def stop_servers(self):
        """Stop both servers"""
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
            print("🛑 HTTP server stopped")

    def is_connected(self):
        """Check if any Chrome tabs are connected"""
        return len(self.connected_clients) > 0

    def get_connection_count(self):
        """Get number of connected Chrome tabs"""
        return len(self.connected_clients)


if __name__ == "__main__":
    """Test the WebSocket server standalone"""

    async def test_server():
        server = DictationWebSocketServer()

        # Start servers
        websocket_server = await server.start_servers()

        print("🎤 WebSocket server running for testing")
        print(f"   📱 Open: http://localhost:{server.http_port}/speech-persistent.html")
        print("   💬 WebSocket URL: ws://localhost:{server.ws_port}")
        print("   ⌨️  Press Ctrl+C to stop")

        try:
            # Keep server running
            await websocket_server.wait_closed()
        except KeyboardInterrupt:
            print("\n👋 Shutting down test server...")
        finally:
            server.stop_servers()

    # Run test server
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Server error: {e}")