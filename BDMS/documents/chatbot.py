import requests
import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Material, InventoryBalance, InventoryTransaction

def get_database_context():
    # 1. Get Materials & Balances
    materials = Material.objects.all().select_related('balance')
    mat_list = []
    for m in materials:
        avail = m.balance.available_quantity if hasattr(m, 'balance') else 0
        mat_list.append(f"- SR-{m.serial_number}: {m.material_name} | Vendor: {m.vendor_name} | Stock: {avail}/{m.quantity} units | Unit Price: Rs. {m.unit_price}")
    materials_str = "\n".join(mat_list) if mat_list else "No materials found in inventory."

    # 2. Get Recent Transactions
    transactions = InventoryTransaction.objects.all().select_related('material', 'transaction_by').order_by('-transaction_date')[:8]
    tx_list = []
    for t in transactions:
        tx_list.append(f"- {t.transaction_date.strftime('%d %b %Y, %H:%M')}: {t.action} of {t.quantity} units of '{t.material.material_name}' (SR-{t.material.serial_number}) by user '{t.transaction_by.username if t.transaction_by else 'System'}' for Directorate/Section '{t.directorate}'")
    transactions_str = "\n".join(tx_list) if tx_list else "No recent transactions logged."
    
    return materials_str, transactions_str

def ask_gemini(query):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
        
    materials_str, transactions_str = get_database_context()
    
    prompt = f"""You are the Docufy AI Assistant, an interactive chatbot for the RDSO (Research Designs and Standards Organisation) Barcode Document Management System (SmartTrack) and Inventory Information Management System (IIMS).

Here is the current live inventory state of materials:
{materials_str}

Here are the recent transaction logs:
{transactions_str}

User's Question: {query}

Use the live data above to answer the user's question accurately. If the user asks about stock levels, valuation, low stock, or transactions, refer to the data above.
If the question is unrelated to the inventory, answer politely but remind them of your purpose.
Be concise, professional, polite, and helpful. Mention that you are the Docufy Assistant."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            return text
        else:
            return None
    except Exception:
        return None

def ask_offline_fallback(query):
    query_lower = query.lower()
    materials_str, transactions_str = get_database_context()
    
    # Check for stock inquiries
    if "low" in query_lower or "exhausted" in query_lower or "reorder" in query_lower:
        low_items = []
        balances = InventoryBalance.objects.all().select_related('material')
        for b in balances:
            if b.available_quantity <= 10:
                low_items.append(f"- {b.material.material_name} (SR-{b.material.serial_number}): {b.available_quantity} units left")
        if low_items:
            return "Here are the materials currently running low on stock:\n" + "\n".join(low_items)
        return "All materials are currently well stocked! No low stock warnings."

    elif "recent" in query_lower or "activity" in query_lower or "transaction" in query_lower or "log" in query_lower:
        return f"Here is the recent activity log in the system:\n{transactions_str}"
        
    elif "how to" in query_lower or "help" in query_lower or "use" in query_lower:
        return ("Welcome to Docufy Help! Here's how to use the portal:\n"
                "1. **Upload Material**: Go to the 'Upload Material' page to drag/drop a vendor invoice PDF. The system will auto-extract items.\n"
                "2. **Print Barcodes**: Go to 'Material Inventory', click on a material, and click 'Print Barcode'.\n"
                "3. **Take/Return Stock**: Open a material workspace to deduct or add stock with automated transactions.")
                
    elif "valuation" in query_lower or "total cost" in query_lower or "worth" in query_lower:
        balances = InventoryBalance.objects.all().select_related('material')
        total_val = sum(b.available_quantity * b.material.unit_price for b in balances)
        return f"The total current valuation of all active stock in the depot is Rs. {total_val:,.2f}."
        
    # Search for specific material mentions
    matched_materials = []
    materials = Material.objects.all().select_related('balance')
    for m in materials:
        if m.material_name.lower() in query_lower or str(m.serial_number) in query_lower:
            avail = m.balance.available_quantity if hasattr(m, 'balance') else 0
            matched_materials.append(f"- **{m.material_name} (SR-{m.serial_number})**: {avail} units available out of {m.quantity} received from {m.vendor_name}. Price: Rs. {m.unit_price}")
            
    if matched_materials:
        return "I found the following matching items in the inventory:\n" + "\n".join(matched_materials)
        
    return ("I am the Docufy Assistant. I couldn't find a direct match for your request. "
            "You can ask me about stock levels (e.g. 'Is sleepers stock low?'), recent activity logs, or portal usage help.")

@csrf_exempt
@login_required
def chatbot_query_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            query = body.get('query', '').strip()
            if not query:
                return JsonResponse({'response': "Please enter a valid message."})
                
            # Try Gemini first
            response_text = ask_gemini(query)
            if not response_text:
                # Fallback to local rule-based solver
                response_text = ask_offline_fallback(query)
                
            return JsonResponse({'response': response_text})
        except Exception as e:
            return JsonResponse({'response': f"An error occurred: {str(e)}"}, status=500)
    return JsonResponse({'response': "Invalid request method."}, status=400)
