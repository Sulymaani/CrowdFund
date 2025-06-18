"""
URL configuration for Campaign API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)

# URL patterns for the API
urlpatterns = [
    path('', include(router.urls)),
]
