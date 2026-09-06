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
    return mapping.get(code, 'UNKNOWN')

with open(r'c:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-08-31_Final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('--- Receipts with UNKNOWN RP Codes ---')
for r in data.get('cashbook', []):
    code = str(r.get('F', '')).strip()
    cash = float(str(r.get('H', '0')).replace(',', '') or '0')
    bank = float(str(r.get('I', '0')).replace(',', '') or '0')
    if (cash + bank) > 0 and 'Deposit' not in str(r.get('E', '')):
        # Check if the code is known in Individual Ledger Mapping
        col = get_col(code)
        if col == 'UNKNOWN':
            # Check if it has a member registered
            if r.get('C'):
                print(f"Doc: {r.get('B')}, Member: {r.get('C')} - {r.get('D')}, Head: {r.get('E')}, Code: {code}, Amt: {cash+bank}")
