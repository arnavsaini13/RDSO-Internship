"""
Intelligent Inventory Management System (IIMS) Views
Smart PDF analysis, Material tracking, Inventory Balance, Transaction History
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime, timedelta
import csv
import tempfile
import os

from .models import Material, InventoryBalance, InventoryTransaction, UserProfile
from .pdf_analyzer import analyze_receipt_pdf
from .utils import (
    create_material_from_pdf_data,
    create_initial_inventory_balance,
    update_inventory_balance,
    get_inventory_status,
    get_material_transaction_history,
    get_directorate_inventory,
)
from .forms_inventory import (
    MaterialUploadForm,
    MaterialConfirmForm,
    InventoryTransactionForm,
    InventorySearchForm,
    TransactionFilterForm,
)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def dashboard(request):
    """Dashboard - Inventory Overview"""
    
    # Get inventory status
    status = get_inventory_status()
    
    # Get recent materials
    recent_materials = Material.objects.all()[:10]
    
    # Get recent transactions
    recent_transactions = InventoryTransaction.objects.all()[:15]
    
    # Get statistics
    total_materials = Material.objects.count()
    total_balance_value = sum(
        (mat.total_cost or 0) for mat in Material.objects.all()
    )
    
    # Get take transactions count
    total_takes = InventoryTransaction.objects.filter(action='TAKE').count()
    total_returns = InventoryTransaction.objects.filter(action='RETURN').count()
    
    # Get directorates using materials
    directorates = InventoryTransaction.objects.values_list(
        'directorate', flat=True
    ).distinct().count()
    
    context = {
        'status': status,
        'recent_materials': recent_materials,
        'recent_transactions': recent_transactions,
        'total_materials': total_materials,
        'total_balance_value': total_balance_value,
        'total_takes': total_takes,
        'total_returns': total_returns,
        'total_directorates': directorates,
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def upload_material(request):
    """Upload new material from vendor receipt PDF"""
    
    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                receipt_pdf = request.FILES['receipt_pdf']
                
                # Save file temporarily to analyze
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    for chunk in receipt_pdf.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                
                # Analyze PDF
                extracted_data = analyze_receipt_pdf(tmp_path)
                os.unlink(tmp_path)
                
                # Store in session for preview/confirmation
                request.session['pdf_data'] = extracted_data
                request.session['pdf_file_name'] = receipt_pdf.name
                
                messages.success(request, 'PDF analyzed successfully! Please confirm the extracted data.')
                return redirect('confirm_material')
            
            except Exception as e:
                messages.error(request, f'Error analyzing PDF: {str(e)}')
    else:
        form = MaterialUploadForm()
    
    context = {'form': form}
    return render(request, 'inventory/upload_material.html', context)


@login_required
def confirm_material(request):
    """Confirm extracted data and create material"""
    
    extracted_data = request.session.get('pdf_data')
    pdf_file_name = request.session.get('pdf_file_name')
    
    if not extracted_data:
        messages.error(request, 'No extracted data found. Please upload a receipt.')
        return redirect('upload_material')
    
    if request.method == 'POST':
        # Get the receipt PDF from FILES
        receipt_pdf = request.FILES.get('receipt_pdf')
        
        if not receipt_pdf:
            messages.error(request, 'Receipt PDF is required.')
            return redirect('upload_material')
        
        try:
            # Update extracted data from form (user can edit)
            for key in ['material_name', 'vendor_name', 'quantity', 'date_received']:
                if key in request.POST:
                    extracted_data[key] = request.POST[key]
            
            # Create material
            material = create_material_from_pdf_data(
                extracted_data,
                receipt_pdf,
                request.user
            )
            
            # Create initial inventory balance
            create_initial_inventory_balance(material)
            
            # Log transaction
            InventoryTransaction.objects.create(
                material=material,
                action='INITIAL',
                quantity=material.quantity,
                directorate='Vendor Receipt',
                transaction_by=request.user,
                remarks='Initial stock from vendor receipt',
                ip_address=get_client_ip(request),
            )
            
            # Clear session
            request.session.pop('pdf_data', None)
            request.session.pop('pdf_file_name', None)
            
            messages.success(request, f'Material {material.material_id} created successfully!')
            return redirect('material_detail', pk=material.id)
        
        except Exception as e:
            messages.error(request, f'Error creating material: {str(e)}')
    
    context = {
        'extracted_data': extracted_data,
        'pdf_file_name': pdf_file_name,
    }
    return render(request, 'inventory/confirm_material.html', context)


@login_required
def material_list(request):
    """List all materials"""
    
    materials = Material.objects.all()
    
    # Search
    search_q = request.GET.get('search', '')
    if search_q:
        materials = materials.filter(
            Q(material_id__icontains=search_q) |
            Q(material_name__icontains=search_q) |
            Q(vendor_name__icontains=search_q)
        )
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        materials = materials.filter(category=category)
    
    # Pagination
    paginator = Paginator(materials, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_q': search_q,
    }
    
    return render(request, 'inventory/material_list.html', context)


@login_required
def material_detail(request, pk):
    """Material detail view"""
    
    material = get_object_or_404(Material, pk=pk)
    balance = material.balance
    transactions = material.transactions.all()
    
    context = {
        'material': material,
        'balance': balance,
        'transactions': transactions,
    }
    
    return render(request, 'inventory/material_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def take_material(request, material_id):
    """Record material taken by directorate"""
    
    material = get_object_or_404(Material, material_id=material_id)
    
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            quantity = Decimal(form.cleaned_data['quantity'])
            directorate = form.cleaned_data['directorate']
            remarks = form.cleaned_data.get('remarks', '')
            
            # Check if sufficient stock
            if material.balance.available_quantity < quantity:
                messages.error(request, f'Insufficient stock! Available: {material.balance.available_quantity}')
                return redirect('material_detail', pk=material.id)
            
            # Update inventory
            success = update_inventory_balance(
                material=material,
                action='TAKE',
                quantity=quantity,
                directorate=directorate,
                transaction_by=request.user,
                remarks=remarks,
                ip_address=get_client_ip(request),
            )
            
            if success:
                messages.success(request, f'{quantity} units taken by {directorate}')
                return redirect('material_detail', pk=material.id)
            else:
                messages.error(request, 'Error updating inventory')
    else:
        form = InventoryTransactionForm()
    
    context = {'material': material, 'form': form, 'action': 'TAKE'}
    return render(request, 'inventory/transaction.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def return_material(request, material_id):
    """Record material returned by directorate"""
    
    material = get_object_or_404(Material, material_id=material_id)
    
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            quantity = Decimal(form.cleaned_data['quantity'])
            directorate = form.cleaned_data['directorate']
            return_reason = request.POST.get('return_reason', '')
            remarks = form.cleaned_data.get('remarks', '')
            
            # Update inventory
            success = update_inventory_balance(
                material=material,
                action='RETURN',
                quantity=quantity,
                directorate=directorate,
                transaction_by=request.user,
                return_reason=return_reason,
                remarks=remarks,
                ip_address=get_client_ip(request),
            )
            
            if success:
                messages.success(request, f'{quantity} units returned by {directorate}')
                return redirect('material_detail', pk=material.id)
            else:
                messages.error(request, 'Error updating inventory')
    else:
        form = InventoryTransactionForm()
    
    context = {'material': material, 'form': form, 'action': 'RETURN'}
    return render(request, 'inventory/transaction.html', context)


@login_required
def inventory_balance(request):
    """View current inventory balance"""
    
    balances = InventoryBalance.objects.all().select_related('material')
    
    # Search
    search_q = request.GET.get('search', '')
    if search_q:
        balances = balances.filter(
            Q(material__material_id__icontains=search_q) |
            Q(material__material_name__icontains=search_q)
        )
    
    # Filter low stock
    show_low_stock = request.GET.get('low_stock')
    if show_low_stock:
        balances = balances.filter(available_quantity__lte=10)
    
    # Pagination
    paginator = Paginator(balances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_q': search_q,
        'show_low_stock': show_low_stock,
    }
    
    return render(request, 'inventory/balance.html', context)


@login_required
def transaction_history(request):
    """View transaction history"""
    
    transactions = InventoryTransaction.objects.select_related('material').all()
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        transactions = transactions.filter(action=action)
    
    # Filter by directorate
    directorate = request.GET.get('directorate')
    if directorate:
        transactions = transactions.filter(directorate=directorate)
    
    # Filter by date range
    days = request.GET.get('days')
    if days:
        try:
            date_from = datetime.now() - timedelta(days=int(days))
            transactions = transactions.filter(transaction_date__gte=date_from)
        except (ValueError, TypeError):
            pass
    
    # Pagination
    paginator = Paginator(transactions, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique directorates
    directorates = InventoryTransaction.objects.values_list(
        'directorate', flat=True
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'directorates': directorates,
        'action': action,
        'directorate': directorate,
        'days': days,
    }
    
    return render(request, 'inventory/transaction_history.html', context)


@login_required
def export_inventory(request):
    """Export inventory data to CSV"""
    
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Only admins can export data.')
        return redirect('dashboard')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Material ID', 'Material Name', 'Available Quantity',
        'Unit Price', 'Total Cost', 'Vendor', 'Date Received'
    ])
    
    for balance in InventoryBalance.objects.all():
        material = balance.material
        writer.writerow([
            material.material_id,
            material.material_name,
            balance.available_quantity,
            material.unit_price or '',
            material.total_cost or '',
            material.vendor_name,
            material.date_received,
        ])
    
    return response


@login_required
def export_transactions(request):
    """Export transaction history to CSV"""
    
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
        messages.error(request, 'Only admins can export data.')
        return redirect('dashboard')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Material ID', 'Material Name', 'Action', 'Quantity',
        'Directorate', 'Date', 'User', 'Remarks'
    ])
    
    for txn in InventoryTransaction.objects.select_related('material'):
        writer.writerow([
            txn.material.material_id,
            txn.material.material_name,
            txn.get_action_display(),
            txn.quantity,
            txn.directorate,
            txn.transaction_date,
            txn.transaction_by.username if txn.transaction_by else '',
            txn.remarks or '',
        ])
    
    return response
