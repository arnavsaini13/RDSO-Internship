from django.contrib import admin
from .models import Material, InventoryBalance, InventoryTransaction


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('material_id', 'material_name', 'vendor_name', 'quantity', 'date_received', 'uploaded_by')
    list_filter = ('category', 'vendor_name', 'date_received', 'uploaded_at')
    search_fields = ('material_id', 'material_name', 'vendor_name', 'batch_number')
    readonly_fields = ('material_id', 'uploaded_at', 'updated_at', 'extracted_data')
    date_hierarchy = 'date_received'
    
    fieldsets = (
        ('Material Information', {
            'fields': ('material_id', 'material_name', 'quantity', 'vendor_name', 'date_received')
        }),
        ('Receipt Details', {
            'fields': ('receipt_pdf', 'extracted_data')
        }),
        ('Pricing & Category', {
            'fields': ('unit_price', 'total_cost', 'category', 'hsn_code')
        }),
        ('Additional Information', {
            'fields': ('description', 'batch_number', 'storage_location', 'condition_notes', 'expiry_date'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InventoryBalance)
class InventoryBalanceAdmin(admin.ModelAdmin):
    list_display = ('get_material_id', 'get_material_name', 'available_quantity', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('material__material_id', 'material__material_name')
    readonly_fields = ('last_updated', 'material')
    
    def get_material_id(self, obj):
        return obj.material.material_id
    get_material_id.short_description = 'Material ID'
    
    def get_material_name(self, obj):
        return obj.material.material_name
    get_material_name.short_description = 'Material Name'


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('material', 'action', 'quantity', 'directorate', 'transaction_date', 'transaction_by')
    list_filter = ('action', 'transaction_date', 'directorate', 'return_reason')
    search_fields = ('material__material_id', 'material__material_name', 'directorate')
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

