import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data_export/Cash_Book.json', 'r', encoding='utf-8') as f:
    cashbook = json.load(f)

print("=== ALL CASHBOOK TRANSACTIONS FOR SANTHOSH K. A. (REG #150) IN APP ===")
total_donations = 0.0
total_all = 0.0

for idx, r in enumerate(cashbook):
    c_val = str(r.get('C', '') or '').strip()
    d_val = str(r.get('D', '') or '').strip()
    if c_val == '150' or 'santhosh' in d_val.lower():
        h = float(r.get('H', 0) or 0)
        i = float(r.get('I', 0) or 0)
        amt = h + i
        rcpt = r.get('B', '')
        dt = r.get('A', '')
        head = r.get('E', '')
        desc = r.get('G', '')
        total_all += amt
        if 'donation' in head.lower() or 'rp-2.02' in str(r.get('F', '')).lower():
            total_donations += amt
        print(f"Receipt #{rcpt:<5} | Date: {dt} | Head: {head:<35} | Amt: ₹ {amt:,.2f} | Note: {desc}")

print("-" * 80)
print(f"Total Donation General Receipts in Cash Book: ₹ {total_donations:,.2f}")
print(f"Total All Receipts for Santhosh K. A.:        ₹ {total_all:,.2f}")
