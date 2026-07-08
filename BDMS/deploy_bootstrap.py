import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from django.core.management import call_command
from documents.models import Material

def main():
    # 1. Run database migrations
    print("[BOOTSTRAP] Running migrations...")
    call_command('migrate', no_input=True)

    # 2. Check if database has data
    material_count = Material.objects.count()
    print(f"[BOOTSTRAP] Detected {material_count} materials in the database.")

    if material_count == 0:
        print("[BOOTSTRAP] Database is empty. Initiating data load from db_dump.json...")
        try:
            call_command('loaddata', 'db_dump.json')
            print("[BOOTSTRAP] Database loaded successfully.")

            # 3. Regenerate all barcode images
            from regenerate_barcodes import run as regenerate_barcodes
            regenerate_barcodes()
        except Exception as e:
            print(f"[BOOTSTRAP] ERROR loading initial data: {e}")
    else:
        print("[BOOTSTRAP] Database already initialized. Skipping mock/import load to preserve live updates.")

if __name__ == '__main__':
    main()
