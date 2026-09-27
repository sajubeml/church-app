import json
import re

# Load JSON backup St_Gregorios_Church_Backup_Fixed_From_XLSM.json which contains the EXACT static Excel sheet grid!
with open('c:\\CASHBOOK_APP\\St_Gregorios_Church_Backup_Fixed_From_XLSM.json', 'r', encoding='utf-8') as f:
    xl_backup = json.load(f)

# Load data.js which feeds the web app
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

# Compute dynamic Catholicate total per Reg No from Cashbook
cb_cath_by_reg = {}
for r in cb_entries:
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
        cb_cath_by_reg[reg] = cb_cath_by_reg.get(reg, 0) + amt

# Now get static Excel row values from xl_backup['individual']
ind_rows = xl_backup.get('individual', [])
cath_col = 'G' # Catholicate Day & Recessa in row 3 of xl_backup['individual']

print("=== COMPLETE AUDIT: EXCEL STATIC vs CASHBOOK DYNAMIC (CATHOLICATE) ===")
print(f"{'Sl':<3} | {'Reg':<5} | {'Member Name':<30} | {'Excel Static':<12} | {'Cashbook Dynamic':<16} | {'Difference':<10}")
print("-" * 88)

excel_total = 0
cb_grand_total = sum(cb_cath_by_reg.values())

for idx in range(4, len(ind_rows)):
    r = ind_rows[idx]
    sl = str(r.get('A', '') or '').strip()
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    
    if not reg and not name:
        continue
        
    val_str = str(r.get(cath_col, '') or '').replace(',', '').strip()
    try:
        ex_val = float(val_str)
    except:
        ex_val = 0
        
    excel_total += ex_val
    cb_val = cb_cath_by_reg.get(reg, 0)
    
    diff = ex_val - cb_val
    if diff != 0 or ex_val > 0 or cb_val > 0:
        flag = " *** DIFF ***" if diff != 0 else ""
        print(f"{sl:<3} | {reg:<5} | {name:<30} | {ex_val:<12.2f} | {cb_val:<16.2f} | {diff:<10.2f}{flag}")

print("-" * 88)
print(f"EXCEL GRAND TOTAL: {excel_total:.2f}")
print(f"CASHBOOK DYNAMIC GRAND TOTAL: {cb_grand_total:.2f}")
print(f"TOTAL NET DIFFERENCE: {excel_total - cb_grand_total:.2f}")

