import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.core.management import call_command
from documents.models import Material
from django.contrib.auth.models import User

def main():
    # 1. Run database migrations
    print("[BOOTSTRAP] Running migrations...")
    call_command('migrate', no_input=True)

    # 2. Check if database has data
    material_count = Material.objects.count()
    print(f"[BOOTSTRAP] Detected {material_count} materials in the database.")

    if material_count < 11:
        print("[BOOTSTRAP] Database lacks the 11 items. Flushing and loading db_dump.json...")
        try:
            call_command('flush', interactive=False)
            call_command('loaddata', 'db_dump.json')
            print("[BOOTSTRAP] Database loaded successfully.")

            # 3. Regenerate all barcode images
            from regenerate_barcodes import run as regenerate_barcodes
            regenerate_barcodes()
        except Exception as e:
            print(f"[BOOTSTRAP] ERROR loading initial data: {e}")
            
    # 4. Force set password for admin@rdso.railnet.gov.in to Admin@123456
    try:
        u = User.objects.filter(email__iexact='admin@rdso.railnet.gov.in').first()
        if u:
            u.set_password('Admin@123456')
            u.save()
            print("[BOOTSTRAP] Successfully set password for admin@rdso.railnet.gov.in to Admin@123456")
        else:
            print("[BOOTSTRAP] Admin user admin@rdso.railnet.gov.in not found to set password.")
    except Exception as e:
        print(f"[BOOTSTRAP] ERROR setting admin password: {e}")

    # 5. Delete specific user accounts requested by user (arnav25100@iiitnr.edu.in and arnav131106@gmail.com)
    try:
        deleted_count, details = User.objects.filter(email__in=['arnav25100@iiitnr.edu.in', 'arnav131106@gmail.com']).delete()
        if deleted_count > 0:
            print(f"[BOOTSTRAP] Successfully deleted {deleted_count} user accounts from Render database: {details}")
        else:
            print("[BOOTSTRAP] Requested user accounts for deletion were not found or already deleted.")
    except Exception as e:
        print(f"[BOOTSTRAP] ERROR deleting requested user accounts: {e}")

if __name__ == '__main__':
    main()
