import json
import re

with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

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

ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,\s*members', text, re.DOTALL)
if not ind_match:
    ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,', text, re.DOTALL)
ind_text = ind_match.group(1) if ind_match else ""
raw_ind = re.findall(r'\{[^{}]*\}', ind_text, re.DOTALL)

ind_rows = []
for ro in raw_ind:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        ind_rows.append(json.loads(q))
    except:
        pass

print(f"Total cashbook rows: {len(cb_entries)}")
print(f"Total individual rows: {len(ind_rows)}")

# Let's inspect non-members (NM) in cashbook vs members
nm_entries = []
for r in cb_entries:
    reg = str(r.get('C', '') or '').strip()
    if reg.upper() in ['NM', 'NON MEMBER', 'NON-MEMBER', ''] or 'NM' in reg.upper():
        nm_entries.append(r)

print(f"Total Non-Member (NM) receipts in Cashbook: {len(nm_entries)}")

