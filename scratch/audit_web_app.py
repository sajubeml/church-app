import json

d = json.load(open('c:/Users/sajub/Downloads/St_Gregorios_Church_Backup_2026-08-31.json', encoding='utf-8'))
header = d['individual'][3]

totals = {}
for row in d['individual'][4:]:
    for k, v in row.items():
        if len(k) <= 2 and k not in ['A', 'B', 'C', 'D', 'AM']:
            try:
                val = float(str(v).replace(',', '')) if str(v).replace(',', '') else 0
                totals[k] = totals.get(k, 0) + val
            except ValueError:
                pass

for k in sorted(totals.keys(), key=lambda x: (len(x), x)):
    if totals[k] > 0:
        print(f"{k} - {header.get(k, 'UNKNOWN')}: {totals[k]}")
