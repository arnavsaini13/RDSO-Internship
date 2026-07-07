"""
Inventory Management Utilities
"""

import logging
from decimal import Decimal
from typing import Dict, Any
from .models import Material, InventoryBalance, InventoryTransaction
from .barcode_utils import generate_material_barcode

logger = logging.getLogger(__name__)


def generate_unique_serial_number() -> int:
    """Generate unique sequential serial number"""
    try:
        last_material = Material.objects.all().order_by('-serial_number').first()
        if last_material and last_material.serial_number:
            return last_material.serial_number + 1
        return 1
    except Exception as e:
        logger.error(f"Error generating serial number: {e}")
        return Material.objects.count() + 1


def create_material_from_pdf_data(pdf_data: Dict[str, Any], receipt_pdf, uploaded_by) -> Material:
    """Create Material record from extracted PDF data"""
    
    serial_number = generate_unique_serial_number()
    
    # Extract core fields
    material_name = pdf_data.get('material_name', 'Unknown Material')
    quantity = Decimal(str(pdf_data.get('quantity', 0)))
    vendor_name = pdf_data.get('vendor_name', 'Unknown Vendor')
    date_received = pdf_data.get('date_received')
    
    # Exclude description from dataset/JSON and database field
    pdf_data_copy = pdf_data.copy()
    pdf_data_copy.pop('description', None)
    
    # Create material
    material = Material.objects.create(
        serial_number=serial_number,
        material_name=material_name,
        quantity=quantity,
        receipt_pdf=receipt_pdf,
        vendor_name=vendor_name,
        date_received=date_received,
        unit_price=Decimal(str(pdf_data.get('unit_price', 0))) if pdf_data.get('unit_price') else None,
        total_cost=Decimal(str(pdf_data.get('total_cost', 0))) if pdf_data.get('total_cost') else None,
        description=None,  # Do not store description in database
        category=pdf_data.get('category'),
        ro_number=pdf_data.get('ro_number'),
        vendor_code=pdf_data.get('vendor_code'),
        hsn_code=pdf_data.get('hsn_code'),
        consignee=pdf_data.get('consignee'),
        r_note_no=pdf_data.get('r_note_no'),
        po_at_no=pdf_data.get('po_at_no'),
        pl_no=pdf_data.get('pl_no'),
        uploaded_by=uploaded_by,
        extracted_data=pdf_data_copy,  # Store extracted data without description
    )
    
    # Generate barcode for the material
    try:
        generate_material_barcode(material)
        material.save()
        logger.info(f"Barcode generated for material: SR-{serial_number}")
    except Exception as e:
        logger.warning(f"Failed to generate barcode for SR-{serial_number}: {e}")
    
    logger.info(f"Material created: SR-{serial_number} - {material_name}")
    
    return material


def create_initial_inventory_balance(material: Material, quantity: Decimal = None):
    """Create initial inventory balance when material is added"""
    
    if quantity is None:
        quantity = material.quantity
    
    balance, created = InventoryBalance.objects.get_or_create(
        material=material,
        defaults={'available_quantity': quantity}
    )
    
    if created:
        logger.info(f"Inventory balance created for SR-{material.serial_number}: {quantity} units")
    
    return balance


def log_inventory_transaction(
    material: Material,
    action: str,
    quantity: Decimal,
    directorate: str,
    transaction_by,
    return_reason: str = None,
    remarks: str = None,
    ip_address: str = None
) -> InventoryTransaction:
    """Log inventory transaction"""
    
    transaction = InventoryTransaction.objects.create(
        material=material,
        action=action,
        quantity=quantity,
        directorate=directorate,
        transaction_by=transaction_by,
        return_reason=return_reason,
        remarks=remarks,
        ip_address=ip_address,
    )
    
    logger.info(f"Transaction logged: {action} - SR-{material.serial_number} - {quantity} units by {directorate}")
    
    return transaction


def update_inventory_balance(
    material: Material,
    action: str,
    quantity: Decimal,
    directorate: str,
    transaction_by,
    return_reason: str = None,
    remarks: str = None,
    ip_address: str = None
) -> bool:
    """Update inventory balance and log transaction"""
    
    try:
        balance = material.balance
        
        if action == 'TAKE':
            # Decrease available quantity
            if balance.available_quantity >= quantity:
                balance.available_quantity -= quantity
                balance.save()
            else:
                logger.error(f"Insufficient inventory: SR-{material.serial_number}")
                return False
        
        elif action == 'RETURN':
            # Increase available quantity
            balance.available_quantity += quantity
            balance.save()
        
        elif action == 'ADJUSTMENT':
            # Set to specific quantity
            balance.available_quantity = quantity
            balance.save()
        
        # Log the transaction
        log_inventory_transaction(
            material=material,
            action=action,
            quantity=quantity,
            directorate=directorate,
            transaction_by=transaction_by,
            return_reason=return_reason,
            remarks=remarks,
            ip_address=ip_address,
        )
        
        logger.info(f"Inventory updated: SR-{material.serial_number} - New balance: {balance.available_quantity}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        return False


def get_inventory_status() -> Dict[str, Any]:
    """Get overall inventory status"""
    
    materials = Material.objects.all()
    total_materials = materials.count()
    total_value = Decimal(0)
    
    low_stock = []
    
    for material in materials:
        if material.total_cost:
            total_value += material.total_cost
        
        balance = material.balance
        if balance and balance.available_quantity <= 10:
            low_stock.append({
                'serial_number': material.serial_number,
                'material_name': material.material_name,
                'available': str(balance.available_quantity),
            })
    
    return {
        'total_materials': total_materials,
        'total_inventory_value': str(total_value),
        'low_stock_items': low_stock,
        'low_stock_count': len(low_stock),
    }


def get_material_transaction_history(serial_number: int) -> list:
    """Get all transactions for a specific material"""
    
    try:
        material = Material.objects.get(serial_number=serial_number)
        transactions = material.transactions.all()
        
        history = []
        for txn in transactions:
            history.append({
                'action': txn.get_action_display(),
                'quantity': str(txn.quantity),
                'directorate': txn.directorate,
                'date': txn.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                'by': txn.transaction_by.username if txn.transaction_by else 'System',
                'remarks': txn.remarks,
                'return_reason': txn.return_reason,
            })
        
        return history
    
    except Material.DoesNotExist:
        logger.error(f"Material not found: SR-{serial_number}")
        return []


def get_directorate_inventory(directorate: str) -> Dict[str, Any]:
    """Get what a specific directorate has taken"""
    
    transactions = InventoryTransaction.objects.filter(
        directorate=directorate,
        action='TAKE'
    ).select_related('material')
    
    total_items_taken = Decimal(0)
    items_detail = []
    
    for txn in transactions:
        total_items_taken += txn.quantity
        items_detail.append({
            'serial_number': txn.material.serial_number,
            'material_name': txn.material.material_name,
            'quantity_taken': str(txn.quantity),
            'date': txn.transaction_date.strftime('%Y-%m-%d'),
        })
    
    return {
        'directorate': directorate,
        'total_items_taken': str(total_items_taken),
        'items': items_detail,
    }

