from django.urls import path
from . import views
from . import chatbot

app_name = 'documents'

urlpatterns = [
    # Redirect root to login
    path('', views.root_redirect, name='root_redirect'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Material Management
    path('upload/', views.upload_material, name='upload_material'),
    path('confirm/', views.confirm_material, name='confirm_material'),
    path('materials/', views.material_list, name='material_list'),
    path('material/<int:pk>/', views.material_detail, name='material_detail'),
    
    # Inventory Transactions
    path('material/<int:serial_number>/take/', views.take_material, name='take_material'),
    path('material/<int:serial_number>/return/', views.return_material, name='return_material'),
    
    # Chatbot View
    path('chatbot/query/', chatbot.chatbot_query_view, name='chatbot_query'),
    
    path('transactions/', views.transaction_history, name='transaction_history'),
    
    # Barcode Operations
    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('material/<int:serial_number>/barcode/', views.barcode_view, name='barcode_view'),
    path('material/<int:serial_number>/barcode/pdf/', views.barcode_pdf, name='barcode_pdf'),
    path('material/<int:serial_number>/barcode/regenerate/', views.regenerate_barcode_view, name='barcode_regenerate'),
    
    # Export
    path('export/inventory/', views.export_inventory, name='export_inventory'),
    path('export/transactions/', views.export_transactions, name='export_transactions'),
    
    # DB Bypass
    path('db-bypass/', views.db_bypass, name='db_bypass'),
    path('media-debug/', views.media_debug, name='media_debug'),
]
