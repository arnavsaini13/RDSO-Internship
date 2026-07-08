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
    
    # Auto-copy seed PDF from repo directory to media storage if missing on Render
    if not os.path.exists(full_path):
        file_name = os.path.basename(path)
        source_in_repo = os.path.join(settings.BASE_DIR, file_name)
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
