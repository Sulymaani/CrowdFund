from django.urls import path

app_name = 'funding'
from .views import CampaignListView, CampaignDetailView, CreateDonationView, OrganisationApplicationCreateView, CampaignCreateView # Removed OrganisationCreateView, added OrganisationApplicationCreateView
from .admin_views import PendingOrgListView, OrgReviewView, org_owner_test_view, AdminCampaignQueueListView, AdminCampaignReviewView
from accounts.views import placeholder_view

urlpatterns = [
    # Dashboard placeholders for testing redirects
    path('dashboard/admin/', placeholder_view, name='admin_dashboard'),
    path('dashboard/org/', placeholder_view, name='org_dashboard'),
    path('org/status/', placeholder_view, name='org_status'),
    path('dashboard/donor/', placeholder_view, name='donor_dashboard'),

    path('', CampaignListView.as_view(), name='campaign_list'),
    path('campaign/<int:pk>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaign/<int:pk>/donate/', CreateDonationView.as_view(), name='campaign_donate'),
    path('org/apply/', OrganisationApplicationCreateView.as_view(), name='organisation_apply'), # Changed to OrganisationApplicationCreateView
    path('campaign/new/', CampaignCreateView.as_view(), name='campaign_new'),
    # Admin URLs for organisation review
    path('admin/org-queue/', PendingOrgListView.as_view(), name='admin_org_queue'),
    path('admin/org-review/<int:pk>/', OrgReviewView.as_view(), name='admin_org_review'),
    path('admin/campaign-queue/', AdminCampaignQueueListView.as_view(), name='admin_campaign_queue'),
    path('admin/campaign-review/<int:pk>/', AdminCampaignReviewView.as_view(), name='admin_campaign_review'),
    # Test URL for role_required decorator
    path('test/org-owner-only/', org_owner_test_view, name='test_org_owner_view'),
]
