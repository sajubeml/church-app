import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
data_export_dir = os.path.join(base_dir, "data_export")

# 1. Load full datasets
members = json.load(open(os.path.join(data_export_dir, "Members.json"), "r", encoding="utf-8")) if os.path.exists(os.path.join(data_export_dir, "Members.json")) else []
codes = json.load(open(os.path.join(data_export_dir, "Codes.json"), "r", encoding="utf-8")) if os.path.exists(os.path.join(data_export_dir, "Codes.json")) else []
trial_balance = json.load(open(os.path.join(data_export_dir, "Trial_Balance.json"), "r", encoding="utf-8")) if os.path.exists(os.path.join(data_export_dir, "Trial_Balance.json")) else []

# 2. Reset Cashbook entries to empty array (or title header only)
empty_cashbook = []

# 3. Create zeroed individual member roster
zero_individual = []
if os.path.exists(os.path.join(data_export_dir, "Individual.json")):
    ind_data = json.load(open(os.path.join(data_export_dir, "Individual.json"), "r", encoding="utf-8"))
    for idx, row in enumerate(ind_data):
        if idx < 4:
            zero_individual.append(row) # Keep row headers
        else:
            # Keep Reg No and Name, zero out contribution columns
            new_row = {}
            for k, v in row.items():
                col_letter = "".join([c for c in k if c.isalpha()]).upper()
                if col_letter in ["A", "B", "C", "D"]:
                    new_row[k] = v
                else:
                    new_row[k] = ""
            zero_individual.append(new_row)

js_content = f"""// St. Gregorios Church Accounting - Fresh Start Dataset (7-Day Trial)
window.isFreshStartBuild = true;

window.INITIAL_MEMBERS = {json.dumps(members, indent=2)};
window.INITIAL_CASHBOOK = {json.dumps(empty_cashbook, indent=2)};
window.INITIAL_INDIVIDUAL = {json.dumps(zero_individual, indent=2)};
window.INITIAL_TRIAL_BALANCE = {json.dumps(trial_balance, indent=2)};
window.INITIAL_CODES = {json.dumps(codes, indent=2)};
"""

target_js = os.path.join(base_dir, "data_fresh.js")
with open(target_js, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"[OK] Generated Fresh Start bundle data_fresh.js ({os.path.getsize(target_js) / 1024:.2f} KB) successfully!")
