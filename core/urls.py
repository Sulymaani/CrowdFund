from django.urls import path
from . import views

from funding.admin_views import (
    AdminDashboardView,
    AdminCampaignQueueListView,
    AdminCampaignReviewView
)

app_name = 'core_admin'

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
    path('campaign-queue/', AdminCampaignQueueListView.as_view(), name='admin_campaign_queue'),
    path('campaign-review/<int:pk>/', AdminCampaignReviewView.as_view(), name='admin_campaign_review'),
]
