from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as django_serve
import os
import shutil

def custom_serve_media(request, path, document_root=None, **kwargs):
    if not document_root:
        document_root = settings.MEDIA_ROOT
        
    full_path = os.path.join(document_root, path)
    
    # Auto-generate or copy missing media assets on the fly
    if not os.path.exists(full_path):
        file_name = os.path.basename(path)
        
        # 1. If it's a barcode request, regenerate the barcode image on the fly!
        if path.startswith('barcodes/'):
            import re
            # Match formats like barcode_10.png or barcode_SR-00000010.png
            match = re.search(r'barcode_(?:SR-)?(\d+)\.png', file_name)
            if match:
                try:
                    serial_number = int(match.group(1))
                    from django.apps import apps
                    Material = apps.get_model('documents', 'Material')
                    material = Material.objects.filter(serial_number=serial_number).first()
                    if material:
                        from documents.barcode_utils import regenerate_barcode
                        regenerate_barcode(material)
                except Exception as e:
                    print(f"[MEDIA-SERVE] Failed to auto-generate barcode: {e}")
                    
        # 2. Otherwise, restore the seed receipts
        else:
            source_in_repo = os.path.join(settings.BASE_DIR, 'seed_receipts', file_name)
            if os.path.exists(source_in_repo):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                try:
                    shutil.copy2(source_in_repo, full_path)
                except Exception as e:
                    print(f"[MEDIA-SERVE] Failed to copy seed file: {e}")
                
    return django_serve(request, path, document_root, **kwargs)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('documents.urls')),
    path('auth/', include('users.urls')),
]

# Serve media files in both development and production for demo purposes
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', custom_serve_media, {'document_root': settings.MEDIA_ROOT}),
]
