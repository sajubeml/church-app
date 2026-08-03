"""
St. Gregorios Orthodox Syrian Church, Mysuru
--------------------------------------------
Build data.js Script (Python Native)
Automatically incorporates backup JSON snapshots from Downloads / Root
"""

import os
import glob
import json

OUTPUT_FILE = "data.js"
EXPORT_DIR = "data_export"

def check_and_sync_latest_backups():
    user_profile = os.environ.get("USERPROFILE", r"C:\Users\sajub")
    search_dirs = [
        r"c:\saju_old pc\Church_App\anti_gravity",
        os.path.join(user_profile, "Downloads")
    ]
    
    latest_backup_file = None
    latest_mtime = 0

    for d in search_dirs:
        if not os.path.exists(d): continue
        for pattern in ["*Backup*.json", "*backup*.json", "*Church*.json"]:
            for fpath in glob.glob(os.path.join(d, pattern)):
                mtime = os.path.getmtime(fpath)
                if mtime > latest_mtime:
                    try:
                        with open(fpath, "r", encoding="utf-8") as bf:
                            data = json.load(bf)
                            if isinstance(data, dict) and "cashbook" in data and len(data["cashbook"]) > 0:
                                latest_mtime = mtime
                                latest_backup_file = (fpath, data)
                    except Exception:
                        pass

    if latest_backup_file:
        fpath, backup_data = latest_backup_file
        print(f"[SYNC] Ingested latest user local PC backup file: {os.path.basename(fpath)}")
        os.makedirs(EXPORT_DIR, exist_ok=True)
        if "cashbook" in backup_data and len(backup_data["cashbook"]) > 0:
            # Auto-sanitize sub-codes
            head_to_code = [
                ('local travelling allowance to vicar', 'RP-12.02 (d)'),
                ('telephone allowance to vicar', 'RP-12.02 (c)'),
                ('medical allowance to vicar', 'RP-12.02 (a)'),
                ('medical allowance to sexton', 'RP-12.06'),
                ('annual travelling allowance to vicar', 'RP-12.02 (e)'),
                ('leave salary to vicar', 'RP-12.02 (f)'),
                ('gift purse to vicar', 'RP-12.02 (g)'),
                ('salary to watchman(cemetry)', 'RP-12.03 (b)'),
                ('salary to sexton', 'RP-12.03 (a)'),
                ('salary to ayah', 'RP-12.03 (c)'),
            ]
            for row in backup_data["cashbook"]:
                if not isinstance(row, dict): continue
                # Check for Cash Deposited / Contra entries
                p_head_val = str(row.get('M') or row.get('payments_account_head') or '').strip()
                p_code_val = str(row.get('N') or row.get('payments_code') or '').strip()
                p_det_val = str(row.get('O') or row.get('particulars') or '').strip()
                r_head_val = str(row.get('E') or row.get('receipt_account_head') or '').strip()
                r_code_val = str(row.get('F') or row.get('receipt_code') or '').strip()
                r_det_val = str(row.get('G') or row.get('particulars') or '').strip()
                comb_all = (p_head_val + ' ' + p_det_val + ' ' + p_code_val + ' ' + r_head_val + ' ' + r_det_val + ' ' + r_code_val).lower()

                if 'cash deposited' in comb_all or 'contra' in comb_all or 'cash to bank' in comb_all:
                    if (row.get('P') or row.get('payments_cash')) and (not p_head_val or p_head_val == '-' or not p_code_val or p_code_val == '-'):
                        if 'M' in row: row['M'] = "Excess Cash Deposited to Bank"
                        else: row['payments_account_head'] = "Excess Cash Deposited to Bank"
                        if 'N' in row: row['N'] = "CD"
                        else: row['payments_code'] = "CD"

                    if (row.get('I') or row.get('receipt_bank')) and (not r_head_val or r_head_val == '-' or not r_code_val or r_code_val == '-'):
                        if 'E' in row: row['E'] = "Excess Cash Deposited to Bank"
                        else: row['receipt_account_head'] = "Excess Cash Deposited to Bank"
                        if 'F' in row: row['F'] = "CD"
                        else: row['receipt_code'] = "CD"

            # Clean and normalize all cashbook titles to match exact Budget Sheet Account Head names
            budget_code_map = {
                'RP-1.01': 'Opening Balance - Cash',
                'RP-1.02': '- Bank',
                'RP-3.82': 'Monthly Subscription ( Current Year)',
                'RP-3.83': 'Monthly Subscription ( Pervious Year)',
                'RP-3.16': 'Birthday Offerings',
                'RP-3.17': 'Wedding Anniversary Offerings',
                'RP-3.12': 'Orma Qurbana/Holy Qurbana',
                'RP-3.17(A)': 'House Blessing',
                'RP-2.14': 'Marriage Bann',
                'RP-3.14': 'Baptism',
                'RP-2.19': 'Cemetry Receipt',
                'RP-3.61': 'Sunday School',
                'RP-3.66': 'OVBS',
                'RP-3.64': 'Kanika Prayer Group',
                'RP-3.52': 'Certificate Fee',
                'RP-2.02': 'Donation General',
                'RP-2.02(A)': 'Donation General-chair & tables',
                'RP-2.16': 'Donation-Breakfast',
                'RP-2.20': 'Donation- Others (Farewell)',
                'RP-2.211': 'KMDC Grant',
                'RP-3.03': 'Kurishinthothi &',
                'RP-3.04': 'Koodaram',
                'RP-3.05': 'Perunnal Vanchika (House Offertory Box)',
                'RP-3.10': 'Kanicka Church',
                'RP-3.13': 'Kanicka-Chapel',
                'RP-2.15(A)': 'Auction Dues - Old',
                'RP-2.15': 'Auction current',
                'RP-2.15(B)': 'Petty Auction',
                'RP-10.04/05': 'Catholicate Day & Recessa',
                'RP-10.04': 'Catholicate Day & Recessa',
                'RP-10.08': 'Metropolitan Fund',
                'RP-10.13': 'Mission Sunday',
                'RP-10.15': 'Seminary Day',
                'RP-10.10': 'Priest Welfare Fund',
                'RP-10.09': 'Marriage Kaimuthu',
                'RP-10.17': 'Old Cover Collection Dues',
                'RP-10.14': 'Sunday School Day Collection',
                'RP-10.16': 'Gerbo Sunday',
                'RP-3.35': 'St. George Feast',
                'RP-3.31': 'St. Thomas Feast',
                'RP-3.32': 'St. Mary\'s Feast',
                'RP-3.33': 'St.Gregorios Feast ( Annual Feast)',
                'RP-2.11': 'Christmas / New Year Collection',
                'RP-2.12': 'Parish Day/Harvest / Collection',
                'RP-2.13': 'Passion Week Collection',
                'RP-8.03': 'Interest Received SB Account',
                'RP-19.31': 'Salary Quota to Diocese(Vicar)',
                'RP-12.03(A)': 'Salary to Sexton',
                'RP-12.03(B)': 'Salary to Watchman(Cemetry)',
                'RP-12.03(C)': 'Salary to Ayah',
                'RP-12.02(A)': 'Medical Allowance to Vicar',
                'RP-12.06': 'Medical Allowance to Sexton',
                'RP-12.02(C)': 'Telephone Allowance to Vicar',
                'RP-12.02(D)': 'Local Travelling Allowance to Vicar',
                'RP-12.02(E)': 'Annual Travelling Allowance to Vicar',
                'RP-12.02(F)': 'Leave Salary to Vicar',
                'RP-12.02(G)': 'Gift Purse to Vicar',
                'RP-12.07': 'Kaimuthu to Thirumeni',
                'RP-12.07(A)': 'Kaimuthu to Visiting priest',
                'RP-16.04': 'Church Service Expense',
                'RP-16.11(A)': 'Electricity Charges - Church',
                'RP-16.11(B)': 'Electricity Charges - Parsonage',
                'RP-16.11(C)': 'Elecricity Charges - Cemetry',
                'RP-16.08': 'Breakfast Expenses',
                'RP-14.31(A)': 'Church Renovation Expenses',
                'RP-14.31': 'Maintenance of Church & Parsonage',
                'RP-16.06': 'Passion Week Expenses',
                'RP-14.35': 'Maintenance of Cemetry',
                'RP-14.05': 'Postage',
                'RP-16.35': 'Canteen Expenses',
                'RP-14.06': 'Printing & Stationery',
                'RP-16.36': 'Cemetry Development',
                'RP-16.87': 'Grant - Sneha Bhavan',
                'RP-16.89': 'Gift & Mementoes',
                'RP-16.62': 'Sunday School Expense',
                'RP-16.67': 'OVBS',
                'RP-16.65': 'Prayer Group',
                'RP-14.03': 'Travelling Expenses',
                'RP-14.04': 'Audit Fee',
                'RP-13.02': 'Bank Charges',
                'RP-16.69': 'St Joseph Orthodox Fellowship',
                'RP-16.70': 'St Dionysius Orthodox Fellowship',
                'RP-14.34': 'Repairs And Maintenance-Vehicles',
                'RP-19.03&.04': 'Catholicate Day & Recceessa',
                'RP-19.11': 'Metropolitan Fund',
                'RP-19.21': 'Mission Sunday',
                'RP-19.22': 'Sunday School Cover Collection',
                'RP-19.23': 'Seminary Day',
                'RP-19.15': 'Priest Welfare Fund',
                'RP-19.12': 'Marriage Kaimuthu',
                'RP-19.32': 'Annual Kaimuthu to Tirumeni',
                'RP-19.24': 'Gerbo Sunday',
                'RP-16.50': 'St. George Feast',
                'RP-16.47': 'St. Mary\'s Feast',
                'RP-16.48': 'St.Gregorios Feast ( Annual Feast)',
                'RP-16.15': 'Christmas & New Year Expense',
                'RP-16.14': 'Harvest Day/Parish Day Expense',
                'RP-16.38': 'Miscellaneous Expenses',
                'RP-18.16': 'Asset Purchase',
                'RP-18.23': 'Electrical Equipments',
                'RP-16.32': 'Diocesan Prayer Meeting Expenses'
            }

            for row in backup_data["cashbook"]:
                rf = str(row.get('F') or row.get('receipt_code') or '').strip().replace(' ', '').upper()
                if rf in budget_code_map:
                    if 'E' in row: row['E'] = budget_code_map[rf]
                    else: row['receipt_account_head'] = budget_code_map[rf]

                pn = str(row.get('N') or row.get('payments_code') or '').strip().replace(' ', '').upper()
                if pn in budget_code_map:
                    if 'M' in row: row['M'] = budget_code_map[pn]
                    else: row['payments_account_head'] = budget_code_map[pn]

            with open(os.path.join(EXPORT_DIR, "Cash_Book.json"), "w", encoding="utf-8") as f:
                json.dump(backup_data["cashbook"], f, indent=2)
            print(f"       -> Updated {EXPORT_DIR}/Cash_Book.json ({len(backup_data['cashbook'])} records)")

            # Recalculate Trial_Balance.json live from Cash_Book.json transactions
            try:
                receipt_totals = {}
                payment_totals = {}
                for row in backup_data["cashbook"]:
                    r_code = str(row.get('F') or row.get('receipt_code') or '').strip().replace(' ', '').upper()
                    r_det = str(row.get('G') or '').lower()
                    if 'opening balance' not in r_det and r_code.startswith('RP-'):
                        c_rec = float(str(row.get('H') or row.get('receipt_cash') or 0).replace(',', '') or 0)
                        b_rec = float(str(row.get('I') or row.get('receipt_bank') or 0).replace(',', '') or 0)
                        receipt_totals[r_code] = receipt_totals.get(r_code, 0.0) + c_rec + b_rec

                    p_code = str(row.get('N') or row.get('payments_code') or '').strip().replace(' ', '').upper()
                    if p_code.startswith('RP-'):
                        c_pay = float(str(row.get('P') or row.get('payments_cash') or 0).replace(',', '') or 0)
                        b_pay = float(str(row.get('Q') or row.get('payments_bank') or 0).replace(',', '') or 0)
                        payment_totals[p_code] = payment_totals.get(p_code, 0.0) + c_pay + b_pay

                tb_path = os.path.join(EXPORT_DIR, "Trial_Balance.json")
                if os.path.exists(tb_path):
                    with open(tb_path, "r", encoding="utf-8") as tbf:
                        tb_data = json.load(tbf)
                        for tb_row in tb_data:
                            r_code = str(tb_row.get('A') or tb_row.get('code') or '').strip().replace(' ', '').upper()
                            if r_code in receipt_totals:
                                tb_row['C'] = f"{receipt_totals[r_code]:.2f}"

                            p_code = str(tb_row.get('D') or tb_row.get('p_code') or '').strip().replace(' ', '').upper()
                            if p_code in payment_totals:
                                tb_row['F'] = f"{payment_totals[p_code]:.2f}"

                    with open(tb_path, "w", encoding="utf-8") as tbf:
                        json.dump(tb_data, tbf, indent=2)
                    print(f"       -> Updated {EXPORT_DIR}/Trial_Balance.json with live Cash Book totals")
            except Exception as e:
                print(f"       [WARN] Trial Balance sync warning: {e}")
        if "individual" in backup_data and len(backup_data["individual"]) > 0:
            with open(os.path.join(EXPORT_DIR, "Individual.json"), "w", encoding="utf-8") as f:
                json.dump(backup_data["individual"], f, indent=2)
            print(f"       -> Updated {EXPORT_DIR}/Individual.json")

def read_json_raw(filename):
    path = os.path.join(EXPORT_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "[]"

def build_data_js():
    check_and_sync_latest_backups()
    print("Packaging exported JSON data into data.js...")
    
    cb = read_json_raw("Cash_Book.json")
    ind = read_json_raw("Individual.json")
    tb = read_json_raw("Trial_Balance.json")
    mem = read_json_raw("Members.json")
    bud = read_json_raw("Budget.json")
    cod = read_json_raw("Codes.json")
    auc = read_json_raw("aution25.json")

    js_content = f"""/**
 * Embedded Church Accounting Database
 * Auto-generated for direct file:// and http:// support.
 */
window.CHURCH_DATA = {{
  cashbook: {cb},
  individual: {ind},
  trialBalance: {tb},
  members: {mem},
  budget: {bud},
  codes: {cod},
  auction: {auc}
}};
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024.0
    print(f"[OK] Created data.js ({size_kb:.2f} KB) successfully!")

if __name__ == "__main__":
    build_data_js()
