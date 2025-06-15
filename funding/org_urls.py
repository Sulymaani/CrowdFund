from django.urls import path

app_name = 'org'
from .views import (
    CampaignCreateView,
    CampaignEditView,
    CampaignCloseView,
    CampaignReactivateView,
    CampaignDeleteView,
    DonationsListView,
    ExportDonationsCSVView,
    OrgCampaignsListView,
    OrgCampaignDetailView,
    OrgDashboardView,
    OrgDonationDetailView,
    OrganisationSettingsView,
)

urlpatterns = [
    # Organization dashboard
    path('dashboard/', OrgDashboardView.as_view(), name='dashboard'),
    
    # Organization owner campaign management
    path('campaigns/', OrgCampaignsListView.as_view(), name='campaigns'),
    path('campaigns/<int:pk>/', OrgCampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/new/', CampaignCreateView.as_view(), name='campaign_new'),
    path('campaigns/<int:pk>/edit/', CampaignEditView.as_view(), name='campaign_edit'),
    path('campaigns/<int:pk>/close/', CampaignCloseView.as_view(), name='campaign_close'),
    path('campaigns/<int:pk>/reactivate/', CampaignReactivateView.as_view(), name='campaign_reactivate'),
    path('campaigns/<int:pk>/delete/', CampaignDeleteView.as_view(), name='campaign_delete'),
    
    # Organization donations management
    path('donations/', DonationsListView.as_view(), name='donations_list'),
    path('donations/export/', ExportDonationsCSVView.as_view(), name='export_donations'),
    path('donations/<str:reference_number>/', OrgDonationDetailView.as_view(), name='donation_detail'),
    
    # Organization settings
    path('settings/', OrganisationSettingsView.as_view(), name='settings'),
]
