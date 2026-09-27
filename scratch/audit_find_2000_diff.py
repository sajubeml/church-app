import json
import re

# Load JSON backup file St_Gregorios_Church_Backup_Fixed_From_XLSM.json
with open('c:\\CASHBOOK_APP\\St_Gregorios_Church_Backup_Fixed_From_XLSM.json', 'r', encoding='utf-8') as f:
    xlsm_backup = json.load(f)

# Load JSON backup file St_Gregorios_Church_Backup_2026-08-14 (1).json
with open('c:\\CASHBOOK_APP\\St_Gregorios_Church_Backup_2026-08-14 (1).json', 'r', encoding='utf-8') as f:
    aug_backup = json.load(f)

print("=== STATIC INDIVIDUAL LEDGER IN XLSM BACKUP ===")
ind_xlsm = xlsm_backup.get('individual', [])
ind_col_xlsm = None
if len(ind_xlsm) > 3:
    for k, v in ind_xlsm[3].items():
        if v and 'catholicate' in str(v).lower():
            ind_col_xlsm = k

sum_xlsm_static = 0
xlsm_member_static = {}
for row in ind_xlsm[4:]:
    reg = str(row.get('B', '') or '').strip()
    name = str(row.get('C', '') or '').strip()
    val_str = str(row.get(ind_col_xlsm, '') or '').replace(',', '').strip()
    try:
        val = float(val_str)
    except:
        val = 0
    if val > 0:
        xlsm_member_static[reg or name] = (reg, name, val)
        sum_xlsm_static += val

print(f"Static Individual Ledger Catholicate Sum in XLSM Backup: {sum_xlsm_static}")

# Now let's calculate Cashbook total for Catholicate in xlsm_backup
cb_xlsm = xlsm_backup.get('cashbook', [])
cb_xlsm_by_reg = {}
cb_xlsm_total = 0
cb_xlsm_all_matching = []

for idx, r in enumerate(cb_xlsm):
    head = str(r.get('E', '') or '').strip()
    code = str(r.get('F', '') or '').strip()
    rem = str(r.get('G', '') or '').strip()
    amt_str = r.get('H') or r.get('I') or '0'
    try:
        amt = float(str(amt_str).replace(',', '').strip() or 0)
    except:
        amt = 0
    
    # Check if this entry is Catholicate
    if 'catholicate' in head.lower() or 'catholicate' in code.lower() or 'catholicate' in rem.lower() or 'RP-10.04' in code or 'RP-10.05' in code or 'recessa' in head.lower() or 'recessa' in rem.lower():
        reg = str(r.get('C', '') or '').strip()
        cb_xlsm_total += amt
        cb_xlsm_by_reg[reg] = cb_xlsm_by_reg.get(reg, 0) + amt
        cb_xlsm_all_matching.append((idx, r.get('B'), reg, r.get('D'), head, code, rem, amt))

print(f"Dynamic Cashbook Catholicate Total in XLSM Backup: {cb_xlsm_total}")
print(f"Difference between XLSM Static Ledger ({sum_xlsm_static}) and Dynamic Cashbook ({cb_xlsm_total}): {sum_xlsm_static - cb_xlsm_total}")

print("\n--- MEMBERS DISCREPANCY BETWEEN STATIC LEDGER AND DYNAMIC CASHBOOK ---")
all_regs = set(list(xlsm_member_static.keys()) + list(cb_xlsm_by_reg.keys()))
for reg in sorted(all_regs, key=lambda x: str(x)):
    stat_val = xlsm_member_static.get(reg, ('', '', 0))[2]
    cb_val = cb_xlsm_by_reg.get(reg, 0)
    if stat_val != cb_val:
        name = xlsm_member_static.get(reg, ('', 'Unknown', 0))[1]
        print(f"Reg #{reg:<5} | Name: {name:<25} | Static XLSM: {stat_val:>7} | Dynamic CB: {cb_val:>7} | Diff: {stat_val - cb_val:>7}")

