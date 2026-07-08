import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

# Run database migrations and load dump automatically on startup
try:
    from django.core.management import call_command
    from django.contrib.auth.models import User
    from documents.models import Material
    
    # 1. Run migrations
    print("[WSGI-BOOTSTRAP] Running migrations...")
    call_command('migrate', no_input=True)
    
    # 2. Check and load dump
    material_count = Material.objects.count()
    print(f"[WSGI-BOOTSTRAP] Detected {material_count} materials.")
    if material_count < 11:
        print("[WSGI-BOOTSTRAP] Database lacks the 11 local items. Flushing and loading db_dump.json...")
        call_command('flush', no_input=True)
        call_command('loaddata', 'db_dump.json')
        print("[WSGI-BOOTSTRAP] Database loaded successfully.")
        
        # Regenerate all barcodes
        from regenerate_barcodes import run as regenerate_barcodes
        regenerate_barcodes()
    
    # 3. Always force-set/verify password for admin
    u = User.objects.filter(email__iexact='admin@rdso.railnet.gov.in').first()
    if u:
        u.set_password('Admin@123456')
        u.save()
        print("[WSGI-BOOTSTRAP] Admin password force-set successfully to Admin@123456.")
    else:
        print("[WSGI-BOOTSTRAP] Admin user not found.")
        
    # 4. Close database connections so they are not shared with Gunicorn forks (prevents SSL errors)
    from django.db import connections
    for conn in connections.all():
        conn.close()
    print("[WSGI-BOOTSTRAP] Closed all boot-time database connections to prevent Gunicorn fork-sharing SSL issues.")
        
except Exception as e:
    print(f"[WSGI-BOOTSTRAP] ERROR: {e}")

application = get_wsgi_application()
