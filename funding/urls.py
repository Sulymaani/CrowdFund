from django.urls import path

app_name = 'funding'
from .views import (
    CampaignListView,
    CampaignDetailView,
    CreateDonationView,
    CampaignCreateView,
    OrganisationListView
)
from .admin_views import (
    org_owner_test_view
)

urlpatterns = [
<<<<<<< HEAD
=======
    path('organisations/', OrganisationListView.as_view(), name='organisation_list'),
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
    path('campaigns/', CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/<int:pk>/', CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/<int:pk>/donate/', CreateDonationView.as_view(), name='campaign_donate'),
    path('campaigns/new/', CampaignCreateView.as_view(), name='campaign_new'),

    # Test URL for role_required decorator
    path('test/org-owner-only/', org_owner_test_view, name='test_org_owner_view'),
]
