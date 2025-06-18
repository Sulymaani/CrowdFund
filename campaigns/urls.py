from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Public campaign browsing
    path('', views.CampaignListView.as_view(), name='list'),
    path('<int:pk>/', views.CampaignDetailView.as_view(), name='detail'),
    
    # Organization owner campaign management
    path('org/', views.OrgCampaignListView.as_view(), name='org_list'),
    path('org/<int:pk>/', views.OrgCampaignDetailView.as_view(), name='org_detail'),
    path('new/', views.CampaignCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.CampaignEditView.as_view(), name='edit'),
    path('<int:pk>/close/', views.CampaignCloseView.as_view(), name='close'),
    path('<int:pk>/reactivate/', views.CampaignReactivateView.as_view(), name='reactivate'),
    path('<int:pk>/delete/', views.CampaignDeleteView.as_view(), name='delete'),
    
    # Admin campaign management
    path('admin/', views.AdminCampaignListView.as_view(), name='admin_list'),
    path('admin/<int:pk>/review/', views.AdminCampaignReviewView.as_view(), name='admin_review'),
]
