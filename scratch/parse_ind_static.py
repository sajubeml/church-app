import json
import re

with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,\s*members', text, re.DOTALL)
if not ind_match:
    ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,', text, re.DOTALL)

ind_text = ind_match.group(1)
raw_objs = re.findall(r'\{[^{}]*\}', ind_text, re.DOTALL)

ind_rows = []
for ro in raw_objs:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        ind_rows.append(json.loads(q))
    except:
        pass

cath_col = 'G' # Catholicate Day & Recessa

print(f"{'Row':<5} | {'Reg':<6} | {'Name':<30} | {'Static G':<10}")
print("-" * 60)

for idx, r in enumerate(ind_rows):
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    val = str(r.get(cath_col, '') or '').strip()
    if val and val != '-' and val != '0':
        print(f"{idx:<5} | {reg:<6} | {name:<30} | {val:<10}")

