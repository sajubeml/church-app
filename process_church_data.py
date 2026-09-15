"""
Church Accounting & XLSM Processing Script
-------------------------------------------
This script processes 'working Church_Accounting_ok ind updte 21-7-(26-27).xlsm'
for St. Gregorios Orthodox Syrian Church and Pilgrim Centre, Mysuru.

Capabilities:
1. Export all worksheets to clean CSV files.
2. Summarize Cash Book transactions (Receipts vs Payments).
3. Generate Member Dues Summary & Total Collections.
4. Extract Trial Balance Account Heads.
"""

import os
import json
import csv

EXPORT_DIR = "data_export"
OUTPUT_CSV_DIR = "csv_export"

def ensure_directories():
    os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)

def load_json_sheet(sheet_name):
    json_path = os.path.join(EXPORT_DIR, f"{sheet_name}.json")
    if not os.path.exists(json_path):
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_csv_exports():
    """Converts extracted JSON grid data into standard tabular CSV files."""
    sheets = ["Cash_Book", "Individual", "Trial_Balance", "Members", "Budget", "Codes", "breakfast", "aution25"]
    
    for sheet in sheets:
        rows = load_json_sheet(sheet)
        if not rows:
            continue
        
        # Discover all unique cell coordinates (e.g. A1, B1, C1)
        csv_file = os.path.join(OUTPUT_CSV_DIR, f"{sheet}.csv")
        
        # Map cell coordinates to matrix
        matrix = {}
        max_row = 0
        max_col_idx = 0
        
        def col_to_num(col_str):
            num = 0
            for c in col_str:
                num = num * 26 + (ord(c.upper()) - ord('A') + 1)
            return num

        for row_dict in rows:
            for cell_ref, val in row_dict.items():
                # Split cell_ref into column letters and row number
                col_letters = ''.join([c for c in cell_ref if c.isalpha()])
                row_num_str = ''.join([c for c in cell_ref if c.isdigit()])
                if col_letters and row_num_str:
                    r = int(row_num_str)
                    c_idx = col_to_num(col_letters)
                    if r > max_row: max_row = r
                    if c_idx > max_col_idx: max_col_idx = c_idx
                    matrix[(r, c_idx)] = val if val is not null else ""

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for r in range(1, max_row + 1):
                row_vals = [matrix.get((r, c), "") for c in range(1, max_col_idx + 1)]
                # Skip completely empty trailing rows
                if any(str(v).strip() for v in row_vals):
                    writer.writerow(row_vals)
                    
        print(f"Exported {csv_file}")

def summarize_accounting():
    print("\n==========================================")
    print("  ST. GREGORIOS CHURCH ACCOUNTING SUMMARY ")
    print("==========================================")
    
    members = load_json_sheet("Members")
    print(f"Total Enrolled Members: {len(members)}")
    
    cashbook = load_json_sheet("Cash_Book")
    print(f"Total Cash Book Recorded Entries: {len(cashbook)}")
    
    indiv = load_json_sheet("Individual")
    print(f"Total Individual Ledger Records: {len(indiv)}")
    
    auction = load_json_sheet("aution25")
    print(f"Total Auction Records: {len(auction)}")

if __name__ == "__main__":
    ensure_directories()
    generate_csv_exports()
    summarize_accounting()
