import re
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header line & text on page 2+
        if self._pageNumber > 0:
            # Header
            self.drawString(36, 565, "St. Gregorios Orthodox Syrian Church & Pilgrim Centre, Mysuru — Contribution Statement")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(36, 558, 806, 558)
            
            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(806, 25, page_text)
            self.drawString(36, 25, "Confidential — Generated from Church Accounting System")
            self.line(36, 35, 806, 35)
        self.restoreState()


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

    return cb_entries, ind_rows


def generate_external_nm_pdf():
    cb_entries, ind_rows = parse_church_data()
    
    # Filter external non-member receipts (NM)
    nm_receipts = []
    total_cash = 0
    total_bank = 0
    total_overall = 0
    
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
        if tot_amt == 0: continue
        
        is_nm = (reg_no.upper() in ['NM', 'NON MEMBER', 'NON-MEMBER', ''] or 
                 'NM' in reg_no.upper() or 
                 'NON MEMBER' in name.upper() or 
                 '- NM' in name.upper())
        
        if is_nm:
            mode = "Cash" if cash_amt > 0 and bank_amt == 0 else ("Bank" if bank_amt > 0 and cash_amt == 0 else "Cash/Bank")
            nm_receipts.append({
                'date': date,
                'rec_no': rec_no,
                'reg_no': reg_no or 'NM',
                'name': name or 'External Donor / NM',
                'head': head,
                'code': code,
                'details': details,
                'mode': mode,
                'amount': tot_amt
            })
            total_cash += cash_amt
            total_bank += bank_amt
            total_overall += tot_amt

    pdf_filename = "c:\\CASHBOOK_APP\\St_Gregorios_Church_External_Non_Member_Contributions.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(A4),
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        alignment=1
    )
    cell_head_style = ParagraphStyle(
        'CellHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    cell_text_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748")
    )
    cell_bold_style = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1A365D")
    )

    elements = []
    
    # Title Header
    elements.append(Paragraph("ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE", title_style))
    elements.append(Paragraph("Government House Road, Nazarbad, Mysuru, Karnataka — 570010", subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>EXTERNAL & NON-MEMBER (NM) CONTRIBUTIONS LIST</b>", ParagraphStyle('SubHeader', parent=subtitle_style, fontSize=12, leading=15, textColor=colors.HexColor("#2B6CB0"))))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

    # Summary Stats Box
    summary_data = [
        [
            Paragraph("<b>Total Non-Member Receipts:</b> " + str(len(nm_receipts)), cell_text_style),
            Paragraph("<b>Total Cash Receipts:</b> ₹ {:,.2f}".format(total_cash), cell_text_style),
            Paragraph("<b>Total Bank Receipts:</b> ₹ {:,.2f}".format(total_bank), cell_text_style),
            Paragraph("<b>GRAND TOTAL CONTRIBUTIONS:</b> ₹ {:,.2f}".format(total_overall), cell_bold_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180, 230])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3182CE")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BEE3F8")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # Table Header
    headers = [
        Paragraph("Sl", cell_head_style),
        Paragraph("Date", cell_head_style),
        Paragraph("Rec No", cell_head_style),
        Paragraph("Reg No", cell_head_style),
        Paragraph("Name of Contributor / HoF", cell_head_style),
        Paragraph("Accounts Head", cell_head_style),
        Paragraph("Code", cell_head_style),
        Paragraph("Details / Remarks", cell_head_style),
        Paragraph("Mode", cell_head_style),
        Paragraph("Amount (₹)", cell_head_style)
    ]

    table_data = [headers]

    for idx, r in enumerate(nm_receipts, 1):
        row = [
            Paragraph(str(idx), cell_text_style),
            Paragraph(r['date'], cell_text_style),
            Paragraph(r['rec_no'], cell_text_style),
            Paragraph(r['reg_no'], cell_text_style),
            Paragraph(r['name'], cell_bold_style),
            Paragraph(r['head'], cell_text_style),
            Paragraph(r['code'], cell_text_style),
            Paragraph(r['details'], cell_text_style),
            Paragraph(r['mode'], cell_text_style),
            Paragraph("{:,.2f}".format(r['amount']), cell_bold_style)
        ]
        table_data.append(row)

    # Add Total Row at bottom
    total_row = [
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("<b>GRAND TOTAL</b>", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("<b>₹ {:,.2f}</b>".format(total_overall), cell_head_style)
    ]
    table_data.append(total_row)

    # Col widths total = 770 pt (A4 Landscape usable width)
    col_widths = [25, 55, 45, 45, 150, 150, 60, 130, 40, 70]

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 4),
        # Total row background
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
    ]

    # Alternating row colors
    for i in range(1, len(table_data) - 1):
        bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else colors.white
        t_style.append(('BACKGROUND', (0, i), (-1, i), bg))

    t.setStyle(TableStyle(t_style))
    elements.append(t)

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {pdf_filename}")


def generate_member_ledgers_pdf():
    cb_entries, ind_rows = parse_church_data()
    
    # Header column keys
    header_row = ind_rows[3] if len(ind_rows) > 3 else {}
    
    # List of member rows
    members_list = []
    grand_totals = {k: 0 for k in header_row.keys() if k not in ['A', 'B', 'C', 'D']}
    
    for r in ind_rows[4:]:
        sl = str(r.get('A', '') or '').strip()
        reg = str(r.get('B', '') or '').strip()
        name = str(r.get('C', '') or '').strip()
        sub_upto = str(r.get('D', '') or '').strip()
        
        if not reg and not name: continue
        if reg == 'GRAND TOTAL' or name == 'GRAND TOTAL': continue
        
        # Calculate dynamic member contributions from Cashbook
        m_total = 0
        m_row = {'sl': sl, 'reg': reg, 'name': name, 'sub_upto': sub_upto, 'cols': {}}
        
        # Read from individual row
        for k in header_row.keys():
            if k in ['A', 'B', 'C', 'D']: continue
            val_str = str(r.get(k, '') or '').replace(',', '').strip()
            try: val = float(val_str)
            except: val = 0
            m_row['cols'][k] = val
            m_total += val
            grand_totals[k] = grand_totals.get(k, 0) + val
            
        m_row['total'] = m_total
        members_list.append(m_row)

    pdf_filename = "c:\\CASHBOOK_APP\\St_Gregorios_Church_Individual_Members_Contribution_List.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(A4),
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        alignment=1
    )
    cell_head_style = ParagraphStyle(
        'CellHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white,
        alignment=1
    )
    cell_text_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#2D3748")
    )
    cell_bold_style = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#1A365D")
    )

    elements = []
    
    # Title Header
    elements.append(Paragraph("ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE", title_style))
    elements.append(Paragraph("Government House Road, Nazarbad, Mysuru, Karnataka — 570010", subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>INDIVIDUAL MEMBER ACCOUNTS & CONTRIBUTIONS SUMMARY STATEMENT</b>", ParagraphStyle('SubHeader', parent=subtitle_style, fontSize=12, leading=15, textColor=colors.HexColor("#2B6CB0"))))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

    # Pick top major columns to fit nicely across landscape A4:
    # Sl, Reg No, Name, Sub Upto, Subscription, Catholicate, Metropolitan, Mission Sun, Seminary, Priest Welfare, Birthday, St Mary Feast, Building Fund, Total Contribution
    headers = [
        Paragraph("Sl", cell_head_style),
        Paragraph("Reg No", cell_head_style),
        Paragraph("Name of Member / HoF", cell_head_style),
        Paragraph("Sub Upto", cell_head_style),
        Paragraph("Subscription (₹)", cell_head_style),
        Paragraph("Catholicate (₹)", cell_head_style),
        Paragraph("Metropolitan (₹)", cell_head_style),
        Paragraph("Mission Sun (₹)", cell_head_style),
        Paragraph("Seminary (₹)", cell_head_style),
        Paragraph("Priest Wfr (₹)", cell_head_style),
        Paragraph("Birthday (₹)", cell_head_style),
        Paragraph("St. Mary (₹)", cell_head_style),
        Paragraph("Building (₹)", cell_head_style),
        Paragraph("Total (₹)", cell_head_style)
    ]
    
    table_data = [headers]
    overall_total = 0

    for idx, m in enumerate(members_list, 1):
        cols = m['cols']
        # Map specific keys from data.js: E=Sub, G=Catholicate, H=Metropolitan, I=Mission, J=Seminary, K=Priest, N=Birthday, Y=St Mary, Z=Building
        tot = m['total']
        overall_total += tot
        
        row = [
            Paragraph(str(idx), cell_text_style),
            Paragraph(m['reg'], cell_text_style),
            Paragraph(m['name'], cell_bold_style),
            Paragraph(m['sub_upto'] or '-', cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('E', 0)) if cols.get('E', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('G', 0)) if cols.get('G', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('H', 0)) if cols.get('H', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('I', 0)) if cols.get('I', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('J', 0)) if cols.get('J', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('K', 0)) if cols.get('K', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('N', 0)) if cols.get('N', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('Y', 0)) if cols.get('Y', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.0f}".format(cols.get('Z', 0)) if cols.get('Z', 0)>0 else "-", cell_text_style),
            Paragraph("{:,.2f}".format(tot), cell_bold_style)
        ]
        table_data.append(row)

    # Grand Total Row
    total_row = [
        Paragraph("", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("<b>GRAND TOTAL</b>", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('E', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('G', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('H', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('I', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('J', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('K', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('N', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('Y', 0)), cell_head_style),
        Paragraph("{:,.0f}".format(grand_totals.get('Z', 0)), cell_head_style),
        Paragraph("<b>₹ {:,.2f}</b>".format(overall_total), cell_head_style)
    ]
    table_data.append(total_row)

    col_widths = [25, 45, 160, 50, 50, 45, 45, 45, 45, 45, 45, 45, 45, 80]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 3),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
    ]

    for i in range(1, len(table_data) - 1):
        bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else colors.white
        t_style.append(('BACKGROUND', (0, i), (-1, i), bg))

    t.setStyle(TableStyle(t_style))
    elements.append(t)

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {pdf_filename}")


if __name__ == '__main__':
    generate_external_nm_pdf()
    generate_member_ledgers_pdf()
