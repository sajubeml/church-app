import json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

backup_path = os.path.join(os.environ.get('USERPROFILE', r'C:\Users\sajub'), 'Downloads', 'St_Gregorios_Church_Backup_2026-07-27.json')

if os.path.exists(backup_path):
    with open(backup_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'individual' in data:
        indiv = data['individual']
        # Update Santhosh K. A.
        for r in indiv:
            if 'B92' in r and r['B92'] == '150':
                r['F92'] = '10000'
                r['AM92'] = '14300'
                print("Updated Santhosh K. A. in Downloads backup!")
            if 'C5' in r and r['C5'] == 'john AM':
                r['F5'] = '2360'
                r['AM5'] = '2360'
                if 'F' in r: del r['F']
                print("Updated john AM in Downloads backup!")

        # Recalculate Grand Total row in backup
        gt_row = None
        for r in indiv:
            if 'C117' in r and r['C117'] == 'GRAND TOTAL':
                gt_row = r
                break

        if gt_row:
            cols_list = ['E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM']
            col_totals = {c: 0.0 for c in cols_list}

            for r in indiv:
                if 'C117' in r: continue
                row_num = None
                for k in r.keys():
                    if k[1:].isdigit():
                        row_num = k[1:]
                        break
                if not row_num: continue
                for c in cols_list:
                    key = f"{c}{row_num}"
                    val_str = r.get(key)
                    if val_str and val_str not in ['None', 'GRAND TOTAL']:
                        try: col_totals[c] += float(val_str)
                        except ValueError: pass

            for c in cols_list:
                key = f"{c}117"
                new_val_str = str(int(col_totals[c])) if col_totals[c].is_integer() else f"{col_totals[c]:.2f}"
                gt_row[key] = new_val_str

            print("Recalculated GRAND TOTAL row in Downloads backup!")

        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved updated backup file at {backup_path}")
