from django.urls import path, include
from rest_framework import routers
from . import views
from .docs import api_docs_view, api_root

# Create a router and register our viewsets with it
router = routers.DefaultRouter()
# Old campaign API endpoint - replaced by the modular campaigns app API
# router.register(r'campaigns', views.CampaignViewSet, basename='campaign')
router.register(r'organizations', views.OrganisationViewSet, basename='organisation')
router.register(r'donations', views.DonationViewSet, basename='donation')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'users', views.UserViewSet, basename='user')

# The API URLs are now determined automatically by the router
app_name = 'api'  # Set the app namespace

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='api-auth'), name='api-auth-root'),
    
    # API Documentation
    path('docs/', api_docs_view, name='api-docs'),
]
