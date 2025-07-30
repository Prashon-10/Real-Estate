from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import index
from accounts.admin_site import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('admin-panel/', include('admin_panel.urls')),  # Custom admin panel
    path('', index, name='index'),
    path('accounts/', include('accounts.urls')),
    path('properties/', include('properties.urls')),
    path('chat/', include('chat.urls')),
    path('search/', include('search.urls')),
    path('dashboard/', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)