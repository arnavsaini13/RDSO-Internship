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

def generate_pdf(filename, supplier, invoice_no, address, date, gstin, po_no, material_name, material_desc, batch_no, hsn, qty, price, tax, total):
    pdf_path = os.path.join(os.path.dirname(__file__), filename)
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
            Paragraph(f"<b>Supplier:</b> {supplier}", normal_style),
            Paragraph(f"<b>Invoice No:</b> {invoice_no}", normal_style)
        ],
        [
            Paragraph(f"<b>Address:</b> {address}", normal_style),
            Paragraph(f"<b>Bill Date:</b> {date}", normal_style)
        ],
        [
            Paragraph(f"<b>GSTIN:</b> {gstin}", normal_style),
            Paragraph(f"<b>PO Number:</b> {po_no}", normal_style)
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

    # Item descriptions
    desc_para = Paragraph(
        f"<b>Material Name:</b> {material_name}<br/>"
        f"{material_desc}",
        normal_style
    )

    items_data = [
        [Paragraph("<b>Item Details</b>", normal_style), Paragraph("<b>Specifications</b>", normal_style)],
        [desc_para, Paragraph(
            f"<b>Batch No:</b> {batch_no}<br/>"
            f"<b>HSN Code:</b> {hsn}<br/>"
            f"<b>Quantity:</b> {qty} units",
            normal_style
        )],
        [
            Paragraph("<b>Pricing Rates</b>", normal_style), 
            Paragraph(
                f"<b>Unit Price:</b> Rs. {price}<br/>"
                f"<b>GST Tax:</b> Rs. {tax}<br/>"
                f"<b>Total Cost:</b> Rs. {total}",
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
        [Paragraph("Prepared By: Accounts Section", normal_style), Paragraph(f"Authorized Signatory: {supplier}", normal_style)]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 30),
    ]))
    story.append(t_sig)

    doc.build(story)
    print(f"[SUCCESS] Mock invoice PDF successfully created at: {pdf_path}")

# Generate PDF 3
generate_pdf(
    filename="mock_receipt_3.pdf",
    supplier="Tata Steel Long Products Ltd",
    invoice_no="INV-2026-1035",
    address="Tata Steel Complex, Jamshedpur, Jharkhand",
    date="05/06/2026",
    gstin="20AAACT1035J1Z5",
    po_no="PO-RDSO-10350",
    material_name="Heavy Duty Steel Sleepers",
    material_desc="High durable structural steel sleepers designed for railway track alignment stability. RDSO Certified.",
    batch_no="BATCH-TATA-33B",
    hsn="73029000",
    qty="200.00",
    price="850.00",
    tax="30600.00 (18% GST)",
    total="170000.00"
)

# Generate PDF 4
generate_pdf(
    filename="mock_receipt_4.pdf",
    supplier="Jindal Steel & Power Ltd",
    invoice_no="INV-2026-6712",
    address="Jindal Industrial Park, Raigarh, Chhattisgarh",
    date="12/06/2026",
    gstin="22AAACJ6712D1Z8",
    po_no="PO-RDSO-67120",
    material_name="Pre-stressed Concrete Wire",
    material_desc="High tensile steel wires specifically engineered for pre-stressed concrete railway sleepers. Spec RDSO/M&C/112.",
    batch_no="BATCH-JINDAL-99F",
    hsn="72171010",
    qty="350.00",
    price="320.00",
    tax="20160.00 (18% GST)",
    total="112000.00"
)
