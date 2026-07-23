"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Build data.js Script (Python Native)
Replaces build_data_js.ps1
"""

import os
import json

OUTPUT_FILE = "data.js"
EXPORT_DIR = "data_export"

def read_json_raw(filename):
    path = os.path.join(EXPORT_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "[]"

def build_data_js():
    print("Packaging exported JSON data into data.js...")
    
    cb = read_json_raw("Cash_Book.json")
    ind = read_json_raw("Individual.json")
    tb = read_json_raw("Trial_Balance.json")
    mem = read_json_raw("Members.json")
    bud = read_json_raw("Budget.json")
    cod = read_json_raw("Codes.json")
    auc = read_json_raw("aution25.json")

    js_content = f"""/**
 * Embedded Church Accounting Database
 * Auto-generated for direct file:// and http:// support.
 */
window.CHURCH_DATA = {{
  cashbook: {cb},
  individual: {ind},
  trialBalance: {tb},
  members: {mem},
  budget: {bud},
  codes: {cod},
  auction: {auc}
}};
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024.0
    print(f"[OK] Created data.js ({size_kb:.2f} KB) successfully!")

if __name__ == "__main__":
    build_data_js()
