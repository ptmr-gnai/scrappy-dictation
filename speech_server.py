#!/usr/bin/env python3
"""
HTTP server to serve the speech recognition page from localhost
This fixes clipboard permissions and enables auto-start functionality
"""

import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser


class SpeechServer:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the HTTP server in a background thread"""
        try:
            server_address = ('localhost', self.port)
            self.server = HTTPServer(server_address, SimpleHTTPRequestHandler)

            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()

            print(f"🌐 Speech server running at http://localhost:{self.port}")
            return True

        except Exception as e:
            print(f"❌ Failed to start speech server: {e}")
            return False

    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🛑 Speech server stopped")

    def open_speech_page(self):
        """Open the speech recognition page in browser"""
        url = f"http://localhost:{self.port}/speech-auto.html"
        try:
            # Try to open in Chrome specifically for better speech recognition
            chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/usr/bin/google-chrome',
                'google-chrome'
            ]

            opened_in_chrome = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    os.system(f'"{chrome_path}" "{url}" >/dev/null 2>&1 &')
                    opened_in_chrome = True
                    break

            if not opened_in_chrome:
                # Fallback to default browser
                webbrowser.open(url)

            print(f"🔗 Opened speech page: {url}")
            return True

        except Exception as e:
            print(f"❌ Failed to open speech page: {e}")
            return False


if __name__ == "__main__":
    server = SpeechServer()

    try:
        if server.start():
            print("✅ Server started successfully")
            print("📱 Opening speech recognition page...")
            server.open_speech_page()

            print("\n🎤 Ready for dictation!")
            print("Press Ctrl+C to stop server")

            # Keep server running
            while True:
                import time
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.stop()
    except Exception as e:
        print(f"❌ Server error: {e}")
        server.stop()