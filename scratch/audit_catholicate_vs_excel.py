import re
import json

def load_data_js(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Let's extract JSON objects for cashbook by parsing text or regex
    # In data.js, cashbook is an array of objects
    # Let's extract all object strings inside cashbook array
    cb_match = re.search(r'cashbook\s*:\s*\[(.*?)\]\s*,\s*individual', text, re.DOTALL)
    if not cb_match:
        cb_match = re.search(r'cashbook\s*:\s*\[(.*?)\]\s*,', text, re.DOTALL)
        
    cb_text = cb_match.group(1) if cb_match else ""
    
    # Parse individual entries
    entries = []
    # Find all { ... }
    raw_objs = re.findall(r'\{[^{}]*\}', cb_text, re.DOTALL)
    for ro in raw_objs:
        # Convert JS keys to quoted keys
        q = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', ro)
        q = re.sub(r',\s*([}\]])', r'\1', q)
        try:
            d = json.loads(q)
            entries.append(d)
        except Exception as e:
            pass
    return entries, text

def audit_file(filepath):
    entries, raw_text = load_data_js(filepath)
    print(f"\n==========================================")
    print(f"AUDITING FILE: {filepath}")
    print(f"Total Cashbook entries parsed: {len(entries)}")
    
    # Account heads and codes in MASTER for Catholicate
    # RP-10.04, RP-10.05, RP-2.xx etc.
    cath_entries = []
    total_cath = 0
    
    # Group by Reg No
    reg_sum = {}
    nm_sum = 0
    unknown_reg_sum = 0
    
    for idx, r in enumerate(entries):
        head = str(r.get('E', '') or '').strip()
        code = str(r.get('F', '') or '').strip()
        remarks = str(r.get('G', '') or '').strip()
        reg_no = str(r.get('C', '') or '').strip()
        name = str(r.get('D', '') or '').strip()
        rec_no = str(r.get('B', '') or '').strip()
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
            total_cath += amt
            cath_entries.append({
                'idx': idx, 'rec': rec_no, 'reg': reg_no, 'name': name, 'head': head, 'code': code, 'amt': amt, 'remarks': remarks
            })
            if reg_no:
                reg_sum[reg_no] = reg_sum.get(reg_no, 0) + amt
            else:
                nm_sum += amt

    print(f"Total Catholicate Amount in Cashbook: {total_cath}")
    print(f"Total entries: {len(cath_entries)}")
    print(f"Sum of Member Reg Nos: {sum(reg_sum.values())}")
    print(f"Sum of Non-Member / Empty Reg Nos: {nm_sum}")
    
    print("\nDetailed list of all Catholicate entries:")
    for c in cath_entries:
        print(f"  Rec #{c['rec']} | Reg #{c['reg']:<5} | Name: {c['name']:<20} | Head: {c['head']:<25} | Code: {c['code']:<12} | Amt: {c['amt']:>7} | Rem: {c['remarks']}")

audit_file('c:\\CASHBOOK_APP\\data.js')
audit_file('c:\\saju_old pc\\Church_App\\anti_gravity_v9.2\\data.js')
