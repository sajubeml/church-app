import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data_export/Individual.json', 'r', encoding='utf-8') as f:
    indiv = json.load(f)

print("=== CHECKING ROW MATH FOR ALL ROWS IN INDIVIDUAL.JSON ===")
cols_list = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL']

total_mismatches = 0
for idx, row in enumerate(indiv):
    row_num = None
    reg = None
    name = None
    for k, v in row.items():
        if k.startswith('B') and k[1:].isdigit():
            reg = str(v or '').strip()
            row_num = k[1:]
            break
        if k.startswith('C') and k[1:].isdigit():
            name = str(v or '').strip()

    if not row_num or reg in ['Register No.', None, 'None'] or name in ['GRAND TOTAL', 'None']:
        continue

    row_name = str(row.get(f'C{row_num}', '') or '')
    col_am = float(row.get(f'AM{row_num}', 0) or 0)

    items_sum = 0.0
    non_zero_items = []
    for c in cols_list:
        val_str = row.get(f'{c}{row_num}', '0') or '0'
        try:
            val = float(val_str)
        except ValueError:
            val = 0.0
        if val != 0:
            non_zero_items.append((c, val))
        items_sum += val

    diff = abs(items_sum - col_am)
    if diff > 0.01:
        total_mismatches += 1
        print(f"Row {row_num:<3} | Sl.No {row.get('A'+row_num, '-'):<3} | Reg #{reg:<4} | Name: {row_name:<25}")
        print(f"   Calculated Sum of Cols (E..AL): ₹ {items_sum:,.2f}")
        print(f"   Stored GRAND TOTAL (Col AM):    ₹ {col_am:,.2f}")
        print(f"   Difference:                     ₹ {col_am - items_sum:,.2f}")
        print(f"   Non-zero columns: {non_zero_items}")
        print("-" * 75)

print(f"\nTotal Mismatched Rows Found: {total_mismatches}")
