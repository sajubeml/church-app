import json

with open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31_Rebuilt.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cb = data.get('cashbook', [])
tb = data.get('trialBalance', [])

tb_expected_by_code = {}

for r in cb:
    r_head = str(r.get('E', '')).strip()
    r_code = str(r.get('F', '')).strip().upper().replace(' ', '')
    r_cash = float(str(r.get('H', '0')).replace(',', '') or '0')
    r_bank = float(str(r.get('I', '0')).replace(',', '') or '0')
    r_amt = r_cash + r_bank
    
    if r_amt > 0 and 'Opening Balance' not in r_head and 'Deposit' not in r_head and 'Withdraw' not in r_head:
        if r_code:
            if r_code not in tb_expected_by_code:
                tb_expected_by_code[r_code] = {'Receipts': 0, 'Payments': 0, 'Head': r_head}
            tb_expected_by_code[r_code]['Receipts'] += r_amt

    p_head = str(r.get('M', '')).strip()
    p_code = str(r.get('N', '')).strip().upper().replace(' ', '')
    p_cash = float(str(r.get('P', '0')).replace(',', '') or '0')
    p_bank = float(str(r.get('Q', '0')).replace(',', '') or '0')
    p_amt = p_cash + p_bank
    
    if p_amt > 0 and 'Deposit' not in p_head and 'Withdraw' not in p_head:
        if p_code:
            if p_code not in tb_expected_by_code:
                tb_expected_by_code[p_code] = {'Receipts': 0, 'Payments': 0, 'Head': p_head}
            tb_expected_by_code[p_code]['Payments'] += p_amt

tb_actual_by_code = {}
for idx, r in enumerate(tb):
    if idx < 2: continue # skip headers
    code = str(r.get('B', '')).strip().upper().replace(' ', '')
    head = str(r.get('C', '')).strip()
    rec = float(str(r.get('D', '0')).replace(',', '') or '0')
    pay = float(str(r.get('E', '0')).replace(',', '') or '0')
    
    if code:
        tb_actual_by_code[code] = {'Receipts': rec, 'Payments': pay, 'Head': head}

discrepancies = []
for code, exp in tb_expected_by_code.items():
    act = tb_actual_by_code.get(code)
    if not act:
        discrepancies.append(f"MISSING IN TB: [{code}] {exp['Head']} - Expected Rec: {exp['Receipts']}, Pay: {exp['Payments']}")
    else:
        if act['Receipts'] != exp['Receipts'] or act['Payments'] != exp['Payments']:
            discrepancies.append(f"MISMATCH IN TB: [{code}] {exp['Head']} - Expected: R:{exp['Receipts']}, P:{exp['Payments']} | Actual: R:{act['Receipts']}, P:{act['Payments']}")

for d in discrepancies:
    print(d)

print(f"Total Discrepancies (by Code): {len(discrepancies)}")

# Special output for RP-3.32
print("--- RP-3.32 Audit ---")
print("Expected (Cashbook):", tb_expected_by_code.get('RP-3.32'))
print("Actual (Trial Balance):", tb_actual_by_code.get('RP-3.32'))
