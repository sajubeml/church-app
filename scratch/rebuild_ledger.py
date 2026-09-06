import json

def get_col(code):
    code = str(code).upper().strip().replace(' ', '').replace('RP-', '')
    code = 'RP-' + code
    if code == 'RP-3.82' or code == 'RP-3.83': return 'E'
    if code == 'RP-2.02' or code == 'RP-2.02(A)': return 'F'
    if code == 'RP-19.03&.04': return 'G'
    if code == 'RP-19.11': return 'H'
    if code == 'RP-19.21': return 'I'
    if code == 'RP-19.23': return 'J'
    if code == 'RP-19.15': return 'K'
    if code == 'RP-10.17': return 'L'
    if code == 'RP-3.17': return 'M'
    if code == 'RP-3.16': return 'N'
    if code == 'RP-3.14': return 'O'
    if code == 'RP-3.12': return 'P'
    if code == 'RP-19.22': return 'Q'
    if code == 'RP-3.33': return 'R'
    if code == 'RP-2.12': return 'S'
    if code == 'RP-3.11': return 'T'
    if code == 'RP-3.05': return 'U'
    if code == 'RP-2.13': return 'V'
    if code == 'RP-16.50': return 'W'
    if code == 'RP-3.31': return 'X'
    if code == 'RP-3.32': return 'Y'
    if code == 'RP-3.15(A)': return 'Z'
    if code == 'RP-3.15(B)': return 'AA'
    if code == 'RP-3.15(C)': return 'AB'
    if code == 'RP-3.15(D)': return 'AC'
    if code == 'RP-3.08': return 'AD'
    if code == 'RP-3.17(A)': return 'AE'
    if code == 'RP-2.15(B)': return 'AF'
    if code == 'RP-2.14': return 'AG'
    if code == 'RP-2.15(A)': return 'AH'
    if code == 'RP-3.09': return 'AI'
    if code == 'RP-3.21': return 'AJ'
    if code == 'RP-2.16': return 'AK'
    if code == 'RP-3.22': return 'AL'
    return 'E'

def rebuild():
    input_file = r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31.json'
    output_file = r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31_Rebuilt.json'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cashbook = data.get('cashbook', [])
    old_individual = data.get('individual', [])
    
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
                    # Format without decimals if whole
                    row[col] = f"{int(val):,}" if val.is_integer() else f"{val:,.2f}"
                else:
                    row[col] = "" # Leave empty if 0
                    
        if grand_total > 0:
            row['AM'] = f"{int(grand_total):,}" if grand_total.is_integer() else f"{grand_total:,.2f}"
        else:
            row['AM'] = ""
            
    # Append calculated member rows to the new individual sheet
    for reg in sorted(member_rows.keys(), key=lambda x: int(x) if str(x).isdigit() else 9999):
        new_individual.append(member_rows[reg])
        
    data['individual'] = new_individual
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        
    print(f"Successfully rebuilt ledger and saved to {output_file}")
    
rebuild()
