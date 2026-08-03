import json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

indiv_path = os.path.join('data_export', 'Individual.json')

with open(indiv_path, 'r', encoding='utf-8') as f:
    indiv = json.load(f)

# 1. Update Santhosh K. A. (index 90, Row 92)
santhosh_row = indiv[90]
santhosh_row['F92'] = '10000'
santhosh_row['AM92'] = '14300'
print("Updated Santhosh K. A. (Reg #150): F92 = 10000, AM92 = 14300")

# 2. Update john AM (index 116, Row 5)
john_row = indiv[116]
john_row['F5'] = '2360'
john_row['AM5'] = '2360'
if 'F' in john_row:
    del john_row['F']
print("Updated john AM (Reg #51): F5 = 2360, AM5 = 2360")

# 3. Recalculate Grand Totals for Row 115 (Row 117 in sheet)
gt_row = indiv[115] # Row with C117 = 'GRAND TOTAL'
cols_list = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM']

col_totals = {c: 0.0 for c in cols_list}

for idx, r in enumerate(indiv):
    if idx == 115: # Skip Grand Total row itself
        continue
    
    # Identify row number for keys
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

print("\nRecalculated Column Totals for GRAND TOTAL Row:")
for c in cols_list:
    key = f"{c}117"
    new_val_str = str(int(col_totals[c])) if col_totals[c].is_integer() else f"{col_totals[c]:.2f}"
    gt_row[key] = new_val_str
    print(f"  Col {c} ({key}): {new_val_str}")

# Save Individual.json
with open(indiv_path, 'w', encoding='utf-8') as f:
    json.dump(indiv, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully saved updated {indiv_path}")
