#!/usr/bin/env python3
"""
WebSocket Dictation Controller - Fixed for websockets 15.x
Zero-manual-step dictation using persistent Chrome tab and WebSocket control
"""

import asyncio
import subprocess
import time
import threading
import pyperclip
import os
import signal
import sys
import json
import websockets
import secrets
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from urllib.parse import unquote
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode


class RestrictedHTTPHandler(BaseHTTPRequestHandler):
    """Secure HTTP handler that only serves the speech-persistent.html file"""

    def do_GET(self):
        """Handle GET requests with file access restrictions"""
        # Normalize the path to prevent directory traversal
        path = unquote(self.path).strip('/')

        # Only allow access to the speech HTML file or root
        if path == '' or path == 'speech-persistent.html' or path.startswith('speech-persistent.html?'):
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


class FixedDictationServer:
    def __init__(self, ws_port=8081, http_port=8080):
        self.ws_port = ws_port
        self.http_port = http_port
        self.connected_clients = set()
        self.controller = None
        self.http_server = None
        self.http_thread = None
        self.ping_task = None

        # Generate session token for authentication
        self.session_token = secrets.token_urlsafe(32)
        print(f"🔐 Generated session token: {self.session_token[:8]}...")
        print(f"🔑 Full token for Chrome tab: {self.session_token}")

    async def websocket_handler(self, websocket):
        """Handle WebSocket connections with authentication"""
        print(f"🔌 Connection attempt from {websocket.remote_address}")

        try:
            # First message must be authentication
            auth_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            auth_data = json.loads(auth_message)

            if auth_data.get('type') != 'AUTH' or auth_data.get('token') != self.session_token:
                # Send the current valid token so browser can reconnect with correct auth
                await websocket.send(json.dumps({
                    'type': 'AUTH_FAILED',
                    'message': 'Invalid authentication token',
                    'current_token': self.session_token,
                    'reconnect_url': f'http://127.0.0.1:{self.http_port}/speech-persistent.html?token={self.session_token}'
                }))
                await websocket.close()
                print(f"🚫 Authentication failed for {websocket.remote_address} - sent new token for reconnection")
                return

            await websocket.send(json.dumps({'type': 'AUTH_SUCCESS'}))
            print(f"🔐 Authenticated connection from {websocket.remote_address}")

        except (asyncio.TimeoutExpired, json.JSONDecodeError, KeyError):
            print(f"🚫 Authentication timeout/error for {websocket.remote_address}")
            await websocket.close()
            return

        # Authentication successful - add to connected clients
        self.connected_clients.add(websocket)

        # Start health monitoring for this client
        self.start_health_monitoring()

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data, websocket)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"🔌 Authenticated client disconnected: code={e.code}, reason='{e.reason}'")
        except Exception as e:
            print(f"❌ WebSocket error: {e} (type: {type(e).__name__})")
        finally:
            self.connected_clients.discard(websocket)
            if not self.connected_clients:
                self.stop_health_monitoring()

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
                if self.controller:
                    threading.Thread(
                        target=self.controller.handle_transcript,
                        args=(transcript,),
                        daemon=True
                    ).start()

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

        self.connected_clients -= disconnected
        return sent_count > 0

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

    async def start_servers(self):
        """Start both HTTP and WebSocket servers"""
        print("🚀 Starting servers...")

        # Start HTTP server in background thread
        self.http_thread = threading.Thread(
            target=self.start_http_server,
            daemon=True
        )
        self.http_thread.start()

        # Start WebSocket server
        return await websockets.serve(
            self.websocket_handler,
            "127.0.0.1",
            self.ws_port
        )

    def is_connected(self):
        return len(self.connected_clients) > 0

    def start_health_monitoring(self):
        """Start periodic health checks"""
        if self.ping_task is None:
            self.ping_task = asyncio.create_task(self.health_monitor_loop())

    def stop_health_monitoring(self):
        """Stop health monitoring"""
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None

    async def health_monitor_loop(self):
        """Periodic health check loop with aggressive keep-alive"""
        try:
            while True:
                await asyncio.sleep(15)  # More frequent checks (every 15s instead of 30s)
                if self.connected_clients:
                    print("💓 Sending health check...")
                    success = await self.send_command('PING')
                    if not success:
                        print("⚠️  Health check failed - no connected clients")
                        # Force cleanup of dead connections
                        self.connected_clients.clear()
        except asyncio.CancelledError:
            print("🛑 Health monitoring stopped")
        except Exception as e:
            print(f"❌ Health monitor error: {e}")


class WebSocketDictationController:
    def __init__(self):
        self.is_listening = False
        self.hotkey_pressed = False
        self.original_clipboard = ""
        self.ws_server = FixedDictationServer()
        self.ws_server.controller = self

        # Hotkey: Right Cmd key only
        self.hotkey_key = Key.cmd_r
        self.chrome_process = None
        self.tab_launched = False

        # Store the event loop for cross-thread access
        self.loop = None

    async def start_system(self):
        """Initialize the complete WebSocket dictation system"""
        print("🚀 Starting WebSocket dictation system...")

        try:
            # Start servers
            await self.ws_server.start_servers()
            print(f"🔌 WebSocket server: ws://127.0.0.1:{self.ws_server.ws_port}")
            print(f"🌐 HTTP server: http://127.0.0.1:{self.ws_server.http_port}")

            # Launch Chrome tab
            await self.launch_persistent_chrome_tab()

            # Wait for connection
            connected = await self.wait_for_tab_connection()

            if connected:
                print("✅ System ready for continuous dictation!")
                print("📋 Instructions:")
                print("   • Press RIGHT CMD to start continuous listening")
                print("   • Speak multiple sentences with pauses")
                print("   • Press RIGHT CMD again to stop and paste ALL text")
                print("   • Text only pastes when you stop (not after each pause)")
                print("   • Press Ctrl+C to quit")
            else:
                print("⚠️  System started but Chrome tab not connected")
                print("   Try manually opening: http://127.0.0.1:8080/speech-persistent.html")

        except Exception as e:
            print(f"❌ Failed to start system: {e}")
            raise

    async def launch_persistent_chrome_tab(self):
        """Launch Chrome with persistent speech recognition tab"""
        if self.tab_launched:
            return

        # Include authentication token in URL
        url = f"http://127.0.0.1:{self.ws_server.http_port}/speech-persistent.html?token={self.ws_server.session_token}"

        try:
            # Launch Chrome with a new tab (simpler approach)
            subprocess.run(['open', '-a', 'Google Chrome', url], check=True)
            print("🌐 Launched Chrome tab with authentication token")
            self.tab_launched = True

            # Add a small delay to let Chrome stabilize
            await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ Error launching Chrome: {e}")

    async def wait_for_tab_connection(self, timeout=15):
        """Wait for Chrome tab to connect"""
        print("⏳ Waiting for Chrome tab to connect...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ws_server.is_connected():
                print("✅ Chrome tab connected")
                return True
            await asyncio.sleep(0.5)

        print("⏰ Chrome tab connection timeout")
        return False

    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if key == self.hotkey_key and not self.hotkey_pressed:
                self.hotkey_pressed = True
                # Schedule async task using thread-safe call
                if self.loop:
                    asyncio.run_coroutine_threadsafe(
                        self.handle_hotkey_async(),
                        self.loop
                    )
        except Exception as e:
            print(f"❌ Key press error: {e}")

    def on_key_release(self, key):
        """Handle key release events"""
        try:
            if key == self.hotkey_key:
                self.hotkey_pressed = False
            if key == Key.ctrl_l or key == Key.ctrl_r:
                return False
        except Exception as e:
            print(f"❌ Key release error: {e}")

    async def handle_hotkey_async(self):
        """Handle hotkey activation"""
        try:
            if self.is_listening:
                print("⏹️  User stopping dictation...")
                await self.stop_dictation()
            else:
                print("🔴 Starting continuous dictation...")
                await self.start_dictation()
        except Exception as e:
            print(f"❌ Hotkey handler error: {e}")

    async def start_dictation(self):
        """Start dictation via WebSocket command"""
        if self.is_listening or not self.ws_server.is_connected():
            if not self.ws_server.is_connected():
                print("❌ No Chrome tab connected - try restarting the system")
                return
            return

        self.is_listening = True
        self.original_clipboard = pyperclip.paste()
        print("💾 Saved clipboard")

        success = await self.ws_server.send_command('START_LISTENING')
        if success:
            print("🎙️  Started continuous listening - speak as much as you want")
            print("    Text will accumulate until you press Right Cmd again")
        else:
            print("❌ Failed to send start command - connection may be dead")
            self.is_listening = False

            # Attempt to relaunch Chrome tab
            print("🔄 Attempting to relaunch Chrome tab...")
            await self.launch_persistent_chrome_tab()

    async def stop_dictation(self):
        """Stop dictation via WebSocket command"""
        if not self.is_listening:
            return

        self.is_listening = False
        await self.ws_server.send_command('STOP_LISTENING')
        print("⏹️  Stopped listening - processing accumulated text...")

    def handle_transcript(self, transcript):
        """Handle transcript received from Chrome tab"""
        if not transcript or not transcript.strip():
            print("⚠️  Empty transcript received - speech may not have been captured")
            return

        print(f"✨ Processing transcript: '{transcript}'")

        try:
            pyperclip.copy(transcript.strip())
            time.sleep(0.1)
            self.paste_to_active_app()

            # This only happens when user explicitly stops dictation
            print("✅ Complete dictation session pasted!")
        except Exception as e:
            print(f"❌ Error handling transcript: {e}")
            print("🔄 Transcript was:", transcript)

    def paste_to_active_app(self):
        """Paste clipboard content to active application"""
        try:
            from pynput.keyboard import Controller
            kb = Controller()

            print("📋 Auto-pasting to active application...")
            time.sleep(0.3)

            kb.press(Key.cmd)
            kb.press(KeyCode.from_char('v'))
            kb.release(KeyCode.from_char('v'))
            kb.release(Key.cmd)

            print("✅ Text pasted successfully!")
        except Exception as e:
            print(f"❌ Error pasting text: {e}")

    async def run_async(self):
        """Run the async parts of the system"""
        # Store the loop for cross-thread access
        self.loop = asyncio.get_running_loop()

        await self.start_system()

        # Keep the async loop running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")

    def run(self):
        """Start the complete dictation system"""
        try:
            # Create event loop and run async setup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Start async system in background
            async_task = loop.create_task(self.run_async())

            # Start hotkey listener in main thread
            print("🎤 Starting hotkey listener...")

            def run_listener():
                with Listener(
                    on_press=self.on_key_press,
                    on_release=self.on_key_release
                ) as listener:
                    listener.join()

            listener_thread = threading.Thread(target=run_listener, daemon=True)
            listener_thread.start()

            # Run the event loop
            loop.run_until_complete(async_task)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    try:
        controller = WebSocketDictationController()
        controller.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")