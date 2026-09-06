import json

with open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31_Rebuilt.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('--- Suspicious Receipts ---')
for r in data.get('cashbook', []):
    code = str(r.get('F', '')).strip().upper()
    cash = float(str(r.get('H', '0')).replace(',', '') or '0')
    bank = float(str(r.get('I', '0')).replace(',', '') or '0')
    if (cash + bank) > 0 and (code.startswith('RP-1') or code.startswith('RP-8')):
        print(f"Doc: {r.get('B')}, Head: {r.get('E')}, Code: {code}, Amt: {cash+bank}")

print('--- Suspicious Payments ---')
for r in data.get('cashbook', []):
    code = str(r.get('N', '')).strip().upper()
    cash = float(str(r.get('P', '0')).replace(',', '') or '0')
    bank = float(str(r.get('Q', '0')).replace(',', '') or '0')
    if (cash + bank) > 0 and (code.startswith('RP-2') or code.startswith('RP-3') or code.startswith('RP-10') or code.startswith('RP-19')):
        print(f"Doc: {r.get('B')}, Head: {r.get('M')}, Code: {code}, Amt: {cash+bank}")
