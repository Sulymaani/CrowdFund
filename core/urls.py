from django.urls import path
from . import views

app_name = 'core'

from funding.admin_views import (
    AdminDashboardView,
    AdminCampaignQueueListView,
    AdminCampaignReviewView
)

urlpatterns = [
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('campaign-queue/', AdminCampaignQueueListView.as_view(), name='admin_campaign_queue'),
    path('campaign-review/<int:pk>/', AdminCampaignReviewView.as_view(), name='admin_campaign_review'),
]
