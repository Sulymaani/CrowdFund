"""
Core view mixins for CrowdFund application.
These mixins provide reusable functionality for views across the application.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class MessageMixin:
    """
    Mixin to add standardized messaging functionality to views.
    """
    success_message = None
    error_message = None
    info_message = None
    warning_message = None
    
    def get_success_message(self):
        """Get success message text."""
        return self.success_message
        
    def get_error_message(self):
        """Get error message text."""
        return self.error_message
        
    def get_info_message(self):
        """Get info message text."""
        return self.info_message
        
    def get_warning_message(self):
        """Get warning message text."""
        return self.warning_message
    
    def add_message(self, level, message_text):
        """Add a message if text is provided."""
        if message_text:
            messages.add_message(self.request, level, message_text)
    
    def form_valid(self, form):
        """Add success message when form is valid."""
        result = super().form_valid(form)
        self.add_message(messages.SUCCESS, self.get_success_message())
        return result
    
    def form_invalid(self, form):
        """Add error message when form is invalid."""
        result = super().form_invalid(form)
        self.add_message(messages.ERROR, self.get_error_message())
        return result


class RoleMixin(UserPassesTestMixin):
    """
    Mixin to enforce role-based access control.
    Verifies that the user has the required role.
    """
    role_required = None  # 'donor', 'organization_admin', etc.
    unauthorized_url = reverse_lazy('home')
    
    def test_func(self):
        """Test if the user has the required role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return False
            
        if self.role_required == 'donor':
            return user.is_donor
            
        elif self.role_required == 'organization_admin':
            return hasattr(user, 'organization') and user.organization is not None
            
        elif self.role_required == 'admin':
            return user.is_staff or user.is_superuser
            
        # Default: no role requirement
        return True
    
    def handle_no_permission(self):
        """Handle unauthorized access."""
        if self.request.user.is_authenticated:
            # User is logged in but doesn't have the right role
            messages.error(
                self.request,
                _("You don't have permission to access this page. This area requires {role} access.").format(
                    role=self.role_required
                )
            )
            return redirect(self.unauthorized_url)
        else:
            # User is not logged in
            return super().handle_no_permission()


class OwnershipMixin:
    """
    Mixin to enforce object ownership.
    Only allows access if the user is the owner of the object.
    """
    owner_field = 'user'  # Default field name for the owner relationship
    
    def get_queryset(self):
        """Filter queryset to only include objects owned by the user."""
        queryset = super().get_queryset()
        return queryset.filter(**{self.owner_field: self.request.user})


class OrganizationMemberMixin:
    """
    Mixin to enforce organization membership.
    Only allows access if the user is a member of the relevant organization.
    """
    def dispatch(self, request, *args, **kwargs):
        """Check if user is a member of the organization."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
            
        # Get the organization from the view or object
        organization = self.get_organization()
        
        # Check if user is a member
        if not self.is_organization_member(request.user, organization):
            messages.error(
                request,
                _("You don't have permission to access this resource.")
            )
            return redirect('organizations:list')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_organization(self):
        """
        Get the organization to check membership against.
        Override this method in the view.
        """
        # Default implementation tries to get organization from the object
        obj = self.get_object()
        return getattr(obj, 'organization', None)
    
    def is_organization_member(self, user, organization):
        """Check if the user is a member of the organization."""
        if not organization:
            return False
            
        # Check direct membership
        if hasattr(organization, 'users') and user in organization.users.all():
            return True
            
        # Check if user is the organization admin
        if hasattr(user, 'organization') and user.organization == organization:
            return True
            
        # Allow staff/admin users
        if user.is_staff or user.is_superuser:
            return True
            
        return False


class AjaxFormMixin:
    """
    Mixin to handle AJAX form submissions.
    """
    def form_valid(self, form):
        """Return JSON response for AJAX or normal redirect otherwise."""
        response = super().form_valid(form)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            data = {
                'success': True,
                'message': self.get_success_message() if hasattr(self, 'get_success_message') else None,
                'redirect_url': self.get_success_url(),
            }
            return JsonResponse(data)
            
        return response
    
    def form_invalid(self, form):
        """Return JSON with errors for AJAX or normal form errors otherwise."""
        response = super().form_invalid(form)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            
            # Format form errors for JSON response
            errors = {}
            for field, field_errors in form.errors.items():
                if field == '__all__':
                    errors['non_field_errors'] = [str(e) for e in field_errors]
                else:
                    errors[field] = [str(e) for e in field_errors]
                    
            data = {
                'success': False,
                'errors': errors,
                'message': self.get_error_message() if hasattr(self, 'get_error_message') else None,
            }
            return JsonResponse(data, status=400)
            
        return response


class LoggedInRedirectMixin:
    """
    Mixin to redirect logged-in users away from login/register pages.
    """
    redirect_authenticated_user = True
    redirect_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard."""
        if self.redirect_authenticated_user and request.user.is_authenticated:
            redirect_url = self.get_redirect_url()
            if redirect_url:
                return redirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_redirect_url(self):
        """Get the URL to redirect authenticated users to."""
        return self.redirect_url


class RoleBasedRedirectMixin:
    """
    Mixin to redirect users to different pages based on their role.
    """
    donor_redirect_url = reverse_lazy('donor:dashboard')
    organization_redirect_url = reverse_lazy('organizations:dashboard')
    admin_redirect_url = reverse_lazy('admin:index')
    default_redirect_url = reverse_lazy('home')
    
    def get_role_based_redirect_url(self):
        """Get the redirect URL based on the user's role."""
        user = self.request.user
        
        if not user.is_authenticated:
            return self.default_redirect_url
            
        if user.is_staff or user.is_superuser:
            return self.admin_redirect_url
            
        if hasattr(user, 'is_donor') and user.is_donor:
            return self.donor_redirect_url
            
        if hasattr(user, 'organization') and user.organization is not None:
            return self.organization_redirect_url
            
        return self.default_redirect_url
        

class FormControlMixin:
    """
    Mixin to add form-control class to all form fields.
    """
    def get_form(self, form_class=None):
        """Add Bootstrap classes to form fields."""
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            if field.widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'CheckboxSelectMultiple']:
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
        return form
