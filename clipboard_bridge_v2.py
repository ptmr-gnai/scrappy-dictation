#!/usr/bin/env python3
"""
Clipboard Bridge Dictation V2 - Zero Manual Steps
Auto-starts speech recognition, auto-copies, auto-pastes
"""

import time
import threading
import subprocess
import pyperclip
import os
from pynput import keyboard
from pynput.keyboard import Key, Listener, KeyCode

# Import our speech server
from speech_server import SpeechServer


class ClipboardDictationV2:
    def __init__(self):
        self.is_listening = False
        self.hotkey_pressed = False
        self.original_clipboard = ""
        self.speech_server = SpeechServer(port=8080)

        # Hotkey combination: Cmd+Shift+Space
        self.hotkey_combination = {Key.cmd, Key.shift, Key.space}
        self.pressed_keys = set()

        print("🎤 Clipboard Dictation Bridge V2 - Zero Manual Steps")
        print("Hotkey: Cmd+Shift+Space (start/stop)")
        print("Press Ctrl+C to quit")

    def start_server(self):
        """Start the speech recognition server"""
        if self.speech_server.start():
            print("✅ Speech server started successfully")
            return True
        else:
            print("❌ Failed to start speech server")
            return False

    def stop_server(self):
        """Stop the speech recognition server"""
        self.speech_server.stop()

    def is_hotkey_combination(self, key, pressed_keys):
        """Check if the current pressed keys match our hotkey combination"""
        if key in self.hotkey_combination:
            pressed_keys.add(key)
        return self.hotkey_combination.issubset(pressed_keys)

    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if self.is_hotkey_combination(key, self.pressed_keys):
                if not self.hotkey_pressed:
                    self.hotkey_pressed = True
                    threading.Thread(target=self.handle_hotkey, daemon=True).start()
        except Exception as e:
            print(f"Key press error: {e}")

    def on_key_release(self, key):
        """Handle key release events"""
        try:
            # Remove key from pressed set
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)

            # Reset hotkey flag when any hotkey key is released
            if key in self.hotkey_combination:
                self.hotkey_pressed = False

            # Quit on Ctrl+C
            if key == Key.ctrl_l or key == Key.ctrl_r:
                return False

        except Exception as e:
            print(f"Key release error: {e}")

    def handle_hotkey(self):
        """Handle hotkey activation"""
        if self.is_listening:
            print("⏹️  Stopping dictation...")
            self.stop_dictation()
        else:
            print("🔴 Starting dictation...")
            self.start_dictation()

    def start_dictation(self):
        """Start the dictation process with zero manual steps"""
        if self.is_listening:
            return

        self.is_listening = True

        try:
            # Save current clipboard
            self.original_clipboard = pyperclip.paste()
            print(f"💾 Saved clipboard: '{self.original_clipboard[:30]}{'...' if len(self.original_clipboard) > 30 else ''}'")

            # Open speech page with auto-start
            self.open_speech_page_auto()

            # Start monitoring clipboard for changes
            threading.Thread(target=self.monitor_clipboard, daemon=True).start()

        except Exception as e:
            print(f"❌ Error starting dictation: {e}")
            self.is_listening = False

    def stop_dictation(self):
        """Stop the dictation process"""
        self.is_listening = False
        print("⏹️  Dictation stopped")

        # Send stop signal to browser page
        self.send_stop_to_browser()

    def open_speech_page_auto(self):
        """Open speech page with auto-start enabled"""
        try:
            url = f"http://localhost:8080/speech-auto.html?autostart=true"

            # Try to open in Chrome with focus to trigger auto-start
            chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                'google-chrome'
            ]

            opened_in_chrome = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    # Open in Chrome and bring to front
                    subprocess.run([
                        chrome_path, url, '--new-window'
                    ], check=True)
                    opened_in_chrome = True
                    break

            if not opened_in_chrome:
                # Fallback to default browser
                subprocess.run(['open', url], check=True)

            print("🌐 Opened auto-start speech page")

            # Give Chrome a moment to load and auto-start
            time.sleep(1.5)

            # Bring Chrome to front to ensure auto-start triggers
            self.bring_chrome_to_front()

        except Exception as e:
            print(f"❌ Error opening speech page: {e}")

    def bring_chrome_to_front(self):
        """Bring Chrome to front to trigger auto-start"""
        try:
            applescript = '''
            tell application "Google Chrome"
                activate
                delay 0.5
                tell front window
                    set active tab index to 1
                end tell
            end tell
            '''

            subprocess.run(['osascript', '-e', applescript],
                         capture_output=True, timeout=3)

            print("📱 Activated Chrome for auto-start")

        except Exception as e:
            print(f"⚠️  Could not activate Chrome: {e}")

    def send_stop_to_browser(self):
        """Send stop signal to browser page"""
        try:
            # Focus Chrome and send Cmd+Space to stop listening
            applescript = '''
            tell application "Google Chrome"
                activate
                delay 0.2
            end tell

            tell application "System Events"
                key down {command}
                key code 49
                key up {command}
            end tell
            '''

            subprocess.run(['osascript', '-e', applescript],
                         capture_output=True, timeout=3)

        except Exception as e:
            print(f"⚠️  Could not send stop signal: {e}")

    def monitor_clipboard(self):
        """Monitor clipboard for new dictated text"""
        print("👁️  Monitoring clipboard for dictated text...")

        last_clipboard = self.original_clipboard
        start_time = time.time()
        timeout = 30  # 30 second timeout

        while self.is_listening:
            try:
                current_clipboard = pyperclip.paste()

                # Check if clipboard changed and it's new content
                if (current_clipboard != last_clipboard and
                    current_clipboard != self.original_clipboard and
                    current_clipboard.strip() and
                    self.looks_like_dictated_text(current_clipboard)):

                    print(f"📝 New dictated text detected: '{current_clipboard}'")
                    self.handle_new_text(current_clipboard)
                    break

                # Timeout check
                if time.time() - start_time > timeout:
                    print("⏰ Dictation timeout - stopping")
                    self.stop_dictation()
                    break

                last_clipboard = current_clipboard
                time.sleep(0.3)  # Check every 300ms

            except Exception as e:
                print(f"❌ Clipboard monitoring error: {e}")
                break

    def looks_like_dictated_text(self, text):
        """Heuristic to determine if text looks like it came from dictation"""
        if not text or not text.strip():
            return False

        text = text.strip()
        return (len(text) > 1 and
                any(c.isalpha() for c in text) and
                len(text) < 1000)

    def handle_new_text(self, text):
        """Handle newly dictated text with auto-paste"""
        try:
            print(f"✨ Processing dictated text: '{text}'")

            # Clean up the text
            cleaned_text = text.strip()

            # Put the text back in clipboard
            pyperclip.copy(cleaned_text)
            time.sleep(0.1)

            # Auto-paste into active application
            self.paste_to_active_app()

            # Stop dictation
            self.stop_dictation()

        except Exception as e:
            print(f"❌ Error handling dictated text: {e}")

    def paste_to_active_app(self):
        """Paste clipboard content to the active application"""
        try:
            print("📋 Auto-pasting to active application...")

            # Give Chrome a moment to unfocus
            time.sleep(0.3)

            # Use AppleScript for more reliable pasting
            applescript = '''
            tell application "System Events"
                keystroke "v" using {command down}
            end tell
            '''

            result = subprocess.run(['osascript', '-e', applescript],
                                  capture_output=True, timeout=3)

            if result.returncode == 0:
                print("✅ Text pasted successfully!")
            else:
                print(f"⚠️  Paste may have failed: {result.stderr.decode()}")

        except Exception as e:
            print(f"❌ Error pasting text: {e}")
            print("   You can manually paste with Cmd+V")

    def restore_clipboard(self):
        """Restore the original clipboard content"""
        try:
            if self.original_clipboard:
                pyperclip.copy(self.original_clipboard)
                print(f"🔄 Restored original clipboard")
        except Exception as e:
            print(f"❌ Error restoring clipboard: {e}")

    def run(self):
        """Start the dictation bridge"""
        print("🚀 Starting Dictation Bridge V2...")

        # Start the HTTP server first
        if not self.start_server():
            return

        print("🎤 Ready for zero-step dictation!")
        print("   Press Cmd+Shift+Space to start dictation")
        print("   Press Cmd+Shift+Space again to stop")
        print("   Press Ctrl+C to quit")

        try:
            with Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            ) as listener:
                listener.join()
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        except Exception as e:
            print(f"❌ Error in hotkey listener: {e}")
        finally:
            if self.is_listening:
                self.restore_clipboard()
            self.stop_server()


if __name__ == "__main__":
    try:
        app = ClipboardDictationV2()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Make sure you have the required permissions:")
        print("   System Preferences → Security & Privacy → Privacy → Input Monitoring")
        print("   Add your Terminal app to the list")