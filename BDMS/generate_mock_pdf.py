import os
import sys

# Ensure reportlab is installed
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except ImportError:
    print("ReportLab not found. Auto-installing dependencies via pip...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

# Output file path
pdf_path = os.path.join(os.path.dirname(__file__), "mock_receipt.pdf")

doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
story = []
styles = getSampleStyleSheet()

# Title Style
title_style = ParagraphStyle(
    'InvoiceTitle',
    parent=styles['Heading1'],
    fontSize=22,
    textColor=colors.HexColor('#0b2240'),
    spaceAfter=15,
)

# Text Style
normal_style = ParagraphStyle(
    'InvoiceText',
    parent=styles['Normal'],
    fontSize=10.5,
    leading=14,
    textColor=colors.HexColor('#333333'),
)

# Draw Title
story.append(Paragraph("<b>TAX INVOICE / RECEIPT</b>", title_style))
story.append(Spacer(1, 10))

# Invoice details table
meta_data = [
    [
        Paragraph("<b>Supplier:</b> Railway Steel Components Ltd", normal_style),
        Paragraph("<b>Invoice No:</b> INV-2026-9875", normal_style)
    ],
    [
        Paragraph("<b>Address:</b> Industrial Area, Sector 4, Steel City", normal_style),
        Paragraph("<b>Bill Date:</b> 02/06/2026", normal_style)
    ],
    [
        Paragraph("<b>GSTIN:</b> 09AAACR1234F1Z0", normal_style),
        Paragraph("<b>PO Number:</b> PO-RDSO-87612", normal_style)
    ]
]
t_meta = Table(meta_data, colWidths=[270, 250])
t_meta.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
]))
story.append(t_meta)
story.append(Spacer(1, 20))

# Divider Line
story.append(Table([[""]], colWidths=[520], rowHeights=[1], style=TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e0e4ec'))])))
story.append(Spacer(1, 15))

# Item descriptions (Intelligent extraction variables)
desc_para = Paragraph(
    "<b>Material Name:</b> Heavy Duty Steel Rail Joint Clamp<br/>"
    "High tensile strength carbon steel joints for railway track reinforcements. Certified to RDSO specifications.",
    normal_style
)

items_data = [
    [Paragraph("<b>Item Details</b>", normal_style), Paragraph("<b>Specifications</b>", normal_style)],
    [desc_para, Paragraph(
        "<b>Batch No:</b> BATCH-SL-87A<br/>"
        "<b>HSN Code:</b> 73021010<br/>"
        "<b>Quantity:</b> 120.00 units",
        normal_style
    )],
    [
        Paragraph("<b>Pricing Rates</b>", normal_style), 
        Paragraph(
            "<b>Unit Price:</b> Rs. 450.00<br/>"
            "<b>GST Tax:</b> Rs. 9720.00 (18% SGST/CGST)<br/>"
            "<b>Total Cost:</b> Rs. 54000.00",
            normal_style
        )
    ]
]

t_items = Table(items_data, colWidths=[260, 260])
t_items.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f4f6f9')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e4ec')),
    ('PADDING', (0,0), (-1,-1), 10),
]))
story.append(t_items)
story.append(Spacer(1, 30))

# Signatures
sig_data = [
    [Paragraph("Prepared By: Accounts Section", normal_style), Paragraph("Authorized Signatory: Railway Steel Components", normal_style)]
]
t_sig = Table(sig_data, colWidths=[260, 260])
t_sig.setStyle(TableStyle([
    ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ('TOPPADDING', (0,0), (-1,-1), 30),
]))
story.append(t_sig)

doc.build(story)
print(f"[SUCCESS] Mock invoice PDF successfully created at: {pdf_path}")
