import json
import os
import glob

def check_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cashbook = data.get('cashbook', [])
        individual = data.get('individual', [])
        
        cb_total = 0
        cb_count = 0
        cb_items = []
        for idx, r in enumerate(cashbook):
            head = str(r.get('E', '') or '').strip()
            code = str(r.get('F', '') or '').strip()
            amt_str = r.get('H') or r.get('I') or '0'
            try:
                amt = float(str(amt_str).replace(',', '').strip() or 0)
            except:
                amt = 0
            if 'catholicate' in head.lower() or 'catholicate' in code.lower() or 'RP-10.04' in code or 'RP-10.05' in code:
                cb_total += amt
                cb_count += 1
                cb_items.append({
                    'rec_no': r.get('B'),
                    'reg_no': r.get('C'),
                    'name': r.get('D'),
                    'amt': amt,
                    'code': code,
                    'head': head
                })
        
        # Check static individual ledger values if present (e.g. Col G or wherever Catholicate is in row 3)
        ind_col = None
        if len(individual) > 3:
            header = individual[3]
            for k, v in header.items():
                if v and 'catholicate' in str(v).lower():
                    ind_col = k
                    break
        
        ind_static_sum = 0
        if ind_col:
            for row in individual[4:]:
                val = str(row.get(ind_col, '') or '').replace(',', '').strip()
                try:
                    ind_static_sum += float(val)
                except:
                    pass

        print(f"\nFile: {filepath}")
        print(f"  Cashbook Total: {cb_total} (Entries: {cb_count})")
        print(f"  Individual Ledger Static Sum (Col {ind_col}): {ind_static_sum}")
        return data, cb_items
    except Exception as e:
        print(f"\nFile {filepath} error: {e}")
        return None, []

files = [
    'c:\\CASHBOOK_APP\\St_Gregorios_Church_Backup_Fixed_From_XLSM.json',
    'c:\\CASHBOOK_APP\\St_Gregorios_Church_Backup_2026-08-14 (1).json',
    'c:\\CASHBOOK_APP\\fixed_final_cashbook_23000.json'
]

for f in files:
    check_json(f)
