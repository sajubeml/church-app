import re
import json
import os
import shutil
import zipfile
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def parse_church_data():
    with open('c:\\CASHBOOK_APP\\data.js', 'r', encoding='utf-8') as f:
        text = f.read()

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
    return ind_rows, header_row

def clean_member_filename(name, reg):
    # Keep member name human-readable, strip invalid filesystem characters
    clean = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    if not clean:
        clean = f"Member_Reg_{reg}"
    return f"{clean}.pdf"

def generate_individual_pdfs():
    ind_rows, header_row = parse_church_data()

    output_dir = "c:\\CASHBOOK_APP\\Individual_Member_PDF_Statements"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    member_map = {}

    for r in ind_rows[4:]:
        sl = str(r.get('A', '') or '').strip()
        reg = str(r.get('B', '') or '').strip()
        name = str(r.get('C', '') or '').strip()
        sub_upto = str(r.get('D', '') or '').strip()
        
        if not reg and not name: continue
        if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL': continue
        
        if reg not in member_map:
            member_map[reg] = {
                'sl': sl,
                'reg': reg,
                'name': name,
                'sub_upto': sub_upto,
                'contributions': {},
                'total': 0
            }
        
        m = member_map[reg]
        for k, h_name in header_row.items():
            if k in ['A', 'B', 'C', 'D', 'AM']: continue
            val_str = str(r.get(k, '') or '').replace(',', '').strip()
            try: val = float(val_str)
            except: val = 0
            if val > 0:
                m['contributions'][h_name] = m['contributions'].get(h_name, 0) + val

    for reg, m in member_map.items():
        m['total'] = sum(m['contributions'].values())

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor("#1A365D"), alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#4A5568"), alignment=1
    )
    label_style = ParagraphStyle(
        'LabelStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor("#1A365D")
    )
    val_style = ParagraphStyle(
        'ValStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor("#2D3748")
    )
    cell_head_style = ParagraphStyle(
        'CellHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white, alignment=1
    )
    cell_text_style = ParagraphStyle(
        'CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor("#2D3748")
    )
    cell_bold_style = ParagraphStyle(
        'CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor("#1A365D")
    )

    generated_files = []
    used_filenames = set()

    for reg, m in member_map.items():
        filename = clean_member_filename(m['name'], reg)
        
        # Handle duplicate member names safely
        if filename in used_filenames:
            base, ext = os.path.splitext(filename)
            filename = f"{base} (Reg #{reg}){ext}"
        used_filenames.add(filename)
        
        filepath = os.path.join(output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=portrait(A4),
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        elements = []

        # Title Header
        elements.append(Paragraph("ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE", title_style))
        elements.append(Paragraph("Government House Road, Nazarbad, Mysuru, Karnataka — 570010", subtitle_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph("<b>MEMBER CONTRIBUTION STATEMENT</b>", ParagraphStyle('SubHeader', parent=subtitle_style, fontSize=12, leading=15, textColor=colors.HexColor("#2B6CB0"))))
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceAfter=12))

        # Member Profile Card Box
        profile_data = [
            [
                Paragraph("<b>Register No:</b>", label_style),
                Paragraph(f"<b>#{m['reg']}</b>", ParagraphStyle('RegVal', parent=val_style, fontName='Helvetica-Bold', textColor=colors.HexColor("#2B6CB0"))),
                Paragraph("<b>Subscription Paid Upto:</b>", label_style),
                Paragraph(f"<b>{m['sub_upto'] or '-'}</b>", val_style)
            ],
            [
                Paragraph("<b>Member Name:</b>", label_style),
                Paragraph(f"<b>{m['name']}</b>", val_style),
                Paragraph("<b>Total Contribution:</b>", label_style),
                Paragraph(f"<b>₹ {m['total']:,.2f}</b>", ParagraphStyle('TotVal', parent=val_style, fontName='Helvetica-Bold', textColor=colors.HexColor("#2F855A")))
            ]
        ]

        profile_table = Table(profile_data, colWidths=[100, 150, 130, 135])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(profile_table)
        elements.append(Spacer(1, 15))

        # Itemized Contributions Table
        elements.append(Paragraph("<b>Itemized Account Head Breakdown:</b>", ParagraphStyle('SecHead', parent=label_style, fontSize=11, leading=14, textColor=colors.HexColor("#1A365D"))))
        elements.append(Spacer(1, 6))

        item_headers = [
            Paragraph("Sl", cell_head_style),
            Paragraph("Account Head / Collection Category", cell_head_style),
            Paragraph("Contribution Amount (₹)", cell_head_style)
        ]
        item_table_data = [item_headers]

        contrib_items = m['contributions']
        if not contrib_items:
            empty_row = [
                Paragraph("-", cell_text_style),
                Paragraph("<i>No active contributions recorded for the current period</i>", cell_text_style),
                Paragraph("₹ 0.00", cell_text_style)
            ]
            item_table_data.append(empty_row)
        else:
            for idx, (h_name, amt) in enumerate(sorted(contrib_items.items(), key=lambda x: x[0]), 1):
                row = [
                    Paragraph(str(idx), cell_text_style),
                    Paragraph(h_name, cell_bold_style),
                    Paragraph(f"₹ {amt:,.2f}", cell_bold_style)
                ]
                item_table_data.append(row)

        # Total Row
        total_row = [
            Paragraph("", cell_head_style),
            Paragraph("<b>TOTAL MEMBER CONTRIBUTION</b>", cell_head_style),
            Paragraph(f"<b>₹ {m['total']:,.2f}</b>", cell_head_style)
        ]
        item_table_data.append(total_row)

        it = Table(item_table_data, colWidths=[40, 335, 140])
        it_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ]

        for i in range(1, len(item_table_data) - 1):
            bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else colors.white
            it_style.append(('BACKGROUND', (0, i), (-1, i), bg))

        it.setStyle(TableStyle(it_style))
        elements.append(it)

        elements.append(Spacer(1, 40))

        # Signature & Seal Box
        sig_data = [
            [
                Paragraph("Date: _____________", cell_text_style),
                Paragraph("Verified By: Trustee / Vicar", ParagraphStyle('CenterSig', parent=cell_text_style, alignment=1)),
                Paragraph("Authorized Signature & Seal", ParagraphStyle('RightSig', parent=cell_text_style, alignment=2))
            ]
        ]
        sig_table = Table(sig_data, colWidths=[160, 195, 160])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('PADDING', (0,0), (-1,-1), 0)
        ]))
        elements.append(KeepTogether(sig_table))

        doc.build(elements)
        generated_files.append((filename, filepath))

    print(f"Successfully generated {len(generated_files)} individual member PDF statements named by Member Name.")

    # Create ZIP file for easy bulk download
    zip_path = "c:\\CASHBOOK_APP\\Individual_Member_PDF_Statements.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fname, fpath in generated_files:
            zipf.write(fpath, fname)

    print(f"Created ZIP file: {zip_path}")

if __name__ == '__main__':
    generate_individual_pdfs()
