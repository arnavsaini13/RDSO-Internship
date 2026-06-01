from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Material Management
    path('upload/', views.upload_material, name='upload_material'),
    path('confirm/', views.confirm_material, name='confirm_material'),
    path('materials/', views.material_list, name='material_list'),
    path('material/<int:pk>/', views.material_detail, name='material_detail'),
    
    # Inventory Transactions
    path('material/<str:material_id>/take/', views.take_material, name='take_material'),
    path('material/<str:material_id>/return/', views.return_material, name='return_material'),
    
    # Inventory Views
    path('balance/', views.inventory_balance, name='inventory_balance'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    
    # Barcode Operations
    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('material/<str:material_id>/barcode/', views.barcode_view, name='barcode_view'),
    path('material/<str:material_id>/barcode/pdf/', views.barcode_pdf, name='barcode_pdf'),
    path('material/<str:material_id>/barcode/regenerate/', views.regenerate_barcode_view, name='regenerate_barcode'),
    
    # Export
    path('export/inventory/', views.export_inventory, name='export_inventory'),
    path('export/transactions/', views.export_transactions, name='export_transactions'),
]

