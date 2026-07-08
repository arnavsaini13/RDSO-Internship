import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BDMS.settings')
django.setup()

from documents.models import Material
from documents.barcode_utils import regenerate_barcode

def run():
    print("Regenerating all barcode images for materials...")
    materials = Material.objects.all()
    for m in materials:
        success = regenerate_barcode(m)
        print(f"[BARCODE] Material SR-{m.serial_number} ({m.material_name[:30]}): {'Success' if success else 'Failed'}")
    print("All barcode images regenerated successfully!")

if __name__ == '__main__':
    run()
