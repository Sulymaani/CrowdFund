from django.urls import path
from . import views
from .views import AdminOrganisationQueueView, AdminOrganisationReviewView

app_name = 'core' # This is used for namespacing URLs, e.g., core:org_queue

urlpatterns = [
    path('org-queue/', AdminOrganisationQueueView.as_view(), name='admin_organisation_queue'),
    path('org-review/<int:pk>/', AdminOrganisationReviewView.as_view(), name='admin_organisation_review'),
    # URL patterns for the core app will be added here
]
