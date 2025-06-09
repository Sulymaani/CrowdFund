from django.urls import path

app_name = 'funding'
from .views import CampaignListView, CampaignDetailView, OrganisationApplicationCreateView, CampaignCreateView # Removed OrganisationCreateView, added OrganisationApplicationCreateView
from .admin_views import PendingOrgListView, OrgReviewView, org_owner_test_view

urlpatterns = [
    path('', CampaignListView.as_view(), name='campaign_list'),
    path('campaign/<int:pk>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('org/apply/', OrganisationApplicationCreateView.as_view(), name='organisation_apply'), # Changed to OrganisationApplicationCreateView
    path('campaign/create/', CampaignCreateView.as_view(), name='campaign_create'),
    # Admin URLs for organisation review
    path('admin/org-queue/', PendingOrgListView.as_view(), name='admin_org_queue'),
    path('admin/org-review/<int:pk>/', OrgReviewView.as_view(), name='admin_org_review'),
    # Test URL for role_required decorator
    path('test/org-owner-only/', org_owner_test_view, name='test_org_owner_view'),
]
