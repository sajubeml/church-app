import json
import re

# Load data.js
with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract cashbook entries
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

# Extract individual header row to map head/code to columns
ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,\s*members', text, re.DOTALL)
if not ind_match:
    ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,', text, re.DOTALL)
ind_text = ind_match.group(1)
raw_ind = re.findall(r'\{[^{}]*\}', ind_text, re.DOTALL)

ind_rows = []
for ro in raw_ind:
    q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
    q = re.sub(r',\s*([}\]])', r'\1', q)
    try:
        ind_rows.append(json.loads(q))
    except:
        pass

header_row = ind_rows[3] if len(ind_rows) > 3 else {}
print("Header columns in Individual Ledger:")
for k, v in header_row.items():
    print(f"  Col {k}: {v}")

# Now let's calculate dynamic total for each ledger column key from Cashbook!
# Excel values provided by user:
excel_values = {
    'D': ('Subscription (Min 200.00)', 205700),
    'E': ('Donation General', 272080),
    'F': ('Catholicate Day & Recessa', 36050),
    'G': ('Metropolitan Fund', 16450),
    'H': ('Mission Sunday', 10550),
    'I': ('Seminary Day', 7450),
    'J': ('Priest Welfare Fund', 8200),
    'K': ('Old Cover Collection', 8100),
    'L': ('Wedding Anniversary Offerings', 9500),
    'M': ('Birthday Offerings', 22750),
    'N': ('Baptism', 2500),
    'O': ('Orma Qurbana/Holy Qurbana', 7220),
    'P': ('Sunday School Day Collection', 5650),
    'Q': ('St. Gregorios Feast Collection', 1600),
    'R': ('Parish Vanchika (House Offertory)', 5800), # in image: 5800, user text: 1500 + 5800?
    'S': ('Pension Scheme Collection', 78606),
    'T': ('St. George Feast', 15500),
    'U': ('St. Thomas Feast', 600),
    'V': ('St. Mary\'s Feast Collection', 85300),
    'W': ('Harvest Festival Collection', 1500),
    'X': ('Passion Week Collection', 1500),
    'Y': ('Charity Fund Collection', 1000),
    'Z': ('Building Fund', 96500),
    'AA': ('Others', 156300)
}

# Let's inspect all unique E (head) and F (code) in cashbook and see how they map!
print("\n=== CASHBOOK RECEIPTS SUMMARY BY ACCOUNT HEAD & CODE ===")
head_totals = {}
for r in cb_entries:
    head = str(r.get('E', '') or '').strip()
    code = str(r.get('F', '') or '').strip()
    amt_str = r.get('H') or r.get('I') or '0'
    try:
        amt = float(str(amt_str).replace(',', '').strip() or 0)
    except:
        amt = 0
    key = f"{code} | {head}"
    head_totals[key] = head_totals.get(key, 0) + amt

for k, v in sorted(head_totals.items(), key=lambda x: x[0]):
    print(f"{k:<60} : {v:>10.2f}")

