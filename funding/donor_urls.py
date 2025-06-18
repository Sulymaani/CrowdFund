from django.urls import path

app_name = 'donor_legacy'
from .views import (
    DonorDashboardView,
    DonorCampaignsView,
    DonorOrganizationsView,
    DonorDonationDetailView,
    DonorProfileView,
    CampaignDetailView,
    CreateDonationView,
)

urlpatterns = [
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
