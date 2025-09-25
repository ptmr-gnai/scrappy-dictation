#!/usr/bin/env python3
"""
WebSocket Dictation Controller
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
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode

# Import our WebSocket server
from websocket_server import DictationWebSocketServer


class WebSocketDictationController:
    def __init__(self):
        self.is_listening = False
        self.hotkey_pressed = False
        self.original_clipboard = ""
        self.ws_server = DictationWebSocketServer()
        self.ws_server.controller = self  # Link back to this controller

        # Hotkey: Right Cmd key only
        self.hotkey_key = Key.cmd_r  # Right Cmd
        self.hotkey_pressed = False

        # Chrome process tracking
        self.chrome_process = None
        self.tab_launched = False

        # Event loop for async operations
        self.loop = None
        self.loop_thread = None

        print("🎤 WebSocket Dictation Controller")
        print("Zero-manual-step dictation system")

    def start_event_loop(self):
        """Start async event loop in background thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()

        # Wait for loop to be ready
        while self.loop is None:
            time.sleep(0.1)

    def run_async(self, coro):
        """Run coroutine in the background event loop"""
        if self.loop:
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            return future
        else:
            print("❌ Event loop not running")

    async def start_system(self):
        """Initialize the complete WebSocket dictation system"""
        print("🚀 Starting WebSocket dictation system...")

        try:
            # Start WebSocket and HTTP servers
            websocket_server = await self.ws_server.start_servers()
            print(f"🔌 WebSocket server: ws://localhost:{self.ws_server.ws_port}")
            print(f"🌐 HTTP server: http://localhost:{self.ws_server.http_port}")

            # Launch persistent Chrome tab
            await self.launch_persistent_chrome_tab()

            # Wait for tab connection
            connected = await self.wait_for_tab_connection()

            if connected:
                print("✅ System ready for zero-step dictation!")
                print("📋 Instructions:")
                print("   • Press RIGHT CMD to start dictating")
                print("   • Speak your text")
                print("   • Press RIGHT CMD again to stop (or just pause)")
                print("   • Text auto-pastes to active app")
                print("   • Press Ctrl+C to quit")
            else:
                print("⚠️  System started but Chrome tab not connected")
                print("   Try manually opening: http://localhost:8080/speech-persistent.html")

            return websocket_server

        except Exception as e:
            print(f"❌ Failed to start system: {e}")
            raise

    async def launch_persistent_chrome_tab(self):
        """Launch Chrome with persistent speech recognition tab"""
        if self.tab_launched:
            print("📱 Chrome tab already launched")
            return

        url = f"http://localhost:{self.ws_server.http_port}/speech-persistent.html"

        try:
            # Try Chrome app mode first (minimal UI)
            chrome_cmd = [
                'google-chrome',
                '--app=' + url,
                '--disable-features=TranslateUI',
                '--autoplay-policy=no-user-gesture-required',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--window-position=0,0',
                '--window-size=300,200'  # Small but visible for debugging
            ]

            self.chrome_process = subprocess.Popen(
                chrome_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print("🌐 Launched persistent Chrome tab (app mode)")
            self.tab_launched = True

        except FileNotFoundError:
            # Fallback: try different Chrome paths
            chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                'open -a "Google Chrome"'
            ]

            for chrome_path in chrome_paths:
                try:
                    if chrome_path.startswith('open'):
                        subprocess.run(chrome_path.split() + [url], check=True)
                    else:
                        subprocess.run([chrome_path, url], check=True)

                    print("🌐 Launched Chrome tab (fallback method)")
                    self.tab_launched = True
                    break

                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue

            if not self.tab_launched:
                print("❌ Could not launch Chrome")
                print(f"   Please manually open: {url}")

        except Exception as e:
            print(f"❌ Error launching Chrome: {e}")
            print(f"   Please manually open: {url}")

    async def wait_for_tab_connection(self, timeout=15):
        """Wait for Chrome tab to connect via WebSocket"""
        print("⏳ Waiting for Chrome tab to connect...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ws_server.is_connected():
                connection_count = self.ws_server.get_connection_count()
                print(f"✅ Chrome tab connected ({connection_count} connection(s))")
                return True

            await asyncio.sleep(0.5)

        print("⏰ Chrome tab connection timeout")
        return False

    def is_hotkey(self, key):
        """Check if the key is our hotkey"""
        return key == self.hotkey_key

    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if self.is_hotkey(key) and not self.hotkey_pressed:
                self.hotkey_pressed = True
                # Run async handler
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
            # Reset hotkey flag when right cmd is released
            if key == self.hotkey_key:
                self.hotkey_pressed = False

            # Quit on Ctrl+C
            if key == Key.ctrl_l or key == Key.ctrl_r:
                return False

        except Exception as e:
            print(f"❌ Key release error: {e}")

    async def handle_hotkey_async(self):
        """Handle hotkey activation asynchronously"""
        try:
            if self.is_listening:
                print("⏹️  Stopping dictation...")
                await self.stop_dictation()
            else:
                print("🔴 Starting dictation...")
                await self.start_dictation()
        except Exception as e:
            print(f"❌ Hotkey handler error: {e}")

    async def start_dictation(self):
        """Start dictation via WebSocket command"""
        if self.is_listening:
            return

        if not self.ws_server.is_connected():
            print("❌ No Chrome tab connected - cannot start dictation")
            print("   Try opening: http://localhost:8080/speech-persistent.html")
            return

        self.is_listening = True

        try:
            # Save current clipboard
            self.original_clipboard = pyperclip.paste()
            print(f"💾 Saved clipboard")

            # Send start command to Chrome tab
            success = await self.ws_server.send_command('START_LISTENING')

            if success:
                print("🎙️  Sent start command to Chrome tab")

                # Start timeout monitoring
                asyncio.create_task(self.dictation_timeout_monitor())
            else:
                print("❌ Failed to send start command")
                self.is_listening = False

        except Exception as e:
            print(f"❌ Error starting dictation: {e}")
            self.is_listening = False

    async def stop_dictation(self):
        """Stop dictation via WebSocket command"""
        if not self.is_listening:
            print("⚠️  Not currently listening")
            return

        self.is_listening = False

        try:
            # Send stop command to Chrome tab
            await self.ws_server.send_command('STOP_LISTENING')
            print("⏹️  Sent stop command to Chrome tab")

        except Exception as e:
            print(f"❌ Error stopping dictation: {e}")

    def handle_transcript(self, transcript):
        """Handle transcript received from Chrome tab (called from WebSocket server)"""
        if not transcript or not transcript.strip():
            print("⚠️  Empty transcript received")
            return

        print(f"✨ Processing transcript: '{transcript}'")

        try:
            # Ensure text is in clipboard (Chrome tab should have copied it)
            pyperclip.copy(transcript.strip())
            time.sleep(0.1)

            # Auto-paste to active application
            self.paste_to_active_app()

            # Stop dictation
            if self.loop:
                asyncio.run_coroutine_threadsafe(
                    self.stop_dictation(),
                    self.loop
                )

        except Exception as e:
            print(f"❌ Error handling transcript: {e}")

    def paste_to_active_app(self):
        """Paste clipboard content to active application"""
        try:
            from pynput.keyboard import Controller
            kb = Controller()

            print("📋 Auto-pasting to active application...")

            # Brief delay to ensure Chrome is not focused
            time.sleep(0.3)

            # Simulate Cmd+V
            kb.press(Key.cmd)
            kb.press(KeyCode.from_char('v'))
            kb.release(KeyCode.from_char('v'))
            kb.release(Key.cmd)

            print("✅ Text pasted successfully!")

        except Exception as e:
            print(f"❌ Error pasting text: {e}")
            print("   You can manually paste with Cmd+V")

    async def dictation_timeout_monitor(self):
        """Monitor for dictation timeout"""
        await asyncio.sleep(30)  # 30 second timeout

        if self.is_listening:
            print("⏰ Dictation timeout - stopping")
            await self.stop_dictation()

    def restore_clipboard(self):
        """Restore the original clipboard content"""
        try:
            if self.original_clipboard:
                pyperclip.copy(self.original_clipboard)
                print("🔄 Restored original clipboard")
        except Exception as e:
            print(f"❌ Error restoring clipboard: {e}")

    async def shutdown(self):
        """Shutdown the system gracefully"""
        print("\n👋 Shutting down WebSocket dictation system...")

        try:
            # Stop dictation if active
            if self.is_listening:
                await self.stop_dictation()

            # Restore clipboard
            self.restore_clipboard()

            # Stop servers
            self.ws_server.stop_servers()

            # Close Chrome process if we launched it
            if self.chrome_process:
                try:
                    self.chrome_process.terminate()
                    self.chrome_process.wait(timeout=3)
                    print("🌐 Chrome process closed")
                except subprocess.TimeoutExpired:
                    self.chrome_process.kill()
                    print("🌐 Chrome process killed")
                except Exception as e:
                    print(f"⚠️  Could not close Chrome: {e}")

            # Stop event loop
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)

            print("✅ Shutdown complete")

        except Exception as e:
            print(f"❌ Error during shutdown: {e}")

    def run(self):
        """Start the complete dictation system"""
        try:
            # Start event loop
            self.start_event_loop()

            # Initialize system
            future = asyncio.run_coroutine_threadsafe(
                self.start_system(),
                self.loop
            )
            websocket_server = future.result(timeout=30)

            # Set up signal handlers
            def signal_handler(signum, frame):
                print("\n🛑 Interrupt received...")
                shutdown_future = asyncio.run_coroutine_threadsafe(
                    self.shutdown(),
                    self.loop
                )
                shutdown_future.result(timeout=10)
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Start hotkey listener
            print("🎤 Starting hotkey listener...")
            with Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            ) as listener:
                listener.join()

        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt")
        except Exception as e:
            print(f"❌ Fatal error: {e}")
        finally:
            # Ensure cleanup
            try:
                if self.loop and not self.loop.is_closed():
                    asyncio.run_coroutine_threadsafe(
                        self.shutdown(),
                        self.loop
                    ).result(timeout=5)
            except:
                pass


if __name__ == "__main__":
    try:
        controller = WebSocketDictationController()
        controller.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Make sure you have the required permissions:")
        print("   System Preferences → Security & Privacy → Privacy → Input Monitoring")
        print("   Add your Terminal app to the list")