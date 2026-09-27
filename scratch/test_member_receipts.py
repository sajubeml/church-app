import re
import json

with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

cb_match = re.search(r'cashbook\s*:\s*\[(.*?)\]\s*,\s*individual', text, re.DOTALL)
cb_text = cb_match.group(1) if cb_match else ""
raw_cb = re.findall(r'\{[^{}]*\}', cb_text, re.DOTALL)

cb_entries = []
for ro in raw_cb:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        cb_entries.append(json.loads(q))
    except:
        pass

print(f"Total Cashbook entries: {len(cb_entries)}")

# Group cashbook receipts by Reg No (column C)
member_receipts = {}
for r in cb_entries:
    reg = str(r.get('C', '') or '').strip()
    date = str(r.get('A', '') or '').strip()
    rec = str(r.get('B', '') or '').strip()
    name = str(r.get('D', '') or '').strip()
    head = str(r.get('E', '') or '').strip()
    code = str(r.get('F', '') or '').strip()
    rem = str(r.get('G', '') or '').strip()
    amt_h = str(r.get('H', '') or '').replace(',', '').strip()
    amt_i = str(r.get('I', '') or '').replace(',', '').strip()
    
    try: cash_amt = float(amt_h) if amt_h else 0
    except: cash_amt = 0
    try: bank_amt = float(amt_i) if amt_i else 0
    except: bank_amt = 0
    tot_amt = cash_amt + bank_amt
    
    if reg and tot_amt > 0:
        if reg not in member_receipts:
            member_receipts[reg] = []
        member_receipts[reg].append({
            'date': date,
            'rec_no': rec,
            'name': name,
            'head': head,
            'code': code,
            'remarks': rem,
            'amount': tot_amt
        })

print(f"Found receipts for {len(member_receipts)} unique Reg Nos in Cashbook.")
for reg in list(member_receipts.keys())[:5]:
    rec_list = member_receipts[reg]
    print(f"\nMember Reg #{reg} ({rec_list[0]['name']}): {len(rec_list)} cashbook receipts")
    for rc in rec_list[:3]:
        print(f"  Date: {rc['date']} | Rt No: {rc['rec_no']} | Head: {rc['head']} | Amt: {rc['amount']}")

