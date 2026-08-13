import sqlite3
import json
import os

DB_NAME = "church_data.db"
DATA_DIR = "data_export"

def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    with open("database_schema.sql", "r") as f:
        conn.executescript(f.read())
    return conn

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename + ".json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def migrate_cashbook(conn):
    data = load_json("Cash_Book")
    cursor = conn.cursor()
    for row in data:
        cursor.execute('''
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
    print(f"Migrated {len(data)} cashbook entries.")

def main():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        
    print("Initializing database...")
    conn = initialize_db()
    
    print("Migrating Cashbook...")
    migrate_cashbook(conn)
    
    # You can expand this to migrate members and individual ledgers as well
    print("Migration complete!")
    conn.close()

if __name__ == "__main__":
    main()
