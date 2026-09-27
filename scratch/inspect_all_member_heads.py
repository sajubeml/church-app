import re
import json

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

header_row = ind_rows[3] if len(ind_rows) > 3 else {}

# Map cashbook entries dynamically per Reg No for all account heads
member_contributions = {}

# Initialize all members from individual array
for r in ind_rows[4:]:
    sl = str(r.get('A', '') or '').strip()
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    sub_upto = str(r.get('D', '') or '').strip()
    if not reg and not name: continue
    if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL': continue
    if reg not in member_contributions:
        member_contributions[reg] = {
            'sl': sl,
            'reg': reg,
            'name': name,
            'sub_upto': sub_upto,
            'heads': {},
            'total': 0
        }

# Also check static individual cells for every head column
for r in ind_rows[4:]:
    reg = str(r.get('B', '') or '').strip()
    if reg in member_contributions:
        m = member_contributions[reg]
        for k, h_name in header_row.items():
            if k in ['A', 'B', 'C', 'D', 'AM']: continue
            val_str = str(r.get(k, '') or '').replace(',', '').strip()
            try: val = float(val_str)
            except: val = 0
            if val > 0:
                m['heads'][h_name] = m['heads'].get(h_name, 0) + val

for reg, m in member_contributions.items():
    m['total'] = sum(m['heads'].values())

print(f"Total registered members found: {len(member_contributions)}")
members_with_contrib = [m for m in member_contributions.values() if m['total'] > 0]
print(f"Members with non-zero contributions: {len(members_with_contrib)}")
print(f"Grand Total across all registered members: {sum(m['total'] for m in member_contributions.values()):,.2f}")

