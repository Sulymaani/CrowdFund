from django.urls import path

app_name = 'org'
from .views import (
    CampaignCreateView,
    CampaignEditView,
    CampaignCloseView,
    DonationsListView,
    ExportDonationsCSVView,
    OrgCampaignsListView,
    OrgCampaignDetailView,
    OrgDonationDetailView,
    OrganisationSettingsView,
)

urlpatterns = [
    # Organization owner campaign management
    path('campaigns/', OrgCampaignsListView.as_view(), name='campaigns'),
    path('campaigns/<int:pk>/', OrgCampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/new/', CampaignCreateView.as_view(), name='campaign_new'),
    path('campaigns/<int:pk>/edit/', CampaignEditView.as_view(), name='campaign_edit'),
    path('campaigns/<int:pk>/close/', CampaignCloseView.as_view(), name='campaign_close'),
    
    # Organization donations management
    path('donations/', DonationsListView.as_view(), name='donations_list'),
    path('donations/export/', ExportDonationsCSVView.as_view(), name='export_donations'),
    path('donations/<str:reference_number>/', OrgDonationDetailView.as_view(), name='donation_detail'),
    
    # Organization settings
    path('settings/', OrganisationSettingsView.as_view(), name='settings'),
]
