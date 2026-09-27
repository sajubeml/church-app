import json
import re

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

# Let's inspect all receipts with Catholicate or Recessa in head/code/remarks
print("=== ALL CATHOLICATE/RECESSA RECEIPTS IN CASHBOOK ===")
cath_total = 0
for r in cb_entries:
    head = str(r.get('E', '') or '').strip()
    code = str(r.get('F', '') or '').strip()
    rem = str(r.get('G', '') or '').strip()
    amt_str = r.get('H') or r.get('I') or '0'
    try:
        amt = float(str(amt_str).replace(',', '').strip() or 0)
    except:
        amt = 0
    if 'catholicate' in head.lower() or 'catholicate' in code.lower() or 'catholicate' in rem.lower() or 'recessa' in head.lower() or 'recessa' in rem.lower() or 'RP-10.04' in code or 'RP-10.05' in code:
        cath_total += amt
        print(f"Rec #{r.get('B'):<5} | Date: {r.get('A'):<10} | Reg #{r.get('C'):<5} | Name: {r.get('D'):<20} | Head: {head:<25} | Code: {code:<12} | Amt: {amt:>7.2f} | Rem: {rem}")

print(f"\nTotal Catholicate in Cashbook: {cath_total}")

# Let's also check if there are any receipts with amount 2000 or 4000 or 1400 in the entire cashbook!
print("\n=== ALL RECEIPTS WITH AMOUNT 2000, 4000, or 1400 IN CASHBOOK ===")
for r in cb_entries:
    amt_str = r.get('H') or r.get('I') or '0'
    try:
        amt = float(str(amt_str).replace(',', '').strip() or 0)
    except:
        amt = 0
    if amt in [2000, 4000, 1400, 2600, 3400]:
        print(f"Rec #{r.get('B'):<5} | Date: {r.get('A'):<10} | Reg #{r.get('C'):<5} | Name: {r.get('D'):<20} | Head: {r.get('E'):<25} | Code: {r.get('F'):<12} | Amt: {amt:>7.2f} | Rem: {r.get('G')}")

