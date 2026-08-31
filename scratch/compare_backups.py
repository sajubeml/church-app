import json

# Load BOTH backups to compare
aug30 = json.load(open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-30 (5).json', 'r', encoding='utf-8'))
aug31 = json.load(open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json', 'r', encoding='utf-8'))

# Check Mary Mathew (Reg 65) in BOTH backups
print("=== Mary Mathew (Reg 65) Individual Ledger ===")
print("\nAug 30 backup:")
for i, row in enumerate(aug30['individual']):
    if i < 4: continue
    if str(row.get('B', '')).strip() == '65':
        for k in sorted(row.keys(), key=lambda x: (len(x), x)):
            v = row.get(k, '')
            if v and str(v).strip() and str(v).strip() != '0':
                print(f"  {k}: {v}")

print("\nAug 31 backup:")
for i, row in enumerate(aug31['individual']):
    if i < 4: continue
    if str(row.get('B', '')).strip() == '65':
        for k in sorted(row.keys(), key=lambda x: (len(x), x)):
            v = row.get(k, '')
            if v and str(v).strip() and str(v).strip() != '0':
                print(f"  {k}: {v}")

# Check: did Aug 31 backup individual ledger actually change from Aug 30?
print("\n\n=== Did individual ledger change between Aug 30 and Aug 31? ===")
changed_members = 0
for i in range(4, min(len(aug30['individual']), len(aug31['individual']))):
    r30 = aug30['individual'][i]
    r31 = aug31['individual'][i]
    c30 = str(r30.get('C', '')).strip()
    c31 = str(r31.get('C', '')).strip()
    if 'GRAND TOTAL' in c30.upper(): continue
    
    am30 = float(str(r30.get('AM', '0')).replace(',', '') or '0')
    am31 = float(str(r31.get('AM', '0')).replace(',', '') or '0')
    
    if abs(am30 - am31) > 0.01:
        reg = str(r31.get('B', '')).strip()
        print(f"  Reg#{reg} {c31}: AM changed from {am30} to {am31} (diff={am31-am30:+.0f})")
        changed_members += 1

if changed_members == 0:
    print("  NO CHANGES in any member's GRAND TOTAL between the two backups!")

# Count cashbook entries
print(f"\n\nAug 30 cashbook entries: {len(aug30['cashbook'])}")
print(f"Aug 31 cashbook entries: {len(aug31['cashbook'])}")

# Find new entries in Aug 31
new_entries = len(aug31['cashbook']) - len(aug30['cashbook'])
print(f"New entries added: {new_entries}")

if new_entries > 0:
    print("\nNew entries:")
    for row in aug31['cashbook'][-new_entries:]:
        recNo = str(row.get('B', '')).strip()
        head = str(row.get('E', '')).strip()
        reg = str(row.get('C', '')).strip()
        hof = str(row.get('D', '')).strip()
        cashR = float(row.get('H', 0) or 0)
        bankR = float(row.get('I', 0) or 0)
        dt = str(row.get('A', '')).strip()
        print(f"  #{recNo} Reg#{reg} {hof}: {head} Cash={cashR} Bank={bankR} Date={dt}")

# KEY CHECK: Did the Aug 30 FIXED backup (the one we recalculated) get used?
# Or did the user take a fresh backup from the offline app?
print("\n\n=== Header row comparison ===")
h30 = str(aug30['individual'][2].get('A', ''))
h31 = str(aug31['individual'][2].get('A', ''))
print(f"Aug 30 header: {h30}")
print(f"Aug 31 header: {h31}")
