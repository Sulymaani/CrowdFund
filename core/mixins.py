from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages # Added for messages in new mixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy # Added for reverse_lazy

class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is a staff member.
    """
    def test_func(self):
        print(f"\nDEBUG StaffRequiredMixin.test_func:")
        print(f"  self.request: {self.request}")
        print(f"  self.request.user: {self.request.user}, type: {type(self.request.user)}")
        is_auth = False
        is_staff = False
        if hasattr(self.request.user, 'is_authenticated'):
            # For SimpleLazyObject, accessing is_authenticated will resolve it.
            # If it's already a concrete user, it just accesses the attribute.
            is_auth = self.request.user.is_authenticated
            print(f"  self.request.user.is_authenticated (resolved): {is_auth}")
        else:
            print(f"  self.request.user has no is_authenticated attribute")
        
        if hasattr(self.request.user, 'is_staff'):
            # Similar for is_staff
            is_staff = self.request.user.is_staff
            print(f"  self.request.user.is_staff (resolved): {is_staff}")
        else:
            print(f"  self.request.user has no is_staff attribute")
            
        result = is_auth and is_staff
        print(f"  StaffRequiredMixin.test_func result: {result}")
        return result

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login') # Or your login URL
        raise PermissionDenied("You do not have permission to access this page.")

class OrganisationOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is an authenticated organisation owner.
    Organisation does not need to be verified.
    """
    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated and
            user.role == 'org_owner' and
            user.organisation is not None
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        raise PermissionDenied("You must be an organisation owner to perform this action.")


class PublicOrNonOrgOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to allow access to anonymous users or authenticated users who are not
    already an organisation owner with an existing organisation.
    Used for the Organisation Application form.
    """
    login_url = reverse_lazy('login') # Default login URL
    permission_denied_message = "You are already associated with an organisation or have an application pending."
    redirect_url_on_permission_denied = 'funding:campaign_list'

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return True  # Allow anonymous users
        
        # Allow authenticated users if they are not an org_owner or don't have an org yet
        # This covers donors, general users, or org_owners whose previous org was deleted/unlinked
        if user.role != 'org_owner' or not user.organisation:
            return True
        
        # Deny if user is an org_owner AND already has an organisation
        return False

    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated:
            # This case should ideally not be hit if test_func allows anonymous,
            # but as a fallback, redirect to login.
            return redirect(self.login_url)
        
        # For authenticated users who fail the test_func (i.e., existing org owners with an org)
        messages.info(self.request, self.permission_denied_message)
        return redirect(self.redirect_url_on_permission_denied)


class DonorRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is an authenticated donor.
    """
    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated and
            hasattr(user, 'role') and
            user.role == 'donor'
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        
        # For authenticated non-donors, raise a 403 Forbidden error.
        raise PermissionDenied("Only donors are allowed to make donations.")
