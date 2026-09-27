import re
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# 1. Parse data.js
with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
    text = f.read()

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

ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,\s*members', text, re.DOTALL)
if not ind_match:
    ind_match = re.search(r'individual\s*:\s*(\[.*?\])\s*,', text, re.DOTALL)
ind_text = ind_match.group(1) if ind_match else ""
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

# Extract member ledger dynamic totals from cashbook
# Build member list (unique members)
members_map = {}
for r in ind_rows[4:]:
    sl = str(r.get('A', '') or '').strip()
    reg = str(r.get('B', '') or '').strip()
    name = str(r.get('C', '') or '').strip()
    sub_upto = str(r.get('D', '') or '').strip()
    if not reg and not name: continue
    if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL': continue
    if reg not in members_map:
        members_map[reg] = {
            'sl': sl,
            'reg': reg,
            'name': name,
            'sub_upto': sub_upto,
            'contributions': {},
            'total': 0
        }

# Aggregate dynamic contributions from Cashbook for each member & non-member
# Receipts (Left side of Cashbook)
nm_receipts = []
for r in cb_entries:
    date = str(r.get('A', '') or '').strip()
    rec_no = str(r.get('B', '') or '').strip()
    reg_no = str(r.get('C', '') or '').strip()
    name = str(r.get('D', '') or '').strip()
    head = str(r.get('E', '') or '').strip()
    code = str(r.get('F', '') or '').strip()
    details = str(r.get('G', '') or '').strip()
    amt_h = str(r.get('H', '') or '').replace(',', '').strip()
    amt_i = str(r.get('I', '') or '').replace(',', '').strip()
    
    try:
        cash_amt = float(amt_h) if amt_h else 0
    except: cash_amt = 0
    try:
        bank_amt = float(amt_i) if amt_i else 0
    except: bank_amt = 0
    
    tot_amt = cash_amt + bank_amt
    if tot_amt == 0: continue
    
    is_nm = (reg_no.upper() in ['NM', 'NON MEMBER', 'NON-MEMBER', ''] or 'NM' in reg_no.upper() or 'NON MEMBER' in name.upper() or '- NM' in name.upper())
    
    if is_nm:
        nm_receipts.append({
            'date': date,
            'rec_no': rec_no,
            'reg_no': reg_no or 'NM',
            'name': name,
            'head': head,
            'code': code,
            'details': details,
            'cash': cash_amt,
            'bank': bank_amt,
            'total': tot_amt
        })
        
    if reg_no in members_map:
        m = members_map[reg_no]
        m['contributions'][head] = m['contributions'].get(head, 0) + tot_amt
        m['total'] += tot_amt

print(f"Extracted {len(members_map)} members and {len(nm_receipts)} external non-member receipts.")
