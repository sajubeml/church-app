import re
import json
import os
import shutil
import zipfile
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def parse_church_data():
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
    return cb_entries, ind_rows, header_row

def clean_member_filename(name, reg):
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    if not clean:
        clean = f"Member_Reg_{reg}"
    return f"{clean}.pdf"

def generate_individual_pdfs():
    cb_entries, ind_rows, header_row = parse_church_data()

    output_dir = "c:\\CASHBOOK_APP\\Individual_Member_PDF_Statements"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Find logo path
    logo_path = "c:\\CASHBOOK_APP\\church_logo.png"
    if not os.path.exists(logo_path):
        logo_path = "c:\\CASHBOOK_APP\\church_logo.jpg"

    member_map = {}

    for r in ind_rows[4:]:
        sl = str(r.get('A', '') or '').strip()
        reg = str(r.get('B', '') or '').strip()
        name = str(r.get('C', '') or '').strip()
        sub_upto = str(r.get('D', '') or '').strip()
        
        if not reg and not name: continue
        if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL': continue
        
        # FILTER 1: Skip NM non-members
        is_nm = (reg.upper() in ['NM', 'NON MEMBER', 'NON-MEMBER', ''] or 
                 'NM' in reg.upper() or 
                 'NON MEMBER' in name.upper() or 
                 '- NM' in name.upper())
        if is_nm:
            continue
        
        if reg not in member_map:
            member_map[reg] = {
                'sl': sl,
                'reg': reg,
                'name': name,
                'sub_upto': sub_upto,
                'summary_heads': {},
                'receipt_transactions': [],
                'total': 0
            }
        
        m = member_map[reg]
        for k, h_name in header_row.items():
            if k in ['A', 'B', 'C', 'D', 'AM']: continue
            val_str = str(r.get(k, '') or '').replace(',', '').strip()
            try: val = float(val_str)
            except: val = 0
            if val > 0:
                m['summary_heads'][h_name] = m['summary_heads'].get(h_name, 0) + val

    # Map cashbook receipt transactions for each member
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
        
        try: cash_amt = float(amt_h) if amt_h else 0
        except: cash_amt = 0
        try: bank_amt = float(amt_i) if amt_i else 0
        except: bank_amt = 0
        tot_amt = cash_amt + bank_amt
        
        if reg_no in member_map and tot_amt > 0:
            member_map[reg_no]['receipt_transactions'].append({
                'date': date,
                'rec_no': rec_no,
                'head': head,
                'code': code,
                'details': details,
                'amount': tot_amt
            })

    # Calculate total and FILTER 2: Skip members who have not paid anything (total == 0)
    active_paying_members = {}
    for reg, m in member_map.items():
        if m['receipt_transactions']:
            m['total'] = sum(t['amount'] for t in m['receipt_transactions'])
        else:
            m['total'] = sum(m['summary_heads'].values())
            
        if m['total'] > 0:
            active_paying_members[reg] = m

    print(f"Total active paying registered members (excluding NM & 0 contributors): {len(active_paying_members)}")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=colors.HexColor("#1A365D"), alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor("#4A5568"), alignment=0
    )
    label_style = ParagraphStyle(
        'LabelStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor("#1A365D")
    )
    val_style = ParagraphStyle(
        'ValStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor("#2D3748")
    )
    cell_head_style = ParagraphStyle(
        'CellHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.white, alignment=1
    )
    cell_text_style = ParagraphStyle(
        'CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#2D3748")
    )
    cell_bold_style = ParagraphStyle(
        'CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#1A365D")
    )

    generated_files = []
    used_filenames = set()
    current_date_str = datetime.now().strftime("%d-%m-%Y")

    for reg, m in active_paying_members.items():
        filename = clean_member_filename(m['name'], reg)
        if filename in used_filenames:
            base, ext = os.path.splitext(filename)
            filename = f"{base} (Reg #{reg}){ext}"
        used_filenames.add(filename)
        
        filepath = os.path.join(output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=portrait(A4),
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []

        # 1. HEADER WITH LOGO
        header_table_data = []
        if os.path.exists(logo_path):
            img = Image(logo_path, width=54, height=54)
            header_text = [
                Paragraph("ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE", title_style),
                Paragraph("Government House Road, Nazarbad, Mysuru, Karnataka — 570010", subtitle_style),
                Paragraph("<b>MEMBER CONTRIBUTION STATEMENT & RECEIPT SUMMARY</b>", ParagraphStyle('SubHeader', parent=subtitle_style, fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#2B6CB0")))
            ]
            header_table_data = [[img, header_text]]
            col_w = [62, 461]
        else:
            header_text = [
                Paragraph("ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE", title_style),
                Paragraph("Government House Road, Nazarbad, Mysuru, Karnataka — 570010", subtitle_style),
                Paragraph("<b>MEMBER CONTRIBUTION STATEMENT & RECEIPT SUMMARY</b>", ParagraphStyle('SubHeader', parent=subtitle_style, fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor("#2B6CB0")))
            ]
            header_table_data = [[header_text]]
            col_w = [523]

        htable = Table(header_table_data, colWidths=col_w)
        htable.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(htable)
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceAfter=10))

        # Build list of Rt Nos for Profile Card
        rt_nos = list(set([t['rec_no'] for t in m['receipt_transactions'] if t['rec_no']]))
        rt_str = ", ".join(sorted(rt_nos, key=lambda x: str(x))) if rt_nos else f"STMT-REG-#{reg}"

        # 2. MEMBER PROFILE & RECEIPT REF CARD
        profile_data = [
            [
                Paragraph("<b>Register No:</b>", label_style),
                Paragraph(f"<b>#{m['reg']}</b>", ParagraphStyle('RegVal', parent=val_style, fontName='Helvetica-Bold', textColor=colors.HexColor("#2B6CB0"))),
                Paragraph("<b>Statement Date:</b>", label_style),
                Paragraph(f"<b>{current_date_str}</b>", val_style)
            ],
            [
                Paragraph("<b>Member Name:</b>", label_style),
                Paragraph(f"<b>{m['name']}</b>", val_style),
                Paragraph("<b>Rt No. / Ref:</b>", label_style),
                Paragraph(f"<b>{rt_str}</b>", ParagraphStyle('RtVal', parent=val_style, fontSize=8.5, textColor=colors.HexColor("#2D3748")))
            ],
            [
                Paragraph("<b>Subscription Upto:</b>", label_style),
                Paragraph(f"<b>{m['sub_upto'] or '-'}</b>", val_style),
                Paragraph("<b>Total Contributions:</b>", label_style),
                Paragraph(f"<b>₹ {m['total']:,.2f}</b>", ParagraphStyle('TotVal', parent=val_style, fontName='Helvetica-Bold', textColor=colors.HexColor("#2F855A")))
            ]
        ]

        profile_table = Table(profile_data, colWidths=[105, 155, 120, 143])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(profile_table)
        elements.append(Spacer(1, 12))

        # 3. ITEMIZED RECEIPT TRANSACTIONS TABLE
        elements.append(Paragraph("<b>Itemized Receipt Transactions & Contributions:</b>", ParagraphStyle('SecHead', parent=label_style, fontSize=10.5, leading=13, textColor=colors.HexColor("#1A365D"))))
        elements.append(Spacer(1, 5))

        item_headers = [
            Paragraph("Sl", cell_head_style),
            Paragraph("Date", cell_head_style),
            Paragraph("Rt No.", cell_head_style),
            Paragraph("Accounts Head / Category", cell_head_style),
            Paragraph("Details / Remarks", cell_head_style),
            Paragraph("Amount (₹)", cell_head_style)
        ]
        item_table_data = [item_headers]

        if m['receipt_transactions']:
            for idx, tx in enumerate(m['receipt_transactions'], 1):
                row = [
                    Paragraph(str(idx), cell_text_style),
                    Paragraph(tx['date'] or '-', cell_text_style),
                    Paragraph(f"<b>{tx['rec_no']}</b>" if tx['rec_no'] else "-", cell_text_style),
                    Paragraph(tx['head'], cell_bold_style),
                    Paragraph(tx['details'] or '-', cell_text_style),
                    Paragraph(f"₹ {tx['amount']:,.2f}", cell_bold_style)
                ]
                item_table_data.append(row)
        else:
            contrib_items = m['summary_heads']
            for idx, (h_name, amt) in enumerate(sorted(contrib_items.items(), key=lambda x: x[0]), 1):
                row = [
                    Paragraph(str(idx), cell_text_style), Paragraph("-", cell_text_style), Paragraph("-", cell_text_style),
                    Paragraph(h_name, cell_bold_style), Paragraph("-", cell_text_style), Paragraph(f"₹ {amt:,.2f}", cell_bold_style)
                ]
                item_table_data.append(row)

        # Total Row
        total_row = [
            Paragraph("", cell_head_style),
            Paragraph("", cell_head_style),
            Paragraph("", cell_head_style),
            Paragraph("<b>TOTAL MEMBER CONTRIBUTIONS</b>", cell_head_style),
            Paragraph("", cell_head_style),
            Paragraph(f"<b>₹ {m['total']:,.2f}</b>", cell_head_style)
        ]
        item_table_data.append(total_row)

        it = Table(item_table_data, colWidths=[25, 65, 55, 175, 115, 88])
        it_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ]

        for i in range(1, len(item_table_data) - 1):
            bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else colors.white
            it_style.append(('BACKGROUND', (0, i), (-1, i), bg))

        it.setStyle(TableStyle(it_style))
        elements.append(it)

        elements.append(Spacer(1, 35))

        # 4. SIGNATURE & SEAL BOX
        sig_data = [
            [
                Paragraph(f"Date: <b>{current_date_str}</b>", cell_text_style),
                Paragraph("Verified By: Trustee / Vicar", ParagraphStyle('CenterSig', parent=cell_text_style, alignment=1)),
                Paragraph("Authorized Signature & Seal", ParagraphStyle('RightSig', parent=cell_text_style, alignment=2))
            ]
        ]
        sig_table = Table(sig_data, colWidths=[160, 203, 160])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('PADDING', (0,0), (-1,-1), 0)
        ]))
        elements.append(KeepTogether(sig_table))

        doc.build(elements)
        generated_files.append((filename, filepath))

    print(f"Generated {len(generated_files)} active paying member PDF statements in {output_dir}")

    # Create ZIP file
    zip_path = "c:\\CASHBOOK_APP\\Individual_Member_PDF_Statements.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fname, fpath in generated_files:
            zipf.write(fpath, fname)

    print(f"Created filtered ZIP file: {zip_path}")

if __name__ == '__main__':
    generate_individual_pdfs()
