import json
import re

# Load data.js
with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract cashbook
cb_match = re.search(r'cashbook\s*:\s*\[(.*?)\]\s*,\s*individual', text, re.DOTALL)
cb_text = cb_match.group(1) if cb_match else ""
raw_cb = re.findall(r'\{[^{}]*\}', cb_text, re.DOTALL)

cb_entries = []
for ro in raw_cb:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        cb_entries.append(json.loads(q))
    except:
        pass

# Extract static individual array from data.js
ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,\s*members', text, re.DOTALL)
if not ind_match:
    ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,', text, re.DOTALL)
ind_text = ind_match.group(1)
raw_ind = re.findall(r'\{[^{}]*\}', ind_text, re.DOTALL)

ind_rows = []
for ro in raw_ind:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        ind_rows.append(json.loads(q))
    except:
        pass

header_row = ind_rows[3] if len(ind_rows) > 3 else {}
print("Header columns in data.js:")
for k, v in header_row.items():
    print(f"  Col {k}: {v}")

# Sum static values across all columns for member rows (index 4 to len-1)
col_static_sums = {}
total_static_grand = 0

for r in ind_rows[4:]:
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL':
        continue
    row_sum = 0
    for k, col_name in header_row.items():
        if k in ['A', 'B', 'C', 'D']: continue # skip sl, reg, name, sub_upto
        val_str = str(r.get(k, '') or '').replace(',', '').strip()
        try:
            val = float(val_str)
        except:
            val = 0
        if val > 0:
            col_static_sums[k] = col_static_sums.get(k, 0) + val
            row_sum += val
    total_static_grand += row_sum

print(f"\nTotal Static Individual Sum in data.js (excluding GRAND TOTAL row): {total_static_grand}")

# Also let's check static GRAND TOTAL row if present
for r in ind_rows[4:]:
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL':
        print("\nStatic GRAND TOTAL Row in data.js:")
        for k, v in r.items():
            col_name = header_row.get(k, k)
            print(f"  Col {k} ({col_name}): {v}")

