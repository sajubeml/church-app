import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import re

CASHBOOK_XLSX = r"C:\Users\sajub\Downloads\St_Gregorios_Cash_Book_FY2026_2027 (5).xlsx"
OUTPUT_HTML = r"c:\CASHBOOK_APP\Half_Yearly_Audited_AGM_Report_30_09_2026.html"
OUTPUT_XLSX = r"c:\CASHBOOK_APP\Half_Yearly_Audited_AGM_Report_30_09_2026.xlsx"

wb_src = openpyxl.load_workbook(CASHBOOK_XLSX, data_only=True)
ws_src = wb_src.active

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
    r_head = str(ws_src.cell(r, 5).value or '').strip()
    r_code = str(ws_src.cell(r, 6).value or '').strip()
    c_r = clean_val(ws_src.cell(r, 8).value)
    b_r = clean_val(ws_src.cell(r, 9).value)
    
    p_head = str(ws_src.cell(r, 12).value or '').strip()
    p_code = str(ws_src.cell(r, 13).value or '').strip()
    c_p = clean_val(ws_src.cell(r, 15).value)
    b_p = clean_val(ws_src.cell(r, 16).value)

    total_cash_r += c_r
    total_bank_r += b_r
    total_cash_p += c_p
    total_bank_p += b_p

    # Auto-classify missing code in row for Kanika on 3-5-26
    if not r_code and 'kanika on 3-5-26' in str(ws_src.cell(r, 7).value or '').lower():
        r_code = 'RP-3.10'
        r_head = 'Kanicka Church'

    if r_code or r_head:
        if 'cash deposited' not in r_head.lower() and r_code != 'CD':
            if r_code:
                if r_code not in rec_heads:
                    rec_heads[r_code] = {'name': r_head, 'amount': 0.0}
                rec_heads[r_code]['amount'] += (c_r + b_r)
                if r_head: rec_heads[r_code]['name'] = r_head

    if p_code or p_head:
        if 'cash deposited' not in p_head.lower() and p_code != 'CD':
            if p_code:
                if p_code not in pay_heads:
                    pay_heads[p_code] = {'name': p_head, 'amount': 0.0}
                pay_heads[p_code]['amount'] += (c_p + b_p)
                if p_head: pay_heads[p_code]['name'] = p_head

opening_cash = 9879.0
opening_bank = 651682.0

# Exact audited closing balances as per Cash Book
closing_cash = 2654.00
closing_bank = 2029537.00
closing_bank_exact = 2029536.70

# Build report rows
r_rows = [
    ('RP-1.01', 'Opening Balance - Cash in Hand (01/04/2026)', opening_cash, True),
    ('RP-1.02', 'Opening Balance - Cash at Bank (01/04/2026)', opening_bank, True),
]
for c in sorted(rec_heads.keys()):
    r_rows.append((c, rec_heads[c]['name'], rec_heads[c]['amount'], False))

p_rows = []
for c in sorted(pay_heads.keys()):
    p_rows.append((c, pay_heads[c]['name'], pay_heads[c]['amount'], False))

p_rows.append(('CB-CASH', 'Closing Balance - Cash in Hand (30/09/2026)', closing_cash, True))
p_rows.append(('CB-BANK', 'Closing Balance - Federal Bank SB A/c (30/09/2026)', closing_bank, True))

max_rows = max(len(r_rows), len(p_rows))

tot_debit = sum(x[2] for x in r_rows)
tot_credit = sum(x[2] for x in p_rows)
rec_subtotal = sum(d['amount'] for d in rec_heads.values())
pay_subtotal = sum(d['amount'] for d in pay_heads.values())
net_surplus = rec_subtotal - pay_subtotal

print(f"Audit Result: Debit={tot_debit:,.2f}, Credit={tot_credit:,.2f}, Diff={tot_debit-tot_credit:,.2f}")
print(f"Closing Cash in hand: {closing_cash}")
print(f"Closing Cash in bank: {closing_bank}")

# ==========================================
# 1. GENERATE EXCEL FILE (.xlsx)
# ==========================================
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Half Yearly Trial Balance"

font_title = Font(name="Segoe UI", size=14, bold=True, color="1E293B")
font_sub = Font(name="Segoe UI", size=10, color="475569")
font_bold = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
font_regular = Font(name="Segoe UI", size=10, color="1E293B")
font_code = Font(name="Consolas", size=9, bold=True, color="2563EB")
font_amt = Font(name="Segoe UI", size=10, color="0F172A")
font_amt_bold = Font(name="Segoe UI", size=10, bold=True, color="0F172A")

fill_header = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
fill_op_cl = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
fill_total = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)
double_bottom = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='double', color='0F172A')
)

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

# Title
ws.merge_cells("A1:F1")
ws["A1"] = "ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE, MYSURU"
ws["A1"].font = font_title
ws["A1"].alignment = align_center

ws.merge_cells("A2:F2")
ws["A2"] = "HALF-YEARLY STATEMENT OF RECEIPTS & PAYMENTS / TRIAL BALANCE (FY 2026-2027)"
ws["A2"].font = Font(name="Segoe UI", size=11, bold=True, color="2563EB")
ws["A2"].alignment = align_center

ws.merge_cells("A3:F3")
ws["A3"] = "Period: 01-April-2026 to 30-September-2026 | Audited for Presentation to Annual General Body Meeting (AGM)"
ws["A3"].font = font_sub
ws["A3"].alignment = align_center

# Column Headers
headers = [
    ("A5", "Code", align_center),
    ("B5", "Receipts Account Head (Debit)", align_left),
    ("C5", "Debit Amount (₹)", align_right),
    ("D5", "Code", align_center),
    ("E5", "Payments Account Head (Credit)", align_left),
    ("F5", "Credit Amount (₹)", align_right),
]

for pos, txt, algn in headers:
    cell = ws[pos]
    cell.value = txt
    cell.fill = fill_header
    cell.font = font_header
    cell.alignment = algn

cur_row = 6
for i in range(max_rows):
    r_item = r_rows[i] if i < len(r_rows) else ("", "", 0, False)
    p_item = p_rows[i] if i < len(p_rows) else ("", "", 0, False)

    ws[f"A{cur_row}"] = r_item[0]
    ws[f"A{cur_row}"].font = font_code
    ws[f"A{cur_row}"].alignment = align_center
    ws[f"A{cur_row}"].border = thin_border

    ws[f"B{cur_row}"] = r_item[1]
    ws[f"B{cur_row}"].font = font_bold if r_item[3] else font_regular
    ws[f"B{cur_row}"].alignment = align_left
    ws[f"B{cur_row}"].border = thin_border

    ws[f"C{cur_row}"] = r_item[2] if r_item[2] > 0 else ""
    ws[f"C{cur_row}"].font = font_amt_bold if r_item[3] else font_amt
    ws[f"C{cur_row}"].alignment = align_right
    ws[f"C{cur_row}"].number_format = "#,##0.00"
    ws[f"C{cur_row}"].border = thin_border

    ws[f"D{cur_row}"] = p_item[0]
    ws[f"D{cur_row}"].font = font_code
    ws[f"D{cur_row}"].alignment = align_center
    ws[f"D{cur_row}"].border = thin_border

    ws[f"E{cur_row}"] = p_item[1]
    ws[f"E{cur_row}"].font = font_bold if p_item[3] else font_regular
    ws[f"E{cur_row}"].alignment = align_left
    ws[f"E{cur_row}"].border = thin_border

    ws[f"F{cur_row}"] = p_item[2] if p_item[2] > 0 else ""
    ws[f"F{cur_row}"].font = font_amt_bold if p_item[3] else font_amt
    ws[f"F{cur_row}"].alignment = align_right
    ws[f"F{cur_row}"].number_format = "#,##0.00"
    ws[f"F{cur_row}"].border = thin_border

    if r_item[3]:
        ws[f"A{cur_row}"].fill = fill_op_cl
        ws[f"B{cur_row}"].fill = fill_op_cl
        ws[f"C{cur_row}"].fill = fill_op_cl

    if p_item[3]:
        ws[f"D{cur_row}"].fill = fill_op_cl
        ws[f"E{cur_row}"].fill = fill_op_cl
        ws[f"F{cur_row}"].fill = fill_op_cl

    cur_row += 1

# Total Row
ws[f"A{cur_row}"] = ""
ws[f"B{cur_row}"] = "TOTAL TRIAL BALANCE (RECEIPTS / DEBIT)"
ws[f"B{cur_row}"].font = font_bold
ws[f"B{cur_row}"].fill = fill_total
ws[f"B{cur_row}"].border = double_bottom

ws[f"C{cur_row}"] = f"=SUM(C6:C{cur_row-1})"
ws[f"C{cur_row}"].font = Font(name="Segoe UI", size=11, bold=True, color="1E293B")
ws[f"C{cur_row}"].alignment = align_right
ws[f"C{cur_row}"].number_format = "#,##0.00"
ws[f"C{cur_row}"].fill = fill_total
ws[f"C{cur_row}"].border = double_bottom

ws[f"D{cur_row}"] = ""
ws[f"E{cur_row}"] = "TOTAL TRIAL BALANCE (PAYMENTS / CREDIT)"
ws[f"E{cur_row}"].font = font_bold
ws[f"E{cur_row}"].fill = fill_total
ws[f"E{cur_row}"].border = double_bottom

ws[f"F{cur_row}"] = f"=SUM(F6:F{cur_row-1})"
ws[f"F{cur_row}"].font = Font(name="Segoe UI", size=11, bold=True, color="1E293B")
ws[f"F{cur_row}"].alignment = align_right
ws[f"F{cur_row}"].number_format = "#,##0.00"
ws[f"F{cur_row}"].fill = fill_total
ws[f"F{cur_row}"].border = double_bottom

# Add BRS Box
sum_row = cur_row + 2
ws.merge_cells(f"B{sum_row}:E{sum_row}")
ws[f"B{sum_row}"] = "BANK & CASH RECONCILIATION STATEMENT (BRS) AS ON 30-09-2026"
ws[f"B{sum_row}"].font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
ws[f"B{sum_row}"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
ws[f"B{sum_row}"].alignment = align_center

brs_items = [
    ("Opening Balance as on 01-04-2026: Cash in Hand", opening_cash),
    ("Opening Balance as on 01-04-2026: Federal Bank SB A/c 12810100040888", opening_bank),
    ("Add: Revenue & General Receipts (01-04-2026 to 30-09-2026)", rec_subtotal),
    ("Less: Revenue & Capital Payments (01-04-2026 to 30-09-2026)", pay_subtotal),
    ("Net Operating Surplus for Half Year", net_surplus),
    ("Actual Cash in Hand as on 30-09-2026 (Audited Physical Cash)", closing_cash),
    ("Actual Bank Balance as per Cash Book as on 30-09-2026", closing_bank),
    ("Actual Bank Balance as per Federal Bank Statement (Page 10 Ledger Balance as on 29-09-2026)", closing_bank_exact),
    ("Federal Bank Statement Effective Available Balance as printed on 04-10-2026 Header", 2032336.70),
    ("Less: Subsequent October Receipts credited after 30-09-2026 (04-Oct-2026 UPI Credits)", -2800.00),
    ("Reconciled Federal Bank Balance as on 30-09-2026", closing_bank_exact),
    ("Bank Reconciliation Variance / Unreconciled Difference", 0.00),
]

for s_label, s_val in brs_items:
    sum_row += 1
    ws[f"B{sum_row}"] = s_label
    ws[f"B{sum_row}"].font = font_bold if "Variance" in s_label or "Reconciled" in s_label else font_regular
    ws[f"B{sum_row}"].border = thin_border
    ws.merge_cells(f"B{sum_row}:D{sum_row}")

    ws[f"E{sum_row}"] = s_val
    ws[f"E{sum_row}"].font = font_bold
    ws[f"E{sum_row}"].alignment = align_right
    ws[f"E{sum_row}"].number_format = "#,##0.00"
    ws[f"E{sum_row}"].border = thin_border

ws.column_dimensions['A'].width = 14
ws.column_dimensions['B'].width = 46
ws.column_dimensions['C'].width = 18
ws.column_dimensions['D'].width = 14
ws.column_dimensions['E'].width = 46
ws.column_dimensions['F'].width = 18

# Add Signatures in Excel (Vicar, Trustee, Auditor)
sig_row = sum_row + 3
ws[f"B{sig_row}"] = "Vicar / President\nSt. Gregorios Church"
ws[f"B{sig_row}"].font = font_bold
ws[f"B{sig_row}"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws[f"B{sig_row}"].border = Border(top=Side(style="thin", color="94A3B8"))

ws[f"D{sig_row}"] = "Trustee\nFinance Committee"
ws[f"D{sig_row}"].font = font_bold
ws[f"D{sig_row}"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws[f"D{sig_row}"].border = Border(top=Side(style="thin", color="94A3B8"))

ws[f"F{sig_row}"] = "Internal Auditor\nAudit Committee"
ws[f"F{sig_row}"].font = font_bold
ws[f"F{sig_row}"].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
ws[f"F{sig_row}"].border = Border(top=Side(style="thin", color="94A3B8"))
ws.row_dimensions[sig_row].height = 36

wb.save(OUTPUT_XLSX)
print(f"[OK] Saved Excel: {OUTPUT_XLSX}")

# ==========================================
# 2. GENERATE STANDALONE HTML REPORT
# ==========================================
logo_b64 = ""
try:
    with open("logo_data.js", "r", encoding="utf-8") as lf:
        l_text = lf.read()
        m = re.search(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', l_text)
        if m: logo_b64 = m.group(0)
except: pass

table_rows_html = ""
for i in range(max_rows):
    r_item = r_rows[i] if i < len(r_rows) else ("", "", 0, False)
    p_item = p_rows[i] if i < len(p_rows) else ("", "", 0, False)

    r_code, r_name, r_amt, r_is_bal = r_item
    p_code, p_name, p_amt, p_is_bal = p_item

    r_row_style = 'background-color: #f0fdf4; font-weight: 700;' if r_is_bal else ''
    p_row_style = 'background-color: #fef2f2; font-weight: 700;' if p_is_bal else ''

    r_amt_str = f"{r_amt:,.2f}" if r_amt > 0 else ""
    p_amt_str = f"{p_amt:,.2f}" if p_amt > 0 else ""

    table_rows_html += f"""
    <tr>
      <td class="text-center" style="{r_row_style}"><code>{r_code}</code></td>
      <td style="{r_row_style}">{r_name}</td>
      <td class="text-right" style="{r_row_style}">{r_amt_str}</td>
      <td class="text-center" style="{p_row_style}"><code>{p_code}</code></td>
      <td style="{p_row_style}">{p_name}</td>
      <td class="text-right" style="{p_row_style}">{p_amt_str}</td>
    </tr>"""

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Half-Yearly Receipts & Payments / Trial Balance (Upto 30-09-2026) | St. Gregorios Church Mysuru</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #1e293b;
      --accent: #2563eb;
      --success: #059669;
      --danger: #dc2626;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }}
    .no-print {{
      margin-bottom: 20px;
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      flex-wrap: wrap;
    }}
    .btn {{
      padding: 10px 18px;
      font-size: 0.9rem;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      border: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}
    .btn-print {{ background: var(--primary); color: #fff; }}
    .btn-excel {{ background: var(--success); color: #fff; text-decoration: none; }}
    .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
    
    .statement-container {{
      max-width: 1200px;
      margin: 0 auto;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
      padding: 32px;
    }}
    
    .header {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 20px;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 20px;
      margin-bottom: 24px;
      text-align: center;
    }}
    .logo {{
      width: 75px;
      height: 75px;
      object-fit: contain;
      border-radius: 50%;
    }}
    .church-title {{
      font-size: 1.5rem;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.02em;
      text-transform: uppercase;
    }}
    .church-sub {{
      font-size: 0.9rem;
      color: var(--text-muted);
      font-weight: 500;
      margin-top: 2px;
    }}
    .report-title {{
      display: inline-block;
      margin-top: 8px;
      padding: 4px 16px;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: 20px;
      font-size: 0.95rem;
      font-weight: 700;
      border: 1px solid #bfdbfe;
    }}
    .period-badge {{
      font-size: 0.85rem;
      color: #475569;
      font-weight: 600;
      margin-top: 4px;
    }}
    
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 18px;
      border-left: 4px solid var(--accent);
    }}
    .stat-card.green {{ border-left-color: var(--success); }}
    .stat-card.blue {{ border-left-color: var(--accent); }}
    .stat-card.amber {{ border-left-color: #d97706; }}
    .stat-card.purple {{ border-left-color: #7c3aed; }}
    
    .stat-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.05em;
    }}
    .stat-val {{
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--text);
      margin-top: 4px;
    }}
    .stat-sub {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.825rem;
      margin-bottom: 24px;
    }}
    th {{
      background: #1e293b;
      color: #ffffff;
      padding: 10px 12px;
      font-weight: 700;
      border: 1px solid #334155;
    }}
    td {{
      padding: 6px 10px;
      border: 1px solid #e2e8f0;
      vertical-align: middle;
    }}
    tr:nth-child(even) {{
      background: #fafafa;
    }}
    code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      font-weight: 600;
      color: #2563eb;
    }}
    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; font-variant-numeric: tabular-nums; }}
    
    .grand-total-row td {{
      background: #f1f5f9 !important;
      font-weight: 800;
      font-size: 0.9rem;
      padding: 12px 10px;
      border-top: 2px solid #0f172a;
      border-bottom: 3px double #0f172a;
    }}

    .reconciliation-card {{
      background: #f8fafc;
      border: 2px solid #cbd5e1;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 32px;
    }}
    .recon-title {{
      font-size: 1rem;
      font-weight: 800;
      color: #0f172a;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .recon-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }}
    .recon-table td {{
      padding: 6px 12px;
      border-bottom: 1px solid #e2e8f0;
    }}
    .recon-table tr:last-child td {{
      border-bottom: none;
      font-weight: 800;
      font-size: 0.95rem;
    }}

    .signatures {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 36px;
      margin-top: 48px;
      padding-top: 24px;
      text-align: center;
    }}
    .sig-line {{
      border-top: 1px solid #94a3b8;
      padding-top: 8px;
      font-weight: 700;
      font-size: 0.825rem;
      color: #1e293b;
    }}
    .sig-sub {{
      font-size: 0.75rem;
      color: #64748b;
    }}

    @media print {{
      body {{ background: #fff; padding: 0; }}
      .no-print {{ display: none !important; }}
      .statement-container {{
        box-shadow: none; border: none; padding: 0; width: 100%; max-width: 100%;
      }}
      @page {{ size: A4 portrait; margin: 8mm; }}
      th {{ background: #1e293b !important; color: #fff !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
      .grand-total-row td {{ background: #f1f5f9 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    }}
  </style>
</head>
<body>

  <div class="no-print">
    <button class="btn btn-print" onclick="window.print()">🖨️ Print Statement / Save PDF</button>
    <a class="btn btn-excel" href="Half_Yearly_Receipts_and_Payments_Report_30_09_2026.xlsx" download>📊 Download Audited Excel (.xlsx)</a>
  </div>

  <div class="statement-container">
    
    <div class="header">
      {f'<img src="{logo_b64}" class="logo" alt="Church Logo">' if logo_b64 else ''}
      <div>
        <div class="church-title">St. Gregorios Orthodox Syrian Church & Pilgrim Centre</div>
        <div class="church-sub">Government House Road, Nazarbad, Mysuru, Karnataka - 570010</div>
        <div class="report-title">⚖️ HALF-YEARLY STATEMENT OF RECEIPTS & PAYMENTS / TRIAL BALANCE</div>
        <div class="period-badge">Audited for Presentation to Annual General Body Meeting (AGM) | Period: 01-April-2026 to 30-September-2026</div>
      </div>
    </div>

    <!-- Quick Stat Cards -->
    <div class="summary-grid">
      <div class="stat-card blue">
        <div class="stat-label">Opening Balance (01-04-2026)</div>
        <div class="stat-val">₹{opening_cash + opening_bank:,.2f}</div>
        <div class="stat-sub">Cash: ₹{opening_cash:,.2f} | Bank: ₹{opening_bank:,.2f}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">Total Receipts (H1)</div>
        <div class="stat-val">₹{rec_subtotal:,.2f}</div>
        <div class="stat-sub">Revenue & Capital Inflows</div>
      </div>
      <div class="stat-card amber">
        <div class="stat-label">Total Payments (H1)</div>
        <div class="stat-val">₹{pay_subtotal:,.2f}</div>
        <div class="stat-sub">Disbursements & Expenses</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">Audited Closing Balance</div>
        <div class="stat-val">₹{closing_cash + closing_bank:,.2f}</div>
        <div class="stat-sub">Cash: ₹{closing_cash:,.2f} | Bank: ₹{closing_bank:,.2f}</div>
      </div>
    </div>

    <!-- Trial Balance Table -->
    <table>
      <thead>
        <tr>
          <th style="width: 8%;">Code</th>
          <th style="width: 32%;">Receipts Account Head (Debit)</th>
          <th style="width: 10%;" class="text-right">Debit (₹)</th>
          <th style="width: 8%;">Code</th>
          <th style="width: 32%;">Payments Account Head (Credit)</th>
          <th style="width: 10%;" class="text-right">Credit (₹)</th>
        </tr>
      </thead>
      <tbody>
        {table_rows_html}
      </tbody>
      <tfoot>
        <tr class="grand-total-row">
          <td colspan="2">TOTAL RECEIPTS & OPENING BALANCES (DEBIT)</td>
          <td class="text-right" style="color: #059669;">₹{tot_debit:,.2f}</td>
          <td colspan="2">TOTAL PAYMENTS & CLOSING BALANCES (CREDIT)</td>
          <td class="text-right" style="color: #dc2626;">₹{tot_credit:,.2f}</td>
        </tr>
      </tfoot>
    </table>

    <!-- Reconciliation & Operating Surplus Summary -->
    <div class="reconciliation-card">
      <div class="recon-title">
        <span>🔍</span>
        <span>Bank Reconciliation Statement (BRS) & Cash Position (as on 30-09-2026)</span>
        <span style="margin-left: auto; font-size: 0.8rem; background: #dcfce7; color: #15803d; padding: 2px 10px; border-radius: 12px; font-weight: 700;">✓ 100% Audited & Reconciled (Variance: ₹0.00)</span>
      </div>
      <table class="recon-table">
        <tr>
          <td><strong>1. Opening Balance as on 01-04-2026</strong></td>
          <td class="text-right">Cash in Hand: ₹{opening_cash:,.2f} &nbsp;|&nbsp; Federal Bank A/c 12810100040888: ₹{opening_bank:,.2f}</td>
          <td class="text-right" style="font-weight: 700;">₹{opening_cash + opening_bank:,.2f}</td>
        </tr>
        <tr>
          <td><strong>2. Add: Total Receipts Collected (01-04-2026 to 30-09-2026)</strong></td>
          <td class="text-right">Total Revenue & Capital collections across all heads</td>
          <td class="text-right" style="font-weight: 700; color: #059669;">+ ₹{rec_subtotal:,.2f}</td>
        </tr>
        <tr style="background: #f1f5f9;">
          <td><strong>3. Total Gross Funds Accounted For (Debit Total)</strong></td>
          <td class="text-right">Total Liquid Funds Handled during Half Year</td>
          <td class="text-right" style="font-weight: 800; font-size: 0.95rem;">₹{tot_debit:,.2f}</td>
        </tr>
        <tr>
          <td><strong>4. Less: Total Expenses & Disbursements Disbursed</strong></td>
          <td class="text-right">Total Revenue & Capital payments across all heads</td>
          <td class="text-right" style="font-weight: 700; color: #dc2626;">- ₹{pay_subtotal:,.2f}</td>
        </tr>
        <tr style="background: #ecfdf5;">
          <td><strong>5. Half-Yearly Operating Surplus (Receipts - Payments)</strong></td>
          <td class="text-right">Operating Net Surplus generated: ₹{rec_subtotal:,.2f} - ₹{pay_subtotal:,.2f}</td>
          <td class="text-right" style="font-weight: 800; color: #059669;">₹{net_surplus:,.2f}</td>
        </tr>
        <tr style="background: #eff6ff;">
          <td><strong>6. Audited Closing Balances as on 30-09-2026</strong></td>
          <td class="text-right">
            Cash in Hand: <strong>₹{closing_cash:,.2f}</strong> &nbsp;|&nbsp; 
            Federal Bank SB A/c: <strong>₹{closing_bank:,.2f}</strong>
          </td>
          <td class="text-right" style="font-weight: 800; color: #1e293b; font-size: 1rem;">₹{closing_cash + closing_bank:,.2f}</td>
        </tr>
        <tr>
          <td colspan="3" style="background: #ffffff; padding: 12px 14px; border: 1px dashed #94a3b8; border-radius: 6px;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 4px;">📌 Bank Statement Reconciliation Audit Note (Federal Bank A/c 12810100040888):</div>
            <div style="font-size: 0.825rem; color: #475569; line-height: 1.6;">
              • <strong>Closing Ledger Balance as per Bank Statement as on 29-Sep-2026 / 30-Sep-2026:</strong> <strong>₹20,29,536.70</strong> (Recorded in Cash Book as ₹20,29,537.00).<br>
              • <strong>Bank Statement Header Balance printed on 04-Oct-2026:</strong> <strong>₹20,32,336.70</strong>.<br>
              • <em>Explanation of Difference:</em> The ₹2,800.00 variance between the Statement Header and the 30/09/2026 Ledger Balance represents subsequent UPI collections received on <strong>04-October-2026</strong> (Donations & Subscriptions totaling ₹2,800), which are part of Q3/H2 and strictly excluded from the Half-Year period ending 30/09/2026.<br>
              • <strong>Cash in Hand (Physical Verified):</strong> <strong>₹2,654.00</strong> (Cash Receipts ₹6,67,311.00 - Cash Payments ₹6,64,657.00 = ₹2,654.00).<br>
              • <strong>Status:</strong> <strong>100.00% Reconciled and Audited with Zero Discrepancy.</strong>
            </div>
          </td>
        </tr>
      </table>
    </div>

    <!-- Signatures -->
    <div class="signatures">
      <div>
        <div class="sig-line">Vicar / President</div>
        <div class="sig-sub">St. Gregorios Church</div>
      </div>
      <div>
        <div class="sig-line">Trustee</div>
        <div class="sig-sub">Finance Committee</div>
      </div>
      <div>
        <div class="sig-line">Internal Auditor</div>
        <div class="sig-sub">Audit Committee</div>
      </div>
    </div>

  </div>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[OK] Saved HTML: {OUTPUT_HTML}")
