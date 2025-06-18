from django.urls import path, include
from .views_donor import (
    DonorDashboardView, 
    DonorProfileView,
    DonorProfileEditView,
    DonorCampaignListView,
    DonorOrganizationListView
)

app_name = 'donor'

urlpatterns = [
    path('dashboard/', DonorDashboardView.as_view(), name='dashboard'),
    
    # Campaign browsing for donors
    path('campaigns/', include([
        path('', DonorCampaignListView.as_view(), name='campaigns'),
    ])),
    
    # Organization browsing for donors
    path('organizations/', include([
        path('', DonorOrganizationListView.as_view(), name='organizations'),
    ])),
    
    # Donor profile management
    path('profile/', include([
        path('', DonorProfileView.as_view(), name='profile'),
        path('edit/', DonorProfileEditView.as_view(), name='edit_profile'),
    ])),
]
