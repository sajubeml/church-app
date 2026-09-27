import re
import json

def parse_data_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert JS object syntax to standard JSON
    # 1. Remove comments if any
    # 2. Add quotes around keys
    # Or evaluate using python exec by declaring JS true/false/null/undefined
    
    # Extract INITIAL_DATA block
    start_idx = text.find('window.INITIAL_DATA =')
    if start_idx == -1:
        start_idx = text.find('const INITIAL_DATA =')
    if start_idx == -1:
        start_idx = 0
    
    json_like = text[start_idx:]
    # Replace keys like A: with "A":
    # Let's clean up JS code to execute in Python
    # Define JS null/true/false/undefined in python context
    null = None
    true = True
    false = False
    undefined = None
    
    # Cut off window.INITIAL_DATA = { ... };
    eq_idx = json_like.find('{')
    semi_idx = json_like.rfind('};')
    if semi_idx == -1:
        semi_idx = json_like.rfind('}')
    else:
        semi_idx += 1
        
    js_obj = json_like[eq_idx:semi_idx]
    
    # To parse JS object in python cleanly:
    # Use re to quote unquoted keys
    js_obj_quoted = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', js_obj)
    # Remove trailing commas
    js_obj_quoted = re.sub(r',\s*([}\]])', r'\1', js_obj_quoted)
    
    try:
        return json.loads(js_obj_quoted)
    except Exception as e:
        print("JSON parse error:", e)
        # Fallback: exec trick
        g = {'null': None, 'true': True, 'false': False, 'undefined': None}
        l = {}
        # Replace unquoted keys in python dict syntax
        py_str = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', js_obj)
        py_str = re.sub(r',\s*([}\]])', r'\1', py_str)
        return eval(py_str, g, l)

data = parse_data_js('data.js')
cashbook = data.get('cashbook', [])
individual = data.get('individual', [])
members = data.get('members', [])

print(f"Loaded cashbook ({len(cashbook)} rows), individual ({len(individual)} rows), members ({len(members)} rows)")

# Now let's mimic app_supabase.js mapping logic!
# Find column key for Catholicate Day & Recessa in individual header
ind_header = individual[3] if len(individual) > 3 else {}
cath_col_key = None
for k, v in ind_header.items():
    if v and 'catholicate' in str(v).lower():
        cath_col_key = k
        print(f"Catholicate column key in Individual header: {k} -> {v}")

# Total in Cashbook for Catholicate
cb_cath_entries = []
cb_cath_total = 0

for idx, r in enumerate(cashbook):
    head = str(r.get('E', '') or '').strip()
    code = str(r.get('F', '') or '').strip()
    remarks = str(r.get('G', '') or '').strip()
    
    pay_head = str(r.get('M', '') or '').strip()
    pay_code = str(r.get('N', '') or '').strip()
    pay_rem = str(r.get('O', '') or '').strip()
    
    # Check left side (Receipts)
    amt_str = r.get('H') or r.get('I') or '0'
    try:
        amt = float(str(amt_str).replace(',', '').strip() or 0)
    except:
        amt = 0
        
    is_cath = ('catholicate' in head.lower() or 
               'catholicate' in code.lower() or 
               'catholicate' in remarks.lower() or
               'RP-10.04' in code or 'RP-10.05' in code)
    
    if is_cath:
        reg_no = str(r.get('C', '') or '').strip()
        name = str(r.get('D', '') or '').strip()
        rec_no = str(r.get('B', '') or '').strip()
        date = str(r.get('A', '') or '').strip()
        cb_cath_entries.append({
            'cb_index': idx,
            'date': date,
            'rec_no': rec_no,
            'reg_no': reg_no,
            'name': name,
            'head': head,
            'code': code,
            'remarks': remarks,
            'amount': amt
        })
        cb_cath_total += amt

print(f"\n--- CASHBOOK CATHOLICATE ENTRIES ---")
print(f"Total count: {len(cb_cath_entries)}, Total amount: {cb_cath_total}")

# Now let's group CB entries by Reg No
reg_totals = {}
for e in cb_cath_entries:
    reg = e['reg_no'] or 'EMPTY'
    reg_totals[reg] = reg_totals.get(reg, 0) + e['amount']

print("\nGrouped by Reg No in Cashbook:")
for reg, tot in sorted(reg_totals.items(), key=lambda x: str(x[0])):
    print(f"  Reg No {reg}: {tot}")

# Now let's check Individual Ledger calculation for each member row (rows from index 4 onwards)
# Let's map how individual ledger calculates totals
ind_totals_by_reg = {}
ind_grand_total = 0

# Member reg nos in individual grid:
for row_idx in range(4, len(individual)):
    r = individual[row_idx]
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    if not reg and not name:
        continue
    
    # Calculate sum from cashbook for this reg
    # App logic: matches cashbook Col C == member Reg No (Col B)
    # If head/code matches Catholicate Day & Recessa
    member_cb_sum = 0
    for e in cb_cath_entries:
        if e['reg_no'] == reg:
            member_cb_sum += e['amount']
            
    if member_cb_sum > 0:
        ind_totals_by_reg[reg] = {'name': name, 'amount': member_cb_sum}
        ind_grand_total += member_cb_sum

print(f"\nIndividual Ledger Calculated Grand Total for Catholicate: {ind_grand_total}")
print(f"Difference between CB Total ({cb_cath_total}) and Individual Ledger Grand Total ({ind_grand_total}): {cb_cath_total - ind_grand_total}")

