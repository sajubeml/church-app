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

PORT = 8088

import json

class ChurchHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching during local dev
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_POST(self):
        if self.path == '/api/save_print':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                filename = data.get('filename', 'Receipt.html')
                content = data.get('content', '')
                
                print_dir = os.path.join(os.getcwd(), 'Receipts')
                os.makedirs(print_dir, exist_ok=True)
                filepath = os.path.join(print_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # Generate PDF automatically using Edge headless converter
                pdf_filename = filename.replace('.html', '.pdf')
                if not pdf_filename.endswith('.pdf'):
                    pdf_filename += '.pdf'
                pdf_filepath = os.path.join(print_dir, pdf_filename)

                edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                if not os.path.exists(edge_path):
                    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

                if os.path.exists(edge_path):
                    import subprocess
                    cmd = [edge_path, "--headless", f"--print-to-pdf={pdf_filepath}", "--no-pdf-header-footer", filepath]
                    subprocess.run(cmd, capture_output=True, text=True)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'path': filepath, 'pdf_url': f'Receipts/{pdf_filename}'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
            return

import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = ChurchHTTPRequestHandler
    local_ip = get_local_ip()

    port = PORT
    httpd = None
    for try_port in [8090, 8888, 8088, 8095]:
        try:
            httpd = socketserver.TCPServer(("", try_port), handler)
            port = try_port
            break
        except Exception:
            continue

    if not httpd:
        print("[ERROR] Could not find an open network port for mobile server.")
        return

    print("==================================================")
    print("  ST. GREGORIOS CHURCH ACCOUNTING MOBILE SERVER  ")
    print(f"  Desktop PC URL  : http://localhost:{port}/")
    print(f"  Mobile Wi-Fi URL: http://{local_ip}:{port}/")
    print("==================================================")
    print("Connect phone to same Wi-Fi and open Mobile Wi-Fi URL.")
    print("Press Ctrl+C to stop the server.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
