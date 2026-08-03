import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data_export/Individual.json', 'r', encoding='utf-8') as f:
    indiv = json.load(f)

# Inspect Reg #150, Reg #51, Reg #169, Reg #52, Reg #8 in detail
target_regs = ['150', '51', '169', '52', '8']

for idx, row in enumerate(indiv):
    reg = None
    row_num = None
    for k, v in row.items():
        if k.startswith('B') and k[1:].isdigit():
            reg = str(v or '').strip()
            row_num = k[1:]
            break
    if reg in target_regs:
        print(f"\n==========================================")
        print(f"Row {row_num}: Reg #{reg} - {row.get('C' + str(row_num))}")
        print("==========================================")
        non_zero = {}
        for k, v in row.items():
            if v and v != '0' and v != '0.00' and v != 'None':
                non_zero[k] = v
        print(non_zero)
