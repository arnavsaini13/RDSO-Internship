from django.contrib import admin
from django.utils.html import format_html
from .models import Material, InventoryBalance, InventoryTransaction


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'material_name', 'vendor_name', 'r_note_no', 
        'po_at_no', 'pl_no', 'ro_number', 'vendor_code', 'hsn_code', 
        'consignee', 'quantity', 'unit_price', 'total_cost', 'display_barcode',
        'date_received', 'get_uploaded_by', 'view_pdf'
    )
    list_filter = ('vendor_name', 'consignee', 'date_received', 'uploaded_at')
    search_fields = ('serial_number', 'material_name', 'vendor_name', 'r_note_no', 'po_at_no', 'pl_no', 'ro_number', 'vendor_code')
    readonly_fields = ('serial_number', 'uploaded_at', 'updated_at', 'extracted_data', 'barcode_data')
    date_hierarchy = 'date_received'
    
    fieldsets = (
        ('Material Information', {
            'fields': ('serial_number', 'material_name', 'quantity', 'vendor_name', 'date_received')
        }),
        ('RDSO Receipt Note Details', {
            'fields': ('consignee', 'r_note_no', 'po_at_no', 'pl_no', 'ro_number', 'vendor_code')
        }),
        ('Receipt Details', {
            'fields': ('receipt_pdf', 'extracted_data')
        }),
        ('Pricing & Barcode', {
            'fields': ('unit_price', 'total_cost', 'barcode_data', 'hsn_code')
        }),
        ('Additional Information', {
            'fields': ('description', 'storage_location', 'condition_notes', 'expiry_date'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_uploaded_by(self, obj):
        if obj.uploaded_by:
            full_name = f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip()
            return full_name if full_name else obj.uploaded_by.username
        return "-"
    get_uploaded_by.short_description = 'Uploaded By'

    def display_barcode(self, obj):
        if obj.barcode_image:
            return format_html('<img src="{}" style="height: 35px; max-width: 150px; display: block;" />', obj.barcode_image.url)
        return "-"
    display_barcode.short_description = 'Barcode'

    def view_pdf(self, obj):
        if obj.receipt_pdf:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.receipt_pdf.url)
        return "-"
    view_pdf.short_description = 'Receipt PDF'


@admin.register(InventoryBalance)
class InventoryBalanceAdmin(admin.ModelAdmin):
    list_display = ('get_serial_number', 'get_material_name', 'available_quantity', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('material__serial_number', 'material__material_name')
    readonly_fields = ('last_updated', 'material')
    
    def get_serial_number(self, obj):
        return obj.material.serial_number
    get_serial_number.short_description = 'Serial Number'
    
    def get_material_name(self, obj):
        return obj.material.material_name
    get_material_name.short_description = 'Material Name'


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('material', 'action', 'quantity', 'directorate', 'transaction_date', 'transaction_by')
    list_filter = ('action', 'transaction_date', 'directorate', 'return_reason')
    search_fields = ('material__serial_number', 'material__material_name', 'directorate')
    readonly_fields = ('transaction_date', 'material')
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('material', 'action', 'quantity', 'transaction_date')
        }),
        ('Directorate & User', {
            'fields': ('directorate', 'transaction_by')
        }),
        ('Return Information', {
            'fields': ('return_reason', 'remarks'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('ip_address',),
            'classes': ('collapse',)
        }),
    )

