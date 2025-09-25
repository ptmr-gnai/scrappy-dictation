#!/usr/bin/env python3
"""
Clipboard Bridge Dictation
Listens for global hotkey, triggers speech recognition, auto-pastes result
"""

import time
import threading
import subprocess
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Listener, HotKey


class ClipboardDictation:
    def __init__(self):
        self.is_listening = False
        self.hotkey_pressed = False
        self.original_clipboard = ""

        # Hotkey combination: Cmd+Shift+Space
        self.hotkey_combination = {Key.cmd, Key.shift, Key.space}
        self.pressed_keys = set()

        print("🎤 Clipboard Dictation Bridge Starting...")
        print("Hotkey: Cmd+Shift+Space")
        print("Press Ctrl+C to quit")

    def is_hotkey_combination(self, key, pressed_keys):
        """Check if the current pressed keys match our hotkey combination"""
        if key in self.hotkey_combination:
            pressed_keys.add(key)

        # Check if all hotkey keys are pressed
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
            print("🔴 Starting dictation... (speak now)")
            self.start_dictation()

    def start_dictation(self):
        """Start the dictation process"""
        if self.is_listening:
            return

        self.is_listening = True

        try:
            # Save current clipboard
            self.original_clipboard = pyperclip.paste()
            print(f"💾 Saved clipboard: '{self.original_clipboard[:50]}{'...' if len(self.original_clipboard) > 50 else ''}'")

            # Open Chrome with our speech recognition page
            self.open_speech_page()

            # Start monitoring clipboard for changes
            threading.Thread(target=self.monitor_clipboard, daemon=True).start()

        except Exception as e:
            print(f"❌ Error starting dictation: {e}")
            self.is_listening = False

    def stop_dictation(self):
        """Stop the dictation process"""
        self.is_listening = False
        print("⏹️  Dictation stopped")

    def open_speech_page(self):
        """Open Chrome with the speech recognition page"""
        try:
            # Get absolute path to our HTML file
            import os
            html_path = os.path.join(os.getcwd(), "speech-test.html")

            # Open in Chrome specifically (better speech recognition)
            subprocess.run([
                'open', '-a', 'Google Chrome', html_path
            ], check=True)

            print("🌐 Opened speech recognition page in Chrome")
            print("   Click 'Start Listening' and speak...")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to open Chrome: {e}")
            print("   Please manually open speech-test.html in Chrome")
        except Exception as e:
            print(f"❌ Error opening speech page: {e}")

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
                time.sleep(0.5)  # Check every 500ms

            except Exception as e:
                print(f"❌ Clipboard monitoring error: {e}")
                break

    def looks_like_dictated_text(self, text):
        """Heuristic to determine if text looks like it came from dictation"""
        if not text or not text.strip():
            return False

        # Simple heuristics:
        # - Not too short (avoid single chars)
        # - Contains letters
        # - Reasonable length for speech
        text = text.strip()
        return (len(text) > 2 and
                any(c.isalpha() for c in text) and
                len(text) < 1000)

    def handle_new_text(self, text):
        """Handle newly dictated text"""
        try:
            print(f"✨ Processing dictated text: '{text}'")

            # Clean up the text (remove extra whitespace, etc.)
            cleaned_text = text.strip()

            # Put the text back in clipboard (in case it got modified)
            pyperclip.copy(cleaned_text)

            # Wait a moment for clipboard to update
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
            from pynput.keyboard import Controller
            kb = Controller()

            print("📋 Auto-pasting to active application...")

            # Give a brief moment for focus
            time.sleep(0.2)

            # Simulate Cmd+V
            kb.press(Key.cmd)
            kb.press(KeyCode.from_char('v'))
            kb.release(KeyCode.from_char('v'))
            kb.release(Key.cmd)

            print("✅ Text pasted successfully!")

        except Exception as e:
            print(f"❌ Error pasting text: {e}")
            print("   You can manually paste with Cmd+V")

    def restore_clipboard(self):
        """Restore the original clipboard content"""
        try:
            if self.original_clipboard:
                pyperclip.copy(self.original_clipboard)
                print(f"🔄 Restored original clipboard: '{self.original_clipboard[:50]}{'...' if len(self.original_clipboard) > 50 else ''}'")
        except Exception as e:
            print(f"❌ Error restoring clipboard: {e}")

    def run(self):
        """Start the global hotkey listener"""
        print("🚀 Dictation bridge is running!")
        print("   Press Cmd+Shift+Space to start/stop dictation")
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


if __name__ == "__main__":
    # Import here to avoid issues if not available
    from pynput.keyboard import KeyCode

    try:
        app = ClipboardDictation()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Make sure you have the required permissions:")
        print("   System Preferences → Security & Privacy → Privacy → Input Monitoring")
        print("   Add your Terminal app to the list")