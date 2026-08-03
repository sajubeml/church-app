import json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

cb_path = os.path.join('data_export', 'Cash_Book.json')
indiv_path = os.path.join('data_export', 'Individual.json')
backup_path = os.path.join(os.environ.get('USERPROFILE', r'C:\Users\sajub'), 'Downloads', 'St_Gregorios_Church_Backup_2026-07-27.json')

# 1. Update Cash_Book.json
with open(cb_path, 'r', encoding='utf-8') as f:
    cashbook = json.load(f)

for row in cashbook:
    c_val = str(row.get('C', '') or '').strip()
    if c_val == '150' and row.get('B') == '4275':
        if row.get('H'):
            row['H'] = '30000'
        if row.get('I'):
            row['I'] = '30000'
        print(f"Updated Cash Book Receipt #4275 for Reg #150 to ₹ 30,000: {row}")

with open(cb_path, 'w', encoding='utf-8') as f:
    json.dump(cashbook, f, indent=2, ensure_ascii=False)

# 2. Update Individual.json
with open(indiv_path, 'r', encoding='utf-8') as f:
    indiv = json.load(f)

santhosh_row = indiv[90] # Index 90
santhosh_row['F92'] = '30000'
santhosh_row['AM92'] = '34300'
print(f"Updated Individual Sheet Row 90 (Reg #150): F92 = 30000, AM92 = 34300")

# Recalculate Grand Totals for Row 115 (Row 117 in sheet)
gt_row = indiv[115] # Row with C117 = 'GRAND TOTAL'
cols_list = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM']

col_totals = {c: 0.0 for c in cols_list}

for idx, r in enumerate(indiv):
    if idx == 115: # Skip Grand Total row itself
        continue
    
    row_num = None
    for k in r.keys():
        if k[1:].isdigit():
            row_num = k[1:]
            break
    
    if not row_num:
        continue
        
    for c in cols_list:
        key = f"{c}{row_num}"
        val_str = r.get(key)
        if val_str and val_str not in ['None', 'GRAND TOTAL']:
            try:
                col_totals[c] += float(val_str)
            except ValueError:
                pass

print("\nRecalculated GRAND TOTAL row for Individual.json:")
for c in cols_list:
    key = f"{c}117"
    new_val_str = str(int(col_totals[c])) if col_totals[c].is_integer() else f"{col_totals[c]:.2f}"
    gt_row[key] = new_val_str
    print(f"  Col {c} ({key}): {new_val_str}")

with open(indiv_path, 'w', encoding='utf-8') as f:
    json.dump(indiv, f, indent=2, ensure_ascii=False)

# 3. Update Downloads backup file
if os.path.exists(backup_path):
    with open(backup_path, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    if 'cashbook' in backup_data:
        for row in backup_data['cashbook']:
            c_val = str(row.get('C', '') or '').strip()
            if c_val == '150' and row.get('B') == '4275':
                if row.get('H'): row['H'] = '30000'
                if row.get('I'): row['I'] = '30000'

    if 'individual' in backup_data:
        for r in backup_data['individual']:
            if 'B92' in r and r['B92'] == '150':
                r['F92'] = '30000'
                r['AM92'] = '34300'
        # Update Grand Total in backup
        gt_b = None
        for r in backup_data['individual']:
            if 'C117' in r and r['C117'] == 'GRAND TOTAL':
                gt_b = r
                break
        if gt_b:
            for c in cols_list:
                key = f"{c}117"
                gt_b[key] = gt_row[key]

    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    print(f"\nUpdated Downloads backup file: {backup_path}")

