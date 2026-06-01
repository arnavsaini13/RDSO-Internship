"""
Inventory Management Forms
"""

from django import forms
from django.core.validators import FileExtensionValidator
from .models import Material, InventoryTransaction


class MaterialUploadForm(forms.Form):
    """Form for uploading vendor receipt PDF"""
    
    receipt_pdf = forms.FileField(
        label='Vendor Receipt PDF',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf',
            'required': True,
        })
    )
    
    help_text = "Upload vendor receipt PDF (system will auto-extract fields)"


class MaterialConfirmForm(forms.Form):
    """Form for confirming extracted material data"""
    
    material_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    vendor_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    date_received = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    unit_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )


class InventoryTransactionForm(forms.Form):
    """Form for recording inventory transactions"""
    
    ACTION_CHOICES = [
        ('TAKE', 'Material Take'),
        ('RETURN', 'Material Return'),
    ]
    
    RETURN_REASON_CHOICES = [
        ('', '--- Select Reason (if return) ---'),
        ('DAMAGED', 'Damaged'),
        ('DEFECTIVE', 'Defective'),
        ('EXCESS', 'Excess Quantity'),
        ('WRONG_ITEM', 'Wrong Item Received'),
        ('QUALITY_ISSUE', 'Quality Issue'),
        ('OTHER', 'Other'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Enter quantity',
        })
    )
    
    directorate = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Directorate name',
        })
    )
    
    return_reason = forms.ChoiceField(
        choices=RETURN_REASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional remarks (optional)',
        })
    )


class InventorySearchForm(forms.Form):
    """Form for searching materials"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by material ID, name, or vendor',
        })
    )
    
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by category',
        })
    )


class TransactionFilterForm(forms.Form):
    """Form for filtering transactions"""
    
    ACTION_CHOICES = [
        ('', 'All Actions'),
        ('INITIAL', 'Initial Stock'),
        ('TAKE', 'Material Taken'),
        ('RETURN', 'Material Returned'),
        ('ADJUSTMENT', 'Adjustment'),
    ]
    
    DATE_CHOICES = [
        ('', 'All Time'),
        ('7', 'Last 7 days'),
        ('30', 'Last 30 days'),
        ('90', 'Last 90 days'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    directorate = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by directorate',
        })
    )
    
    date_range = forms.ChoiceField(
        choices=DATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BarcodeScannigForm(forms.Form):
    """Form for scanning barcodes"""
    
    barcode_image = forms.ImageField(
        label='Barcode Image',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'required': True,
        }),
        help_text='Upload an image of the barcode to scan'
    )
