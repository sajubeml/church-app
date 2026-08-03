import json, re

print("=== FIXING ALL CASHBOOK KEYS FOR RP-12 SUB-CODES ===")

with open('data_export/Cash_Book.json', 'r', encoding='utf-8') as f:
    cb = json.load(f)

head_to_code = [
    ('local travelling allowance to vicar', 'RP-12.02 (d)'),
    ('telephone allowance to vicar', 'RP-12.02 (c)'),
    ('medical allowance to vicar', 'RP-12.02 (a)'),
    ('medical allowance to sexton', 'RP-12.06 (b)'),
    ('annual travelling allowance to vicar', 'RP-12.02 (e)'),
    ('leave salary to vicar', 'RP-12.02 (f)'),
    ('gift purse to vicar', 'RP-12.02 (g)'),
    ('salary to watchman(cemetry)', 'RP-12.03 (b)'),
    ('salary to sexton', 'RP-12.03 (a)'),
    ('salary to ayah', 'RP-12.03 (c)'),
]

updated = 0
for row in cb:
    h_val = ""
    c_key = None
    for k, v in row.items():
        if k == 'payments_account_head' or k.startswith('M'):
            h_val = str(v or '').strip().lower()
        if k == 'payments_code' or k.startswith('N'):
            c_key = k

    if h_val and c_key:
        for head_sub, correct_code in head_to_code:
            if head_sub in h_val:
                old_val = row[c_key]
                if old_val != correct_code:
                    row[c_key] = correct_code
                    updated += 1
                    print(f"Updated '{h_val}' ({c_key}): '{old_val}' -> '{correct_code}'")
                break

with open('data_export/Cash_Book.json', 'w', encoding='utf-8') as f:
    json.dump(cb, f, indent=2, ensure_ascii=False)

print(f"Total CashBook rows updated: {updated}")
