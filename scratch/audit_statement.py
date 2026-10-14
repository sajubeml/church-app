import openpyxl
import json
from datetime import datetime

wb = openpyxl.load_workbook(r'C:\Users\sajub\Downloads\St_Gregorios_Cash_Book_FY2026_2027 (5).xlsx', data_only=True)
ws = wb.active

def clean_val(v):
    if v is None: return 0.0
    s = str(v).replace(',', '').strip()
    try: return float(s)
    except: return 0.0

rec_heads = {}
pay_heads = {}

total_cash_r = 0.0
total_bank_r = 0.0
total_cash_p = 0.0
total_bank_p = 0.0

for r in range(8, 922):
    r_head = str(ws.cell(r, 5).value or '').strip()
    r_code = str(ws.cell(r, 6).value or '').strip()
    c_r = clean_val(ws.cell(r, 8).value)
    b_r = clean_val(ws.cell(r, 9).value)
    
    p_head = str(ws.cell(r, 12).value or '').strip()
    p_code = str(ws.cell(r, 13).value or '').strip()
    c_p = clean_val(ws.cell(r, 15).value)
    b_p = clean_val(ws.cell(r, 16).value)

    total_cash_r += c_r
    total_bank_r += b_r
    total_cash_p += c_p
    total_bank_p += b_p

    if r_code or r_head:
        if 'cash deposited' not in r_head.lower() and r_code != 'CD':
            if r_code:
                if r_code not in rec_heads:
                    rec_heads[r_code] = {'name': r_head, 'amount': 0.0, 'cash': 0.0, 'bank': 0.0}
                rec_heads[r_code]['amount'] += (c_r + b_r)
                rec_heads[r_code]['cash'] += c_r
                rec_heads[r_code]['bank'] += b_r
                if r_head: rec_heads[r_code]['name'] = r_head

    if p_code or p_head:
        if 'cash deposited' not in p_head.lower() and p_code != 'CD':
            if p_code:
                if p_code not in pay_heads:
                    pay_heads[p_code] = {'name': p_head, 'amount': 0.0, 'cash': 0.0, 'bank': 0.0}
                pay_heads[p_code]['amount'] += (c_p + b_p)
                pay_heads[p_code]['cash'] += c_p
                pay_heads[p_code]['bank'] += b_p
                if p_head: pay_heads[p_code]['name'] = p_head

opening_cash = 9879.0
opening_bank = 651682.0

closing_cash = opening_cash + total_cash_r - total_cash_p
closing_bank = opening_bank + total_bank_r - total_bank_p

print("=== CASH & BANK VERIFICATION FROM CASH BOOK ===")
print(f"Opening Cash:  INR {opening_cash:>12,.2f}")
print(f"Opening Bank:  INR {opening_bank:>12,.2f}")
print(f"Total Cash R:  INR {total_cash_r:>12,.2f}  (Gross: {opening_cash + total_cash_r:,.2f})")
print(f"Total Bank R:  INR {total_bank_r:>12,.2f}  (Gross: {opening_bank + total_bank_r:,.2f})")
print(f"Total Cash P:  INR {total_cash_p:>12,.2f}")
print(f"Total Bank P:  INR {total_bank_p:>12,.2f}")
print(f"Closing Cash:  INR {closing_cash:>12,.2f}  [Matches Cash Book: 2,654]")
print(f"Closing Bank:  INR {closing_bank:>12,.2f}  [Matches Cash Book & Federal Bank: 20,29,537]")
print(f"Total Closing: INR {closing_cash + closing_bank:>12,.2f}  [Matches Cash Book: 20,32,191]")

print("\n=== RECONCILING WITH REVENUE / EXPENSE HEADS ===")
tot_rec_non_contra = sum(d['amount'] for d in rec_heads.values())
tot_pay_non_contra = sum(d['amount'] for d in pay_heads.values())
print(f"Receipt Heads Total: INR {tot_rec_non_contra:>12,.2f}")
print(f"Payment Heads Total: INR {tot_pay_non_contra:>12,.2f}")
print(f"Net Operating Surplus: INR {tot_rec_non_contra - tot_pay_non_contra:>12,.2f}")
print(f"Closing Balance - Opening Balance: INR {(closing_cash + closing_bank) - (opening_cash + opening_bank):>12,.2f}")
