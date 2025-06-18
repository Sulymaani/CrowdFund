from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Public and donor routes
    path('create/<int:campaign_id>/', views.DonationCreateView.as_view(), name='create'),
    path('<slug:reference_number>/', views.DonationDetailView.as_view(), name='detail'),
    path('receipt/<int:pk>/', views.DonationReceiptView.as_view(), name='receipt'),
    
    # Donor-specific routes
    path('donor/history/', views.DonorDonationsListView.as_view(), name='donor_history'),
    
    # Organization owner routes
    path('org/list/', views.OrgDonationsListView.as_view(), name='org_list'),
    path('org/<slug:reference_number>/', views.OrgDonationDetailView.as_view(), name='org_detail'),
]
