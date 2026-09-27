import json
import re

# Let's inspect data.js and backup json
with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's extract static individual array from data.js
ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,\s*members', text, re.DOTALL)
if not ind_match:
    ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,', text, re.DOTALL)

ind_text = ind_match.group(1) if ind_match else ""

# Extract JSON array
raw_objs = re.findall(r'\{[^{}]*\}', ind_text, re.DOTALL)
ind_rows = []
for ro in raw_objs:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        ind_rows.append(json.loads(q))
    except:
        pass

print(f"Parsed {len(ind_rows)} rows from data.js individual array")

# Find Catholicate column key in row 3
cath_col = None
if len(ind_rows) > 3:
    for k, v in ind_rows[3].items():
        if v and 'catholicate' in str(v).lower():
            cath_col = k
            print(f"Catholicate column in data.js static individual: {k} -> {v}")

static_by_reg = {}
static_total = 0
for r in ind_rows[4:]:
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    val_str = str(r.get(cath_col, '') or '').replace(',', '').strip()
    try:
        val = float(val_str)
    except:
        val = 0
    if val > 0:
        static_by_reg[reg] = {'name': name, 'static_val': val}
        static_total += val

print(f"Static Catholicate sum in data.js individual array: {static_total}")

# Now extract cashbook entries from data.js
cb_match = re.search(r'cashbook\s*:\s*\[(.*?)\]\s*,\s*individual', text, re.DOTALL)
cb_text = cb_match.group(1) if cb_match else ""
raw_cb = re.findall(r'\{[^{}]*\}', cb_text, re.DOTALL)

cb_by_reg = {}
cb_total = 0
cb_all = []

for ro in raw_cb:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        r = json.loads(q)
        head = str(r.get('E', '') or '').strip()
        code = str(r.get('F', '') or '').strip()
        rem = str(r.get('G', '') or '').strip()
        amt_str = r.get('H') or r.get('I') or '0'
        try:
            amt = float(str(amt_str).replace(',', '').strip() or 0)
        except:
            amt = 0
        if 'catholicate' in head.lower() or 'catholicate' in code.lower() or 'catholicate' in rem.lower() or 'RP-10.04' in code or 'RP-10.05' in code:
            reg = str(r.get('C', '') or '').strip()
            name = str(r.get('D', '') or '').strip()
            rec = str(r.get('B', '') or '').strip()
            cb_total += amt
            cb_by_reg[reg] = cb_by_reg.get(reg, 0) + amt
            cb_all.append({'rec': rec, 'reg': reg, 'name': name, 'head': head, 'code': code, 'amt': amt, 'rem': rem})
    except:
        pass

print(f"Dynamic Cashbook Catholicate sum in data.js: {cb_total}")

print("\n--- COMPARISON OF STATIC INDIVIDUAL LEDGER (EXCEL DRAFT) vs DYNAMIC CASHBOOK ---")
all_regs = sorted(list(set(list(static_by_reg.keys()) + list(cb_by_reg.keys()))), key=lambda x: str(x))
for reg in all_regs:
    stat = static_by_reg.get(reg, {}).get('static_val', 0)
    cb = cb_by_reg.get(reg, 0)
    name = static_by_reg.get(reg, {}).get('name', '')
    if not name:
        # find in cb_all
        for c in cb_all:
            if c['reg'] == reg:
                name = c['name']
                break
    if stat != cb:
        print(f"Reg #{reg:<5} | Name: {name:<25} | Static (Excel): {stat:>6} | Dynamic (Cashbook): {cb:>6} | Diff: {stat - cb:>6}")

