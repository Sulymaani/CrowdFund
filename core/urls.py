from django.urls import path
from . import views

from funding.admin_views import (
    AdminActiveCampaignsListView, AdminCampaignQueueListView, AdminCampaignReviewView,
    AdminDashboardView, AdminDonorsListView, AdminOrganisationsListView,
    AdminToggleOrganisationActiveView, ImpersonateOrgOwnerView, StopImpersonationView,
    AdminMetricsSummaryView, AdminOrganisationDeleteView
)

app_name = 'core_admin'

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('campaign-queue/', AdminCampaignQueueListView.as_view(), name='admin_campaign_queue'),
    path('campaign-review/<int:pk>/', AdminCampaignReviewView.as_view(), name='admin_campaign_review'),
    path('campaigns/active/', AdminActiveCampaignsListView.as_view(), name='admin_active_campaigns'),
    path('organisations/', AdminOrganisationsListView.as_view(), name='admin_organisations'),
    path('organisations/<int:pk>/toggle-active/', AdminToggleOrganisationActiveView.as_view(), name='admin_org_toggle_active'),
    path('donors/', AdminDonorsListView.as_view(), name='admin_donors'),
    path('impersonate/start/<int:user_id>/', ImpersonateOrgOwnerView.as_view(), name='impersonate_start'),
    path('impersonate/stop/', StopImpersonationView.as_view(), name='impersonate_stop'),
    path('organisations/<int:pk>/delete/', AdminOrganisationDeleteView.as_view(), name='admin_org_delete'),
    path('metrics/summary/', AdminMetricsSummaryView.as_view(), name='admin_metrics_summary'),
]
