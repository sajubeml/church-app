import json

with open('c:\\CASHBOOK_APP\\St_Gregorios_Church_Backup_Fixed_From_XLSM.json', 'r', encoding='utf-8') as f:
    xl = json.load(f)

ind = xl['individual']
cath_col = 'G'

excel_members = {}
for r in ind[4:]:
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    val_str = str(r.get(cath_col, '') or '').replace(',', '').strip()
    try:
        val = float(val_str)
    except:
        val = 0
    if reg != 'GRAND TOTAL' and val > 0:
        excel_members[reg] = {'name': name, 'val': val}

print(f"Total non-zero Catholicate members in Excel backup: {len(excel_members)}")
print(f"Sum of these members: {sum(m['val'] for m in excel_members.values())}")
for reg, m in sorted(excel_members.items(), key=lambda x: str(x[0])):
    print(f"Reg #{reg:<5} | Name: {m['name']:<30} | Excel Val: {m['val']}")

