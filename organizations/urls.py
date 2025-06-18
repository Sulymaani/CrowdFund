from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    # Public organization browsing
    path('', views.OrganizationListView.as_view(), name='list'),
    path('<int:pk>/', views.OrganisationDetailView.as_view(), name='detail'),
    
    # Organization owner routes
    path('dashboard/', views.OrgDashboardView.as_view(), name='dashboard'),
    path('settings/', views.OrganisationSettingsView.as_view(), name='settings'),
    
    # Utility routes
    path('export-donations/', views.ExportDonationsCSVView.as_view(), name='export_donations'),
]
