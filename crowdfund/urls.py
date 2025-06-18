"""
URL configuration for crowdfund project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView

handler404 = 'core.views.custom_page_not_found_view'
handler403 = 'core.views.custom_permission_denied_view'

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('__django_admin__/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # For password reset, etc.,

    # New modularized apps - primary URLs
    path('campaigns/', include('campaigns.urls', namespace='campaigns')),
    path('organizations/', include('organizations.urls', namespace='organizations')),
    path('donations/', include('donations.urls', namespace='donations')),
    path('tags/', include('tags.urls', namespace='tags')),
    path('donor/', include('accounts.urls_donor', namespace='donor')),
    
    # API endpoints
    path('api/v1/', include('api.urls')),
    
    # Legacy URLs (for backward compatibility during transition)
    path('donor/', include('funding.donor_urls', namespace='donor_legacy')),  # Legacy donor URLs
    path('org/', include('funding.org_urls')),  # Legacy organization URLs
    path('admin/', include('core.urls', namespace='core_admin')),  # Admin URLs
    path('', include('funding.urls')),  # Legacy main app URLs
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
