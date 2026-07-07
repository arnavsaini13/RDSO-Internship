import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.contrib.auth.models import User
from documents.models import Material, InventoryBalance
from documents.barcode_utils import generate_material_barcode

def populate_mock():
    print("Populating database with 3 standard mock material records...")

    # Ensure we have an admin user to assign as uploader
    admin_email = 'admin@rdso.railnet.gov.in'
    admin_user = User.objects.filter(email__iexact=admin_email).first()
    if not admin_user:
        admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username=admin_email,
            email=admin_email,
            password='Admin@123456',
            first_name='Super',
            last_name='Admin'
        )
        print(f"Created superuser {admin_email} for uploading.")

    # Clean existing data to start fresh (sequential serial numbers 1, 2, 3)
    Material.objects.all().delete()
    InventoryBalance.objects.all().delete()
    print("Cleared existing materials and balances.")

    mock_materials = [
        {
            'serial_number': 1,
            'material_name': 'Heavy Duty Steel Rail Joint Clamp',
            'quantity': Decimal('120.00'),
            'vendor_name': 'Railway Steel Components Ltd',
            'date_received': '2026-06-02',
            'unit_price': Decimal('450.00'),
            'total_cost': Decimal('54000.00'),
            'hsn_code': '73021010',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-87612',
            'ro_number': 'RO-87612',
            'vendor_code': 'V-STEEL-98',
            'r_note_no': 'RNOTE-11001',
            'pl_no': 'PL-7302-01',
            'receipt_pdf': 'receipts/mock_receipt.pdf',
            'barcode_data': 'SR-00000001'
        },
        {
            'serial_number': 2,
            'material_name': 'High Strength Track Switches and Crossings',
            'quantity': Decimal('45.00'),
            'vendor_name': 'Bharat Heavy Electricals Ltd',
            'date_received': '2026-06-03',
            'unit_price': Decimal('1250.00'),
            'total_cost': Decimal('56250.00'),
            'hsn_code': '73023000',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-44512',
            'ro_number': 'RO-44512',
            'vendor_code': 'V-BHEL-02',
            'r_note_no': 'RNOTE-11002',
            'pl_no': 'PL-7302-02',
            'receipt_pdf': 'receipts/mock_receipt_2.pdf',
            'barcode_data': 'SR-00000002'
        },
        {
            'serial_number': 3,
            'material_name': 'Heavy Duty Steel Sleepers',
            'quantity': Decimal('200.00'),
            'vendor_name': 'Tata Steel Long Products Ltd',
            'date_received': '2026-06-05',
            'unit_price': Decimal('850.00'),
            'total_cost': Decimal('170000.00'),
            'hsn_code': '73029000',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-10350',
            'ro_number': 'RO-10350',
            'vendor_code': 'V-TATA-33',
            'r_note_no': 'RNOTE-11003',
            'pl_no': 'PL-7302-03',
            'receipt_pdf': 'receipts/mock_receipt_3.pdf',
            'barcode_data': 'SR-00000003'
        },
        {
            'serial_number': 4,
            'material_name': 'Elastic Rail Clip (ERC) MK-V',
            'quantity': Decimal('500.00'),
            'vendor_name': 'Rail Fasteners India Pvt Ltd',
            'date_received': '2026-06-08',
            'unit_price': Decimal('85.00'),
            'total_cost': Decimal('42500.00'),
            'hsn_code': '73029010',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-10892',
            'ro_number': 'RO-10892',
            'vendor_code': 'V-FAST-12',
            'r_note_no': 'RNOTE-11004',
            'pl_no': 'PL-7302-04',
            'receipt_pdf': 'receipts/mock_receipt_4.pdf',
            'barcode_data': 'SR-00000004'
        },
        {
            'serial_number': 5,
            'material_name': 'LED Main Signal Lighting Unit',
            'quantity': Decimal('80.00'),
            'vendor_name': 'Siemens Mobility Solutions',
            'date_received': '2026-06-10',
            'unit_price': Decimal('1800.00'),
            'total_cost': Decimal('144000.00'),
            'hsn_code': '85301010',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-21940',
            'ro_number': 'RO-21940',
            'vendor_code': 'V-SIEM-99',
            'r_note_no': 'RNOTE-11005',
            'pl_no': 'PL-8530-01',
            'receipt_pdf': 'receipts/mock_receipt.pdf',
            'barcode_data': 'SR-00000005'
        },
        {
            'serial_number': 6,
            'material_name': 'Electronic Interlocking Module',
            'quantity': Decimal('15.00'),
            'vendor_name': 'Alstom Transport India',
            'date_received': '2026-06-12',
            'unit_price': Decimal('12500.00'),
            'total_cost': Decimal('187500.00'),
            'hsn_code': '85308000',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-33412',
            'ro_number': 'RO-33412',
            'vendor_code': 'V-ALST-04',
            'r_note_no': 'RNOTE-11006',
            'pl_no': 'PL-8530-02',
            'receipt_pdf': 'receipts/mock_receipt_2.pdf',
            'barcode_data': 'SR-00000006'
        },
        {
            'serial_number': 7,
            'material_name': 'Prestressed Concrete Sleepers (S-Type)',
            'quantity': Decimal('350.00'),
            'vendor_name': 'Deccan Concrete Products Ltd',
            'date_received': '2026-06-15',
            'unit_price': Decimal('620.00'),
            'total_cost': Decimal('217000.00'),
            'hsn_code': '68109100',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-40129',
            'ro_number': 'RO-40129',
            'vendor_code': 'V-DECC-08',
            'r_note_no': 'RNOTE-11007',
            'pl_no': 'PL-6810-01',
            'receipt_pdf': 'receipts/mock_receipt_3.pdf',
            'barcode_data': 'SR-00000007'
        },
        {
            'serial_number': 8,
            'material_name': 'Standard Steel Fish Plates (60kg Rail)',
            'quantity': Decimal('240.00'),
            'vendor_name': 'Jindal Steel & Power Ltd',
            'date_received': '2026-06-18',
            'unit_price': Decimal('290.00'),
            'total_cost': Decimal('69600.00'),
            'hsn_code': '73024000',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-51289',
            'ro_number': 'RO-51289',
            'vendor_code': 'V-JIND-77',
            'r_note_no': 'RNOTE-11008',
            'pl_no': 'PL-7302-05',
            'receipt_pdf': 'receipts/mock_receipt_4.pdf',
            'barcode_data': 'SR-00000008'
        },
        {
            'serial_number': 9,
            'material_name': 'Copper Contact Wire (107 sq mm)',
            'quantity': Decimal('12.00'),
            'vendor_name': 'Hindalco Industries Ltd',
            'date_received': '2026-06-20',
            'unit_price': Decimal('42000.00'),
            'total_cost': Decimal('504000.00'),
            'hsn_code': '74081190',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-60312',
            'ro_number': 'RO-60312',
            'vendor_code': 'V-HIND-01',
            'r_note_no': 'RNOTE-11009',
            'pl_no': 'PL-7408-01',
            'receipt_pdf': 'receipts/mock_receipt.pdf',
            'barcode_data': 'SR-00000009'
        },
        {
            'serial_number': 10,
            'material_name': 'Solid Locomotive Coached Wheels',
            'quantity': Decimal('25.00'),
            'vendor_name': 'Steel Authority of India Ltd (SAIL)',
            'date_received': '2026-06-22',
            'unit_price': Decimal('18500.00'),
            'total_cost': Decimal('462500.00'),
            'hsn_code': '86071910',
            'consignee': 'Central Stores Depot, RDSO',
            'po_at_no': 'PO-RDSO-70198',
            'ro_number': 'RO-70198',
            'vendor_code': 'V-SAIL-50',
            'r_note_no': 'RNOTE-11010',
            'pl_no': 'PL-8607-01',
            'receipt_pdf': 'receipts/mock_receipt_2.pdf',
            'barcode_data': 'SR-00000010'
        }
    ]

    for mdata in mock_materials:
        # Create Material
        material = Material.objects.create(
            serial_number=mdata['serial_number'],
            material_name=mdata['material_name'],
            quantity=mdata['quantity'],
            vendor_name=mdata['vendor_name'],
            date_received=mdata['date_received'],
            unit_price=mdata['unit_price'],
            total_cost=mdata['total_cost'],
            hsn_code=mdata['hsn_code'],
            consignee=mdata['consignee'],
            po_at_no=mdata['po_at_no'],
            ro_number=mdata['ro_number'],
            vendor_code=mdata['vendor_code'],
            r_note_no=mdata['r_note_no'],
            pl_no=mdata['pl_no'],
            receipt_pdf=mdata['receipt_pdf'],
            barcode_data=mdata['barcode_data'],
            uploaded_by=admin_user
        )

        # Create Balance
        InventoryBalance.objects.create(
            material=material,
            available_quantity=mdata['quantity']
        )

        # Generate Barcode
        generate_material_barcode(material)
        material.save()

        print(f"[SUCCESS] Created Serial No: {material.serial_number} | {material.material_name}")

    print("\nMock data population complete. 3 items are now active in the system database.")

if __name__ == '__main__':
    populate_mock()
