from django.urls import path
from . import views

urlpatterns = [
    path('test/admin/', views.admin_test_view, name='admin_test_view'),
    path('test/org_owner/', views.org_owner_test_view, name='org_owner_test_view'),
    path('test/donor/', views.donor_test_view, name='donor_test_view'),
    path('test/admin_or_org_owner/', views.admin_or_org_owner_test_view, name='admin_or_org_owner_test_view'),
]
