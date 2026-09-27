import json
import re

with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

cb_match = re.search(r'cashbook\s*:\s*\[(.*?)\]\s*,\s*individual', text, re.DOTALL)
cb_text = cb_match.group(1) if cb_match else ""
raw_cb = re.findall(r'\{[^{}]*\}', cb_text, re.DOTALL)

cb_entries = []
for ro in raw_cb:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', q := ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        cb_entries.append(json.loads(q))
    except:
        pass

print(f"Loaded {len(cb_entries)} cashbook entries")

# Search for Wiley / Wilsy / Reg 51 / Reg 53 / Reg 96 (Susamma) / Reg 107 (Thomas A.M.)
targets = ['51', '53', '96', '107', 'wiley', 'wilsy', 'susamma']

print("\n--- CASHBOOK RECEIPTS FOR TARGET REG NOS / NAMES ---")
for r in cb_entries:
    reg = str(r.get('C', '') or '').strip()
    name = str(r.get('D', '') or '').strip().lower()
    if reg in ['51', '53', '96', '107'] or any(t in name for t in ['wiley', 'wilsy', 'susamma']):
        rec = r.get('B')
        date = r.get('A')
        head = r.get('E')
        code = r.get('F')
        rem = r.get('G')
        amt = r.get('H') or r.get('I') or '0'
        print(f"Date: {date} | Rec: {rec} | Reg: {reg} | Name: {r.get('D')} | Head: {head} | Code: {code} | Amt: {amt} | Rem: {rem}")

