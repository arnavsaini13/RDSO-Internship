"""
Inventory Management Utilities
"""

import logging
from decimal import Decimal
from typing import Dict, Any
from .models import Material, InventoryBalance, InventoryTransaction
from .barcode_utils import generate_material_barcode

logger = logging.getLogger(__name__)


def generate_unique_material_id() -> str:
    """Generate unique material ID: MAT-2026-XXXX"""
    try:
        last_material = Material.objects.all().order_by('-id').first()
        if last_material:
            # Extract number from last ID
            last_id_str = last_material.material_id.split('-')[-1]
            last_num = int(last_id_str)
            next_num = last_num + 1
        else:
            next_num = 1
        
        return f"MAT-2026-{str(next_num).zfill(4)}"
    except Exception as e:
        logger.error(f"Error generating material ID: {e}")
        return f"MAT-2026-{Material.objects.count() + 1}"


def create_material_from_pdf_data(pdf_data: Dict[str, Any], receipt_pdf, uploaded_by) -> Material:
    """Create Material record from extracted PDF data"""
    
    material_id = generate_unique_material_id()
    
    # Extract core fields
    material_name = pdf_data.get('material_name', 'Unknown Material')
    quantity = Decimal(str(pdf_data.get('quantity', 0)))
    vendor_name = pdf_data.get('vendor_name', 'Unknown Vendor')
    date_received = pdf_data.get('date_received')
    
    # Create material
    material = Material.objects.create(
        material_id=material_id,
        material_name=material_name,
        quantity=quantity,
        receipt_pdf=receipt_pdf,
        vendor_name=vendor_name,
        date_received=date_received,
        unit_price=Decimal(str(pdf_data.get('unit_price', 0))) if pdf_data.get('unit_price') else None,
        total_cost=Decimal(str(pdf_data.get('total_cost', 0))) if pdf_data.get('total_cost') else None,
        description=pdf_data.get('description'),
        category=pdf_data.get('category'),
        batch_number=pdf_data.get('batch_number'),
        hsn_code=pdf_data.get('hsn_code'),
        uploaded_by=uploaded_by,
        extracted_data=pdf_data,  # Store all extracted data as JSON
    )
    
    # Generate barcode for the material
    try:
        generate_material_barcode(material)
        material.save()
        logger.info(f"Barcode generated for material: {material_id}")
    except Exception as e:
        logger.warning(f"Failed to generate barcode for {material_id}: {e}")
    
    logger.info(f"Material created: {material_id} - {material_name}")
    
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
        logger.info(f"Inventory balance created for {material.material_id}: {quantity} units")
    
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
    
    logger.info(f"Transaction logged: {action} - {material.material_id} - {quantity} units by {directorate}")
    
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
                logger.error(f"Insufficient inventory: {material.material_id}")
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
        
        logger.info(f"Inventory updated: {material.material_id} - New balance: {balance.available_quantity}")
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
                'material_id': material.material_id,
                'material_name': material.material_name,
                'available': str(balance.available_quantity),
            })
    
    return {
        'total_materials': total_materials,
        'total_inventory_value': str(total_value),
        'low_stock_items': low_stock,
        'low_stock_count': len(low_stock),
    }


def get_material_transaction_history(material_id: str) -> list:
    """Get all transactions for a specific material"""
    
    try:
        material = Material.objects.get(material_id=material_id)
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
        logger.error(f"Material not found: {material_id}")
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
            'material_id': txn.material.material_id,
            'material_name': txn.material.material_name,
            'quantity_taken': str(txn.quantity),
            'date': txn.transaction_date.strftime('%Y-%m-%d'),
        })
    
    return {
        'directorate': directorate,
        'total_items_taken': str(total_items_taken),
        'items': items_detail,
    }

