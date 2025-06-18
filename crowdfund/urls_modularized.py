from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication urls
    path('accounts/', include('accounts.urls')),
    
    # Modularized app urls
    path('campaigns/', include('campaigns.urls')),
    path('organizations/', include('organizations.urls')),
    path('donations/', include('donations.urls')),
    
    # Home page and public routes
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    
    # Legacy routes (for compatibility during transition)
    path('funding/', include('funding.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
