#!/usr/bin/env python3
"""
Simple HTTP server to receive dictated text from browser and send to Terminal
"""

import json
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs

class DictationHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/dictation':
            # Get the content length
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Parse JSON data
                data = json.loads(post_data.decode('utf-8'))
                text = data.get('text', '').strip()

                if text:
                    print(f"Received: {text}")

                    # Send to Terminal using AppleScript
                    self.send_to_terminal(text)

                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'success'}).encode())
                else:
                    self.send_error(400, "No text provided")

            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                print(f"Error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_to_terminal(self, text):
        """Send text to the active Terminal window using AppleScript"""
        # Escape text for AppleScript
        escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

        applescript = f'''
        tell application "Terminal"
            if (count of windows) > 0 then
                do script "{escaped_text}" in front window
            else
                do script "{escaped_text}"
            end if
        end tell
        '''

        try:
            # Run AppleScript
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print(f"AppleScript error: {result.stderr}")
            else:
                print(f"Sent to Terminal: {text}")

        except subprocess.TimeoutExpired:
            print("AppleScript timeout")
        except Exception as e:
            print(f"Error sending to Terminal: {e}")

def run_server(port=8080):
    """Start the HTTP server"""
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, DictationHandler)

    print(f"Starting dictation server on http://localhost:{port}")
    print("Send POST requests to /dictation with JSON: {'text': 'your text'}")
    print("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()