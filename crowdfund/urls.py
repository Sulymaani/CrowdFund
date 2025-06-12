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
from core.views import HomeView
from funding.views import DonorDashboardView, OrgDashboardView


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path('__django_admin__/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # For password reset, etc.

    # Dashboards
    path('dashboard/donor/', DonorDashboardView.as_view(), name='donor_dashboard'),
    path('dashboard/org/', OrgDashboardView.as_view(), name='org_dashboard'),

    # Admin URLs
    path('admin/', include('core.urls', namespace='core_admin')),

    # Main app (campaigns, etc.)
    path('', include('funding.urls')),
]
