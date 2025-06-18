from django.urls import path, include

# Import view modules
from .donor_views import (
    DonorDashboardView,
    DonorCampaignsView, 
    DonorOrganizationsView,
    DonorDonationDetailView,
    DonorProfileView
)

from .org_views import (
    OrgDashboardView,
    OrgCampaignsListView,
    OrgCampaignDetailView,
    DonationsListView,
    ExportDonationsCSVView,
    OrgDonationDetailView,
    OrganisationSettingsView
)

from .campaign_views import (
    CampaignListView,
    CampaignDetailView,
    CampaignCreateView,
    CampaignEditView,
    CampaignCloseView,
    CampaignReactivateView,
    CampaignDeleteView
)

from .donation_views import (
    CreateDonationView,
    DonationDetailView
)

# Import admin views
from .admin_views import (
    AdminDashboardView,
    AdminOrganisationsListView,
    AdminDonorsListView,
    AdminActiveCampaignsListView,
    AdminCampaignQueueListView,
    AdminCampaignReviewView,
    AdminOrganisationDeleteView,
    org_owner_test_view
)

# Public/shared URLs
public_patterns = [
    # Public campaign browsing
    path('campaigns/', CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/<int:pk>/', CampaignDetailView.as_view(), name='campaign_detail'),
    
    # Public organization browsing - Now handled by organizations app
    # path('organisations/', OrganisationListView.as_view(), name='organisation_list'),
    
    # Public donation view
    path('donations/<int:pk>/', DonationDetailView.as_view(), name='donation_detail'),
    
    # Test URL for role_required decorator
    path('test/org-owner-only/', org_owner_test_view, name='test_org_owner_view'),
]

# Donor URLs
donor_patterns = [
    # Donor dashboard
    path('dashboard/', DonorDashboardView.as_view(), name='dashboard'),
    
    # Donor campaigns browsing
    path('campaigns/', DonorCampaignsView.as_view(), name='campaigns'),
    path('campaigns/<int:pk>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/<int:pk>/donate/', CreateDonationView.as_view(), name='donate'),
    
    # Donor organizations browsing
    path('organizations/', DonorOrganizationsView.as_view(), name='organizations'),
    
    # Donor donation detail
    path('donations/<str:reference_number>/', DonorDonationDetailView.as_view(), name='donation_detail'),
    
    # Donor profile
    path('profile/', DonorProfileView.as_view(), name='profile'),
]

# Organization URLs
org_patterns = [
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

# Admin URLs
admin_patterns = [
    # Admin dashboard
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Admin organization management
    path('organisations/', AdminOrganisationsListView.as_view(), name='admin_organisations'),
    path('organisations/<int:pk>/delete/', AdminOrganisationDeleteView.as_view(), name='admin_delete_organisation'),
    
    # Admin donor management
    path('donors/', AdminDonorsListView.as_view(), name='admin_donors'),
    
    # Admin campaign management
    path('campaigns/active/', AdminActiveCampaignsListView.as_view(), name='admin_active_campaigns'),
    path('campaigns/queue/', AdminCampaignQueueListView.as_view(), name='admin_campaign_queue'),
    path('campaigns/<int:pk>/review/', AdminCampaignReviewView.as_view(), name='admin_campaign_review'),
]

# Configure URL namespaces
app_name = 'funding'
urlpatterns = [
    path('', include((public_patterns, 'funding'))),
    path('donor/', include((donor_patterns, 'donor'))),
    path('org/', include((org_patterns, 'org'))),
    path('admin/', include((admin_patterns, 'core_admin'))),
]
