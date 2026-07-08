import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

def P(text, is_bold=False, align='left', size=7.5, leading=9):
    align_val = 0
    if align == 'center':
        align_val = 1
    elif align == 'right':
        align_val = 2
    
    font = 'Helvetica-Bold' if is_bold else 'Helvetica'
    p_style = ParagraphStyle(
        'cell_style',
        fontName=font,
        fontSize=size,
        leading=leading,
        alignment=align_val
    )
    html_text = text.replace('\n', '<br/>')
    return Paragraph(html_text, p_style)

def generate_pdf(filename):
    # 0.5-inch margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    story = []
    
    # Define widths for a 6-column grid spanning 7.5 inches (540 points)
    col_widths = [90, 90, 100, 90, 80, 90]
    
    # 1. Main Structured Receipt Note Grid
    table_data = [
        # Row 0
        [P("RDSO", True, 'center', 9, 11), "", P("RECEIPT NOTE", True, 'center', 10, 12), "", "", P("[STOCK] [S719]", True, 'center', 8, 10)],
        # Row 1
        [P("E-79", True, 'center', 8, 10), "", P("Inspecting Depot: Central Stores Depot, RDSO", True, 'center', 8, 10), "", "", P("CC: 44", True, 'center', 8, 10)],
        # Row 2
        [P("R/Note-No.\n0126200155", True), P("Date\n10/06/26", True), P("PO/AT No.\nPO-RDSO-10892", True), P("P.O.Date\n22/05/26", True), P("P.O.Sr.No.\n001", True), P("Allocation\n03025199", True)],
        # Row 3
        [P("Name & Address of Supplier", True), "", P("Vendor Code", True), P("Depot: 01   Ward: 02", True), P("R.O.No.: 02044", True), P("R.O.Date: 10/06/26", True)],
        # Row 4
        [P("M/s RAIL FASTENERS INDIA PVT LTD\nPlot No. 12, Industrial Area, Sector 5, Noida-201301\n[Tel: 0120-2458921]   (V.Code: V-FAST-12)"), "", 
         P("RN Quantity: 500\n(Five Hundred Nos.)\n\nRO Quantity: 500"), "", 
         P("Unit: Nos.   Rate: 85.00\n(Rs. Eighty Five Only)\n\nRO Unit: Nos."), ""],
        # Row 5
        [P("Description & Drg./Spec.", True), P("PL No.: 73029010", True), P("Value: Rs. 42500.00", True), P("DRR-No.: R1260112", True), P("Date: 10/06/26", True), ""],
        # Row 6
        [P("Elastic Rail Clip (ERC) MK-V to RDSO Spec. No. T-3701\n(Detailed Description/Specification as per Product # 1 of GeM Contract No. GEMC-511687797220686 dt.22/05/2026)"), "", 
         P("Date of Acceptance\n10/06/26"), P("ISL-No.: R1260115"), P("Date: 10/06/26"), ""],
        # Row 6b
        [P("Terms of Delivery\nF.O.R. Noida"), "", P("Freight"), P("Wharfage/Demurrage"), P("Packing  /  Forwarding"), P("Excise Duty  /  GST\nGST")],
        # Row 7
        [P("Gate/Challan Registration No.\n1142955"), P("Dated\n10/06/26"), P("Consignee\n000100-Central Stores Depot, Depot, RDSO"), "", P("P.O.Qty\n500"), P("Bal.P.O.Qty\n0")],
        # Row 8
        [P("Inspection Details :\nInsp Agency : CONSG\nIC No.ADMM CSD dated 10/JUN/26"), "", 
         P("Warranty Upto/Expiry Date: 31-MAR-29\nPaying-Auth.: Director/Finance.\nPayment-Terms: As per GeM Contract terms and conditions.\nRemarks\n\nInspection Report :\n(1) Elastic Rail Clip MK-V.. type............. OK\n(2) Colour- black, ISI marked ......... OK\n(3) MANUFACTURING 2024/2025..................OK\n(4) Brand: RailFasteners.....................OK\n(5) One year warranty from the date of supply...................OK\nItem is as per PO.\n\nITEM IS ACCEPTED AS PER ABOVE REPORT GIVEN IN REMARKS COLUMN ."), "", "", ""],
        # Row 9
        [P("RR/MTR No.: By Hand"), "", P("Date:"), "", "", ""],
        # Row 10
        [P("Challan/Invoice No.: GEM-74927355"), "", P("Date: 28-MAY-26"), "", "", ""],
        # Row 11
        [P("Due Date of Delivery\n05/06/26"), "", P("Actual Date of Supply\n10/06/26"), "", "", ""],
        # Row 12
        [P("Qty.Invoiced\n500.000", True), P("Qty.Received\n500.000", True), P("Qty.Accepted\n500.000", True), P("Qty.Rejected\n0.000", True), P("Original PO details", True), ""],
        # Row 13
        [P("E-Dispatch Note No and date :"), "", "", "", "", ""]
    ]
    
    grid_style = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (2,0), (4,0)),
        ('SPAN', (0,1), (1,1)),
        ('SPAN', (2,1), (4,1)),
        ('SPAN', (0,3), (1,3)),
        ('SPAN', (0,4), (1,4)),
        ('SPAN', (2,4), (3,4)),
        ('SPAN', (4,4), (5,4)),
        ('SPAN', (4,5), (5,5)),
        ('SPAN', (0,6), (1,6)),
        ('SPAN', (4,6), (5,6)),
        ('SPAN', (0,7), (1,7)),
        ('SPAN', (2,8), (3,8)),
        ('SPAN', (0,9), (1,9)),
        ('SPAN', (2,9), (-1,9)),
        ('SPAN', (0,10), (1,10)),
        ('SPAN', (2,10), (3,10)),
        ('SPAN', (0,11), (1,11)),
        ('SPAN', (2,11), (3,11)),
        ('SPAN', (0,12), (1,12)),
        ('SPAN', (2,12), (3,12)),
        ('SPAN', (4,13), (5,13)),
        ('SPAN', (0,14), (-1,14)),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ])
    
    t = Table(table_data, colWidths=col_widths, style=grid_style)
    story.append(t)
    
    story.append(Spacer(1, 10))
    decl_style = ParagraphStyle(
        'decl',
        fontName='Helvetica',
        fontSize=7,
        leading=9
    )
    story.append(Paragraph("Depot Officer Has Exercised his powers to accept material after expiry of Delivery period.", decl_style))
    story.append(Paragraph("Received the Accepted Quantity Correctly and Rate Certified.", decl_style))
    story.append(Spacer(1, 10))
    
    sig_widths = [180, 180, 180]
    sig_headers = [
        [P("Despatching Official", True, 'center', 8, 10), P("Receiving official", True, 'center', 8, 10), P("Depot Officer", True, 'center', 8, 10)]
    ]
    
    sig_table = Table(sig_headers, colWidths=sig_widths, style=[
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ])
    story.append(sig_table)
    story.append(Spacer(1, 5))
    
    signed_data = [
        [
            P("<font color='red'><b>Signature Not Verified</b></font><br/>"
              "Digitally signed by AMIT SHARMA<br/>"
              "Date: 2026.06.10 15:10:22 IST<br/>"
              "Reason: WARD-R.O. 02044<br/>"
              "dt.10/06/26", False, 'left', 7.5, 9),
            "",
            P("<font color='red'><b>Signature Not Verified</b></font><br/>"
              "Digitally signed by SURESH SINGH<br/>"
              "Date: 2026.06.10 13:42:15 IST<br/>"
              "Reason: Signed RNote<br/>"
              "Location: IREPS-CRIS", False, 'left', 7.5, 9)
        ]
    ]
    
    signed_table = Table(signed_data, colWidths=[240, 60, 240], style=[
        ('BOX', (0,0), (0,0), 1, colors.Color(0.9, 0.6, 0.1)),
        ('BOX', (2,0), (2,0), 1, colors.Color(0.9, 0.6, 0.1)),
        ('BACKGROUND', (0,0), (0,0), colors.Color(0.98, 0.98, 0.95)),
        ('BACKGROUND', (2,0), (2,0), colors.Color(0.98, 0.98, 0.95)),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ])
    story.append(signed_table)
    
    doc.build(story)
    print(f"Successfully generated PDF: {filename}")

if __name__ == '__main__':
    # Save directly in the artifacts directory
    output_path = r"C:\Users\Arnav Saini\.gemini\antigravity-ide\brain\e9af2602-7b15-4f9b-bbe8-11ce6b656bc8\test_receipt_new_item.pdf"
    generate_pdf(output_path)
