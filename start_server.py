"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Local Web HTTP Server (Python Native)
Replaces start_server.ps1
"""

import http.server
import socketserver
import os
import webbrowser

PORT = 8080

class ChurchHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching during local dev
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = ChurchHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("==================================================")
        print("  ST. GREGORIOS CHURCH ACCOUNTING PORTAL STARTED  ")
        print(f"  URL: http://localhost:{PORT}/")
        print("==================================================")
        print("Press Ctrl+C to stop the server.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
