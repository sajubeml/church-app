import json

def get_col(code):
    code = str(code).upper().strip().replace(' ', '').replace('RP-', '')
    code = 'RP-' + code
    mapping = {
        'RP-3.82': 'E', 'RP-3.83': 'E',
        'RP-2.02': 'F', 'RP-2.02(A)': 'F',
        'RP-19.03&.04': 'G',
        'RP-19.11': 'H',
        'RP-19.21': 'I',
        'RP-19.23': 'J',
        'RP-19.15': 'K',
        'RP-10.17': 'L',
        'RP-3.17': 'M',
        'RP-3.16': 'N',
        'RP-3.14': 'O',
        'RP-3.12': 'P',
        'RP-19.22': 'Q',
        'RP-3.33': 'R',
        'RP-2.12': 'S',
        'RP-3.11': 'T',
        'RP-3.05': 'U',
        'RP-2.13': 'V',
        'RP-16.50': 'W',
        'RP-3.31': 'X',
        'RP-3.32': 'Y',
        'RP-3.15(A)': 'Z',
        'RP-3.15(B)': 'AA',
        'RP-3.15(C)': 'AB',
        'RP-3.15(D)': 'AC',
        'RP-3.08': 'AD',
        'RP-3.17(A)': 'AE',
        'RP-2.15(B)': 'AF',
        'RP-2.14': 'AG',
        'RP-2.15(A)': 'AH',
        'RP-3.09': 'AI',
        'RP-3.21': 'AJ',
        'RP-2.16': 'AK',
        'RP-3.22': 'AL',
        # Added aliases that user uses
        'RP-10.04/05': 'G', # Catholicate Day
        'RP-10.13': 'I', # Mission Sunday
        'RP-10.08': 'H', # Metropolitan Fund
        'RP-10.15': 'J', # Seminary Day
        'RP-10.10': 'K', # Priest Welfare
    }
    return mapping.get(code, None) # Return None if not found, DO NOT default to Subscription!

def rebuild():
    input_file = r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json'
    output_file = r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31_Final.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cashbook = data.get('cashbook', [])
    old_individual = data.get('individual', [])
    
    # 1. FIX THE CASHBOOK CODES
    for r in cashbook:
        # Check Receipt Side for RP-16.47
        r_code = str(r.get('F', '')).strip().upper().replace(' ', '')
        r_cash = float(str(r.get('H', '0')).replace(',', '') or '0')
        r_bank = float(str(r.get('I', '0')).replace(',', '') or '0')
        if (r_cash + r_bank) > 0 and r_code == 'RP-16.47':
            r['F'] = 'RP-3.32' # Change receipt to RP-3.32
    
    # Preserve headers (rows 0-3)
    new_individual = old_individual[:4]
    
    # Initialize empty rows for all members in the old individual list
    member_rows = {}
    for m in old_individual[4:]: # skip headers
        reg = m.get('B')
        if reg:
            # Create a 39-column blank row
            row = {chr(65+i): "" for i in range(26)} # A-Z
            for i in range(13): # AA-AM
                row['A' + chr(65+i)] = ""
                
            row['A'] = str(len(member_rows) + 1) # Sl No
            row['B'] = reg
            row['C'] = m.get('C', '') # Name
            row['D'] = m.get('D', '') # Subscription upto
            member_rows[reg] = row

    # Now loop through the entire cashbook and map all receipts
    for r in cashbook:
        reg = r.get('C')
        if reg and reg in member_rows:
            cash_str = str(r.get('H', '0')).replace(',', '').strip()
            bank_str = str(r.get('I', '0')).replace(',', '').strip()
            cash = float(cash_str) if cash_str else 0
            bank = float(bank_str) if bank_str else 0
            amt = cash + bank
            
            if amt > 0:
                col = get_col(r.get('F', ''))
                if col: # Only map if it corresponds to an actual column!
                    current_val = float(str(member_rows[reg].get(col, '0')).replace(',', '').strip() or '0')
                    member_rows[reg][col] = str(current_val + amt)
                
    # Calculate Grand Totals (Column AM)
    for reg, row in member_rows.items():
        grand_total = 0
        for col in row.keys():
            if col not in ['A', 'B', 'C', 'D', 'AM']:
                val = float(str(row.get(col, '0')).replace(',', '').strip() or '0')
                if val > 0:
                    grand_total += val
                    # Format WITHOUT commas to prevent JS parseFloat bugs
                    row[col] = f"{int(val)}" if val.is_integer() else f"{val:.2f}"
                else:
                    row[col] = "" # Leave empty if 0
                    
        if grand_total > 0:
            row['AM'] = f"{int(grand_total)}" if grand_total.is_integer() else f"{grand_total:.2f}"
        else:
            row['AM'] = ""
            
    # Append calculated member rows to the new individual sheet
    for reg in sorted(member_rows.keys(), key=lambda x: int(x) if str(x).isdigit() else 9999):
        new_individual.append(member_rows[reg])
        
    data['individual'] = new_individual
    data['cashbook'] = cashbook
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        
    print(f"Successfully rebuilt ledger and saved to {output_file}")
    
rebuild()
