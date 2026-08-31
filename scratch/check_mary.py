import json
data = json.load(open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json', 'r', encoding='utf-8'))

print("=== Mary Mathew (Reg 65) Cashbook Entries for Donation-Breakfast ===")
for row in data['cashbook']:
    reg = str(row.get('C', '')).strip()
    head = str(row.get('E', '')).strip()
    code = str(row.get('F', '')).strip()
    if reg == '65' and ('breakfast' in head.lower() or code == 'RP-2.16'):
        dt = str(row.get('A', '')).strip()
        cashR = float(row.get('H', 0) or 0)
        bankR = float(row.get('I', 0) or 0)
        print(f"  Date={dt} Head={head} Code={code} Cash={cashR} Bank={bankR}")

print("\n=== Individual Ledger for Reg 65 ===")
for i, row in enumerate(data['individual']):
    if i < 4: continue
    if str(row.get('B', '')).strip() == '65':
        for k in sorted(row.keys(), key=lambda x: (len(x), x)):
            v = row.get(k, '')
            if v and str(v).strip() and str(v).strip() != '0':
                print(f"  {k}: {v}")

# Also check what new cashbook entries exist in Aug 31 that weren't in Aug 30
print("\n\n=== New cashbook entries (Donation-Breakfast with AK mapping) ===")
for row in data['cashbook']:
    head = str(row.get('E', '')).strip()
    code = str(row.get('F', '')).strip()
    if 'breakfast' in head.lower() or code == 'RP-2.16':
        reg = str(row.get('C', '')).strip()
        hof = str(row.get('D', '')).strip()
        dt = str(row.get('A', '')).strip()
        cashR = float(row.get('H', 0) or 0)
        bankR = float(row.get('I', 0) or 0)
        total = cashR + bankR
        if total > 0:
            print(f"  Reg#{reg} {hof}: Date={dt} Total={total} Code={code}")
