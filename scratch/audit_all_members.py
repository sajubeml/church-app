import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

with open('data_export/Cash_Book.json', 'r', encoding='utf-8') as f:
    cashbook = json.load(f)

with open('data_export/Individual.json', 'r', encoding='utf-8') as f:
    indiv = json.load(f)

# Group Cashbook Receipts by Reg No
cb_by_reg = {}
for idx, row in enumerate(cashbook):
    reg = str(row.get('C', '') or '').strip()
    if not reg:
        continue
    # Cash amount (H) or Bank amount (I)
    cash_amt = float(row.get('H', 0) or 0)
    bank_amt = float(row.get('I', 0) or 0)
    tot = cash_amt + bank_amt
    
    head = str(row.get('E', '') or '').strip()
    code = str(row.get('F', '') or '').strip()
    date_val = str(row.get('A', '') or '').strip()

    if reg not in cb_by_reg:
        cb_by_reg[reg] = []
    cb_by_reg[reg].append({
        'row_idx': idx,
        'date': date_val,
        'head': head,
        'code': code,
        'amount': tot,
        'name': str(row.get('D', '') or '').strip()
    })

print(f"Total Unique Members with Cashbook Entries: {len(cb_by_reg)}")

# Compare each member in Individual.json
print("\n=== AUDITING ALL MEMBERS IN INDIVIDUAL SHEET ===")
discrepancies = []

for idx, member in enumerate(indiv):
    reg_no = str(member.get(f'B{idx+1}', member.get('B', '')) or '').strip()
    # Find matching cell ref in row
    reg_val = None
    for k, v in member.items():
        if k.startswith('B') and k[1:].isdigit():
            reg_val = str(v or '').strip()
            row_num = k[1:]
            break

    if not reg_val or reg_val == 'Register No.' or reg_val == 'None':
        continue

    # Get member name and current columns
    name = str(member.get(f'C{row_num}', '') or '')
    col_e = float(member.get(f'E{row_num}', 0) or 0) # Sub
    col_f = float(member.get(f'F{row_num}', 0) or 0) # Donation Gen
    col_g = float(member.get(f'G{row_num}', 0) or 0)
    col_h = float(member.get(f'H{row_num}', 0) or 0)
    col_i = float(member.get(f'I{row_num}', 0) or 0)
    col_j = float(member.get(f'J{row_num}', 0) or 0)
    col_k = float(member.get(f'K{row_num}', 0) or 0)
    col_l = float(member.get(f'L{row_num}', 0) or 0)
    col_m = float(member.get(f'M{row_num}', 0) or 0)
    col_n = float(member.get(f'N{row_num}', 0) or 0)
    col_o = float(member.get(f'O{row_num}', 0) or 0)
    col_p = float(member.get(f'P{row_num}', 0) or 0)
    col_q = float(member.get(f'Q{row_num}', 0) or 0)
    col_r = float(member.get(f'R{row_num}', 0) or 0)
    col_s = float(member.get(f'S{row_num}', 0) or 0)
    col_t = float(member.get(f'T{row_num}', 0) or 0)
    col_u = float(member.get(f'U{row_num}', 0) or 0)
    col_v = float(member.get(f'V{row_num}', 0) or 0)
    col_w = float(member.get(f'W{row_num}', 0) or 0)
    col_x = float(member.get(f'X{row_num}', 0) or 0)
    col_y = float(member.get(f'Y{row_num}', 0) or 0)
    col_z = float(member.get(f'Z{row_num}', 0) or 0)
    col_aa = float(member.get(f'AA{row_num}', 0) or 0)
    col_ab = float(member.get(f'AB{row_num}', 0) or 0)
    col_ac = float(member.get(f'AC{row_num}', 0) or 0)
    col_ad = float(member.get(f'AD{row_num}', 0) or 0)
    col_ae = float(member.get(f'AE{row_num}', 0) or 0)
    col_af = float(member.get(f'AF{row_num}', 0) or 0)
    col_ag = float(member.get(f'AG{row_num}', 0) or 0)
    col_ah = float(member.get(f'AH{row_num}', 0) or 0)
    col_ai = float(member.get(f'AI{row_num}', 0) or 0)
    col_aj = float(member.get(f'AJ{row_num}', 0) or 0)
    col_ak = float(member.get(f'AK{row_num}', 0) or 0)
    col_al = float(member.get(f'AL{row_num}', 0) or 0)
    col_am = float(member.get(f'AM{row_num}', 0) or 0) # Reported Grand Total

    # Sum of E through AL
    calc_sum = sum([
        col_e, col_f, col_g, col_h, col_i, col_j, col_k, col_l, col_m, col_n, col_o, col_p,
        col_q, col_r, col_s, col_t, col_u, col_v, col_w, col_x, col_y, col_z, col_aa, col_ab,
        col_ac, col_ad, col_ae, col_af, col_ag, col_ah, col_ai, col_aj, col_ak, col_al
    ])

    if abs(calc_sum - col_am) > 0.01:
        print(f"Row {row_num} (Reg #{reg_val} - {name}): Internal Row Sum Error! Sum of cols = {calc_sum}, AM = {col_am}")
        discrepancies.append((reg_val, name, "Internal Row Sum Mismatch", calc_sum, col_am))

    # Check against cashbook entries
    cb_entries = cb_by_reg.get(reg_val, [])
    cb_tot = sum(e['amount'] for e in cb_entries)
    
    if cb_entries:
        print(f"Reg #{reg_val:<4} ({name:<25}): Sheet Col F={col_f:<8} Row Total={col_am:<8} Cashbook Entries Sum={cb_tot}")
        for e in cb_entries:
            print(f"    -> CB Row {e['row_idx']}: Date {e['date']} | Head: {e['head']} ({e['code']}) | Amt: ₹ {e['amount']}")

