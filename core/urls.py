from django.urls import path
from . import views



from funding.admin_views import (
    AdminDashboardView,
    AdminCampaignQueueListView,
    AdminCampaignReviewView
)

from funding.admin_views import (
    AdminDashboardView,
    AdminCampaignQueueListView,
    AdminCampaignReviewView
)

urlpatterns = [
<<<<<<< HEAD
    path('dashboard/', AdminDashboardView.as_view(), name='dashboard'),
=======
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
    path('campaign-queue/', AdminCampaignQueueListView.as_view(), name='admin_campaign_queue'),
    path('campaign-review/<int:pk>/', AdminCampaignReviewView.as_view(), name='admin_campaign_review'),
]
