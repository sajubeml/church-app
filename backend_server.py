import http.server
import socketserver
import os
import json
import sqlite3
import socket

PORT = 8088
DB_NAME = "church_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

class ChurchBackendHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching and allow CORS for local dev
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/data':
            try:
                conn = get_db_connection()
                
                # Fetch Cashbook and map to frontend Excel keys (A, B, C...)
                raw_cashbook = [dict(row) for row in conn.execute('SELECT * FROM cashbook').fetchall()]
                cashbook = []
                for row in raw_cashbook:
                    cashbook.append({
                        "A": row.get("date", ""),
                        "B": row.get("receipt_no", ""),
                        "C": row.get("reg_no", ""),
                        "D": row.get("name_of_hof", ""),
                        "E": row.get("receipt_acct_head", ""),
                        "F": row.get("receipt_code", ""),
                        "G": row.get("receipt_details", ""),
                        "H": row.get("receipt_cash", ""),
                        "I": row.get("receipt_bank", ""),
                        "K": row.get("payment_date", ""),
                        "L": row.get("payment_voucher_no", ""),
                        "M": row.get("payment_acct_head", ""),
                        "N": row.get("payment_code", ""),
                        "O": row.get("payment_details", ""),
                        "P": row.get("payment_cash", ""),
                        "Q": row.get("payment_bank", "")
                    })
                
                # Fetch Members
                members = [dict(row) for row in conn.execute('SELECT * FROM members').fetchall()]
                
                # Fetch Account Heads
                heads = [dict(row) for row in conn.execute('SELECT * FROM account_heads').fetchall()]
                
                # Fetch Individual Ledgers
                ledgers = [dict(row) for row in conn.execute('SELECT * FROM individual_ledgers').fetchall()]
                
                conn.close()

                data = {
                    "cashbook": cashbook,
                    "members": members,
                    "accountHeads": heads,
                    "individualLedgers": ledgers
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save_receipt' or self.path == '/api/save_payment':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                conn = get_db_connection()
                
                if self.path == '/api/save_receipt':
                    conn.execute('''
                        INSERT INTO cashbook (
                            date, receipt_no, reg_no, name_of_hof, receipt_acct_head, receipt_code, receipt_details, receipt_cash, receipt_bank
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data.get('date'), data.get('receipt_no'), data.get('reg_no'), data.get('name_of_hof'),
                        data.get('receipt_acct_head'), data.get('receipt_code'), data.get('receipt_details'), 
                        data.get('receipt_cash', 0), data.get('receipt_bank', 0)
                    ))
                else:
                    conn.execute('''
                        INSERT INTO cashbook (
                            payment_date, payment_voucher_no, payment_acct_head, payment_code, payment_details, payment_cash, payment_bank
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data.get('payment_date'), data.get('payment_voucher_no'),
                        data.get('payment_acct_head'), data.get('payment_code'), data.get('payment_details'), 
                        data.get('payment_cash', 0), data.get('payment_bank', 0)
                    ))
                    
                conn.commit()
                conn.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        if self.path == '/api/bulk_import':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                cashbook_data = json.loads(body)
                conn = get_db_connection()
                
                # Clear existing cashbook
                conn.execute('DELETE FROM cashbook')
                
                # Insert all new rows
                for row in cashbook_data:
                    conn.execute('''
                        INSERT INTO cashbook (
                            date, receipt_no, reg_no, name_of_hof, receipt_acct_head, receipt_code, receipt_details, receipt_cash, receipt_bank,
                            payment_date, payment_voucher_no, payment_acct_head, payment_code, payment_details, payment_cash, payment_bank
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get("A", ""), row.get("B", ""), row.get("C", ""), row.get("D", ""),
                        row.get("E", ""), row.get("F", ""), row.get("G", ""), row.get("H", 0), row.get("I", 0),
                        row.get("K", ""), row.get("L", ""), row.get("M", ""), row.get("N", ""),
                        row.get("O", ""), row.get("P", 0), row.get("Q", 0)
                    ))
                    
                conn.commit()
                conn.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
            
        if self.path == '/api/save_print':
            # Existing print logic from start_server.py
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

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
            return

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
    handler = ChurchBackendHandler
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
        print("[ERROR] Could not find an open network port.")
        return

    print("==================================================")
    print("  ST. GREGORIOS CHURCH NEW DB BACKEND SERVER  ")
    print(f"  Desktop PC URL  : http://localhost:{port}/")
    print(f"  Mobile Wi-Fi URL: http://{local_ip}:{port}/")
    print("==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
