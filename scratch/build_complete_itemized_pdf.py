import re
import json
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
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
        
        # Header on page 2+
        if self._pageNumber > 1:
            self.drawString(36, 810, "St. Gregorios Orthodox Syrian Church, Mysuru — All Registered Members Contribution Statement")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(36, 804, 559, 804)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 25, page_text)
        self.drawString(36, 25, "St. Gregorios Orthodox Syrian Church & Pilgrim Centre — Official Audit Copy")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(36, 35, 559, 35)
        self.restoreState()


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


def build_complete_pdf():
    ind_rows, header_row = parse_church_data()

    # Build member list with ALL contribution heads
    member_map = {}
    head_totals = {}

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
                head_totals[h_name] = head_totals.get(h_name, 0) + val

    for reg, m in member_map.items():
        m['total'] = sum(m['contributions'].values())

    # Sort members by Reg No integer if numeric, else string
    def reg_key(m):
        r = m['reg']
        try: return (0, int(r))
        except: return (1, r)

    sorted_members = sorted(member_map.values(), key=reg_key)

    total_parishioners = len(sorted_members)
    active_contributors = len([m for m in sorted_members if m['total'] > 0])
    grand_total_amount = sum(m['total'] for m in sorted_members)

    pdf_filename = "c:\\CASHBOOK_APP\\St_Gregorios_Church_Complete_Individual_Member_Contributions.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=portrait(A4),
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=colors.HexColor("#1A365D"), alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#4A5568"), alignment=1
    )
    cell_head_style = ParagraphStyle(
        'CellHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=1
    )
    cell_text_style = ParagraphStyle(
        'CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#2D3748")
    )
    cell_bold_style = ParagraphStyle(
        'CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#1A365D")
    )

    elements = []
    
    # Header Title
    elements.append(Paragraph("ST. GREGORIOS ORTHODOX SYRIAN CHURCH & PILGRIM CENTRE", title_style))
    elements.append(Paragraph("Government House Road, Nazarbad, Mysuru, Karnataka — 570010", subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>COMPLETE REGISTERED MEMBERS INDIVIDUAL CONTRIBUTIONS STATEMENT</b>", ParagraphStyle('SubHeader', parent=subtitle_style, fontSize=11, leading=14, textColor=colors.HexColor("#2B6CB0"))))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2B6CB0"), spaceAfter=8))

    # Summary Statistics Box
    summary_data = [
        [
            Paragraph("<b>Total Registered Members:</b> " + str(total_parishioners), cell_text_style),
            Paragraph("<b>Members with Active Contributions:</b> " + str(active_contributors), cell_text_style),
            Paragraph("<b>GRAND TOTAL CONTRIBUTIONS:</b> ₹ {:,.2f}".format(grand_total_amount), cell_bold_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[170, 180, 210])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3182CE")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BEE3F8")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # Section 1: Itemized Member Contributions Table
    table_headers = [
        Paragraph("Reg No", cell_head_style),
        Paragraph("Name of Member / Head of Family", cell_head_style),
        Paragraph("Sub Upto", cell_head_style),
        Paragraph("All Itemized Account Head Contributions", cell_head_style),
        Paragraph("Total Contribution (₹)", cell_head_style)
    ]
    table_data = [table_headers]

    for m in sorted_members:
        # Build clean html text for itemized contributions
        contrib_items = m['contributions']
        if not contrib_items:
            details_str = "<font color='#A0AEC0'><i>No active contributions recorded</i></font>"
        else:
            items_list = []
            for h_name, amt in sorted(contrib_items.items(), key=lambda x: x[0]):
                items_list.append(f"<b>{h_name}:</b> ₹ {amt:,.0f}")
            details_str = " &nbsp;|&nbsp; ".join(items_list)

        row = [
            Paragraph(f"<b>#{m['reg']}</b>", cell_bold_style),
            Paragraph(m['name'], cell_bold_style),
            Paragraph(m['sub_upto'] or '-', cell_text_style),
            Paragraph(details_str, cell_text_style),
            Paragraph(f"<b>₹ {m['total']:,.2f}</b>" if m['total'] > 0 else "-", cell_bold_style)
        ]
        table_data.append(row)

    # Grand Total Row
    total_row = [
        Paragraph("", cell_head_style),
        Paragraph("<b>GRAND TOTAL (ALL MEMBERS)</b>", cell_head_style),
        Paragraph("", cell_head_style),
        Paragraph(f"<b>Total Contributors: {active_contributors} members</b>", cell_head_style),
        Paragraph(f"<b>₹ {grand_total_amount:,.2f}</b>", cell_head_style)
    ]
    table_data.append(total_row)

    col_widths = [45, 140, 50, 240, 85] # Total = 520 pt (A4 Portrait width usable = 523 pt)
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
    ]

    for i in range(1, len(table_data) - 1):
        bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else colors.white
        t_style.append(('BACKGROUND', (0, i), (-1, i), bg))

    t.setStyle(TableStyle(t_style))
    elements.append(t)
    
    elements.append(Spacer(1, 15))

    # Section 2: Account Head Master Summary Breakdown Table
    elements.append(Paragraph("<b>ACCOUNT HEAD MASTER SUMMARY BREAKDOWN</b>", ParagraphStyle('SectionHeader', parent=subtitle_style, fontSize=11, leading=14, textColor=colors.HexColor("#1A365D"), alignment=0)))
    elements.append(Spacer(1, 4))

    head_headers = [
        Paragraph("Sl", cell_head_style),
        Paragraph("Account Head / Collection Category", cell_head_style),
        Paragraph("Total Collected Amount (₹)", cell_head_style)
    ]
    head_table_data = [head_headers]

    for idx, (h_name, h_tot) in enumerate(sorted(head_totals.items(), key=lambda x: x[0]), 1):
        h_row = [
            Paragraph(str(idx), cell_text_style),
            Paragraph(h_name, cell_bold_style),
            Paragraph(f"<b>₹ {h_tot:,.2f}</b>", cell_bold_style)
        ]
        head_table_data.append(h_row)

    head_total_row = [
        Paragraph("", cell_head_style),
        Paragraph("<b>GRAND TOTAL ACROSS ALL ACCOUNT HEADS</b>", cell_head_style),
        Paragraph(f"<b>₹ {grand_total_amount:,.2f}</b>", cell_head_style)
    ]
    head_table_data.append(head_total_row)

    ht = Table(head_table_data, colWidths=[35, 345, 140])
    ht_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2D3748")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
    ]
    for i in range(1, len(head_table_data) - 1):
        bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else colors.white
        ht_style.append(('BACKGROUND', (0, i), (-1, i), bg))

    ht.setStyle(TableStyle(ht_style))
    elements.append(ht)

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {pdf_filename}")


if __name__ == '__main__':
    build_complete_pdf()
