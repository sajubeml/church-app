import json

with open(r'C:\Users\sajub\Downloads\St_Gregorios_Church_Backup_2026-10-23.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

cb = data.get('cashbook', [])

ovbs = []
candle_cup = []
candles_other = []

for idx, r in enumerate(cb):
    rem = str(r.get('G') or '').strip()
    rem_lower = rem.lower()
    head = str(r.get('E') or '').strip()
    code = str(r.get('F') or '').strip()
    dt = str(r.get('A') or '').strip()
    rcpt = str(r.get('B') or '').strip()
    reg = str(r.get('C') or '').strip()
    name = str(r.get('D') or '').strip()
    cash = float(r.get('H') or 0) if str(r.get('H') or '').strip() else 0.0
    bank = float(r.get('I') or 0) if str(r.get('I') or '').strip() else 0.0
    amt = cash + bank
    
    row_data = {
        'row': idx, 'date': dt, 'rcpt': rcpt, 'reg': reg, 'name': name,
        'rem': rem, 'head': head, 'code': code, 'cash': cash, 'bank': bank, 'amt': amt
    }
    
    if code == 'RP-3.66' or 'ovbs' in head.lower():
        ovbs.append(row_data)
    elif 'candle cup' in rem_lower:
        candle_cup.append(row_data)
    elif any(k in rem_lower for k in ['candle', 'candles']) and 'sale' not in rem_lower and name != '':
        candles_other.append(row_data)

print(f"=== 1. OVBS CONTRIBUTIONS ({len(ovbs)} entries) ===")
print(f"{'Date':<10} | {'Rcpt':<5} | {'Reg':<5} | {'Name':<25} | {'Remarks':<18} | {'Cash':>8} | {'Bank':>8} | {'Total':>8}")
print("-" * 95)
for x in ovbs:
    print(f"{x['date']:<10} | {x['rcpt']:<5} | {x['reg']:<5} | {x['name']:<25} | {x['rem']:<18} | {x['cash']:>8.2f} | {x['bank']:>8.2f} | {x['amt']:>8.2f}")
print("-" * 95)
print(f"{'TOTAL OVBS':<50} | {sum(x['cash'] for x in ovbs):>8.2f} | {sum(x['bank'] for x in ovbs):>8.2f} | {sum(x['amt'] for x in ovbs):>8.2f}")

print("\n")
print(f"=== 2. CANDLE CUP CONTRIBUTIONS ({len(candle_cup)} entries) ===")
print(f"{'Date':<10} | {'Rcpt':<5} | {'Reg':<5} | {'Name':<25} | {'Remarks':<18} | {'Cash':>8} | {'Bank':>8} | {'Total':>8}")
print("-" * 95)
for x in candle_cup:
    print(f"{x['date']:<10} | {x['rcpt']:<5} | {x['reg']:<5} | {x['name']:<25} | {x['rem']:<18} | {x['cash']:>8.2f} | {x['bank']:>8.2f} | {x['amt']:>8.2f}")
print("-" * 95)
print(f"{'TOTAL CANDLE CUP':<50} | {sum(x['cash'] for x in candle_cup):>8.2f} | {sum(x['bank'] for x in candle_cup):>8.2f} | {sum(x['amt'] for x in candle_cup):>8.2f}")

print("\n")
print(f"=== 3. OTHER CANDLE CONTRIBUTIONS / SPONSORSHIPS ({len(candles_other)} entries) ===")
print(f"{'Date':<10} | {'Rcpt':<5} | {'Reg':<5} | {'Name':<25} | {'Remarks':<18} | {'Cash':>8} | {'Bank':>8} | {'Total':>8}")
print("-" * 95)
for x in candles_other:
    print(f"{x['date']:<10} | {x['rcpt']:<5} | {x['reg']:<5} | {x['name']:<25} | {x['rem']:<18} | {x['cash']:>8.2f} | {x['bank']:>8.2f} | {x['amt']:>8.2f}")
print("-" * 95)
print(f"{'TOTAL OTHER CANDLES':<50} | {sum(x['cash'] for x in candles_other):>8.2f} | {sum(x['bank'] for x in candles_other):>8.2f} | {sum(x['amt'] for x in candles_other):>8.2f}")

combined_candles = candle_cup + candles_other
print("\n")
print(f"=== 4. COMBINED ALL CANDLE / CANDLE CUP CONTRIBUTIONS ({len(combined_candles)} entries) ===")
print(f"{'TOTAL ALL CANDLES':<50} | {sum(x['cash'] for x in combined_candles):>8.2f} | {sum(x['bank'] for x in combined_candles):>8.2f} | {sum(x['amt'] for x in combined_candles):>8.2f}")
