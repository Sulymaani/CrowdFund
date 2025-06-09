from django.shortcuts import render
from django.http import HttpResponse
from .decorators import role_required
from .models import CustomUser # Ensure CustomUser is imported to access roles if needed directly, though decorator handles strings

# Create your views here.

@role_required('admin')
def admin_test_view(request):
    return HttpResponse("Admin access granted.")

@role_required('org_owner')
def org_owner_test_view(request):
    return HttpResponse("Org owner access granted.")

@role_required('donor')
def donor_test_view(request):
    return HttpResponse("Donor access granted.")

@role_required(['admin', 'org_owner'])
def admin_or_org_owner_test_view(request):
    return HttpResponse("Admin or Org Owner access granted.")
