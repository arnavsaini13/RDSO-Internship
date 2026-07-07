from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import json

# ============================================
# INTELLIGENT INVENTORY MANAGEMENT SYSTEM
# ============================================

class Material(models.Model):
    """Master Materials Table - Vendor Receipts with Flexible Fields"""
    
    # Auto-generated sequential serial number
    serial_number = models.IntegerField(unique=True, verbose_name="Serial Number", default=1)
    
    # Core fields (extracted from PDF)
    material_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    
    # PDF and receipt info
    receipt_pdf = models.FileField(
        upload_to='receipts/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    extracted_data = models.JSONField(default=dict, blank=True)  # All extracted fields stored as JSON
    
    # Vendor information
    vendor_name = models.CharField(max_length=255)
    date_received = models.DateField()
    
    # Optional fields (flexible - extracted from PDF)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    ro_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="RO Number")
    vendor_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vendor Code")
    hsn_code = models.CharField(max_length=50, blank=True, null=True)
    storage_location = models.CharField(max_length=255, blank=True, null=True)
    condition_notes = models.TextField(blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # RDSO Specific Fields
    consignee = models.CharField(max_length=255, blank=True, null=True)
    r_note_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="R/Note No.")
    po_at_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="PO/AT No.")
    pl_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="PL No.")
    
    # Barcode
    barcode_image = models.ImageField(
        upload_to='barcodes/',
        null=True,
        blank=True,
        help_text='Auto-generated barcode image for this material'
    )
    barcode_data = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text='Barcode data (usually same as serial_number)'
    )
    
    # Tracking
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_received']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['-date_received']),
            models.Index(fields=['vendor_name']),
        ]
    
    def __str__(self):
        return f"SR-{self.serial_number} - {self.material_name}"
    
    def get_all_fields(self):
        """Return all fields including extracted data"""
        data = {
            'serial_number': self.serial_number,
            'material_name': self.material_name,
            'quantity': str(self.quantity),
            'vendor_name': self.vendor_name,
            'date_received': self.date_received.isoformat(),
        }
        # Add all extracted fields from PDF
        if self.extracted_data:
            data.update(self.extracted_data)
        return data


class InventoryBalance(models.Model):
    """Current Inventory Balance - Shows Latest Available Quantity Only"""
    
    material = models.OneToOneField(Material, on_delete=models.CASCADE, related_name='balance')
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['material__material_name']
        indexes = [
            models.Index(fields=['material']),
        ]
    
    def __str__(self):
        return f"{self.material.material_name} - {self.available_quantity} units"


class InventoryTransaction(models.Model):
    """Transaction History - Audit Trail (Never Deleted, All Records Visible)"""
    
    ACTION_CHOICES = [
        ('INITIAL', 'Initial Stock from Receipt'),
        ('TAKE', 'Material Taken by Directorate'),
        ('RETURN', 'Material Returned'),
        ('ADJUSTMENT', 'Quantity Adjustment'),
    ]
    
    RETURN_REASON_CHOICES = [
        ('DAMAGED', 'Damaged'),
        ('DEFECTIVE', 'Defective'),
        ('EXCESS', 'Excess Quantity'),
        ('WRONG_ITEM', 'Wrong Item Received'),
        ('QUALITY_ISSUE', 'Quality Issue'),
        ('OTHER', 'Other'),
    ]
    
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Who took/returned the material
    directorate = models.CharField(max_length=255)
    
    # Reason for return (if applicable)
    return_reason = models.CharField(
        max_length=50, 
        choices=RETURN_REASON_CHOICES,
        blank=True, 
        null=True
    )
    remarks = models.TextField(blank=True, null=True)
    
    # Tracking
    transaction_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['material', '-transaction_date']),
            models.Index(fields=['action', '-transaction_date']),
            models.Index(fields=['directorate']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.material.material_name} - {self.quantity} units - {self.transaction_date.strftime('%Y-%m-%d')}"
