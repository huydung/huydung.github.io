#!/usr/bin/env python3
"""
Simple HTTP server for DBA Knowledge Map.
Serves files from the current directory with CORS headers enabled,
so the HTML can fetch .md content files via async requests.

Usage:
    python serve.py          # starts on port 8000
    python serve.py 3000     # starts on port 3000
"""

import http.server
import socketserver
import sys
import os
import webbrowser
from functools import partial

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that adds CORS headers and proper MIME types."""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def guess_type(self, path):
        """Ensure .md files are served as text."""
        if path.endswith('.md'):
            return 'text/markdown; charset=utf-8'
        return super().guess_type(path)

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directory)

    handler = partial(CORSRequestHandler, directory=directory)

    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/index.html"
        print(f"\n  DBA Knowledge Map Server")
        print(f"  {'='*40}")
        print(f"  Serving from: {directory}")
        print(f"  Open in browser: {url}")
        print(f"  Press Ctrl+C to stop\n")

        # Auto-open in default browser
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")

if __name__ == "__main__":
    main()
