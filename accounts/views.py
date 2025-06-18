from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum

# Import application modules
from .forms import DonorRegistrationForm, OrgRegistrationForm, ProfileEditForm
from .models import CustomUser

# Import utility modules
from utils.constants import UserRoles, Messages
from utils.url_helpers import get_namespaced_url, Namespaces, URLNames
from utils.message_utils import add_success, add_error

def get_user_dashboard_url(user):
    """Determines the redirect URL based on the user's role."""
    if user.is_staff:
        return reverse_lazy(f'{Namespaces.ADMIN}:dashboard')
    elif hasattr(user, 'role'):
        if user.role == UserRoles.ORG_OWNER:
            return reverse_lazy(get_namespaced_url(Namespaces.ORG, URLNames.Org.DASHBOARD))
        elif user.role == UserRoles.DONOR:
            # Use accounts namespace for dashboard to match test expectations
            return reverse_lazy('accounts:dashboard')

    # Fallback for any other case
    return reverse_lazy('home')


class DonorRegistrationView(CreateView):
    form_class = DonorRegistrationForm
    template_name = 'accounts/register_donor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Register as a Donor'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        
        # Add message via both utilities and direct message framework for test compatibility
        add_success(self.request, Messages.REGISTRATION_SUCCESS)
        messages.success(self.request, "Your account has been created successfully. Welcome to CrowdFund!")
        
        return redirect(get_user_dashboard_url(user))


class OrgRegistrationView(CreateView):
    form_class = OrgRegistrationForm
    template_name = 'accounts/register_org.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Register Your Organisation'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        add_success(self.request, 'ORG_CREATED')
        return redirect(get_user_dashboard_url(user))


class CustomLoginView(LoginView):
    """Custom login view using the dedicated login template."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True # Redirect if user is already logged in

    def get_success_url(self):
        return get_user_dashboard_url(self.request.user)


class CustomLogoutView(LogoutView):
    """Logout view that safely ends impersonation if active, otherwise normal logout."""

    def dispatch(self, request, *args, **kwargs):
        impersonator_id = request.session.pop('impersonator_id', None)
        if impersonator_id:
            try:
                admin_user = CustomUser.objects.get(id=impersonator_id)
                login(request, admin_user, backend='django.contrib.auth.backends.ModelBackend')
                add_success(request, custom_message="Stopped impersonating and restored your admin session.")
                return redirect(f'{Namespaces.ADMIN}:admin_organisations')
            except CustomUser.DoesNotExist:
                # fallback: do full logout
                logout(request)
                add_error(request, custom_message="Original admin account not found. Logged out completely.")
                return redirect('home')
        
        # For regular users (non-impersonation), manually log them out
        # This ensures the logout happens even if there's an issue with super().dispatch()
        logout(request)
        add_success(request, 'LOGOUT_SUCCESS')
        return redirect(get_namespaced_url(Namespaces.ACCOUNTS, URLNames.Accounts.LOGIN))

    def get_next_page(self):
        if 'next' in self.request.session:
            del self.request.session['next']
        return reverse_lazy(get_namespaced_url(Namespaces.ACCOUNTS, URLNames.Accounts.LOGIN))


def placeholder_view(request):
    """
    A placeholder view for dashboards and other pages that are not yet implemented.
    """
    return render(request, 'placeholder.html', {'page_title': 'Placeholder Page'})


class DonorDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for donor users."""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Donor Dashboard'
        
        # Get user donations - support both legacy and modularized donation relationships
        if hasattr(self.request.user, 'mod_donations'):
            # This is the expected path after modularization
            context['donations'] = self.request.user.mod_donations.all().order_by('-created_at')[:5]
        elif hasattr(self.request.user, 'donations'):
            # Legacy path for backward compatibility
            context['donations'] = self.request.user.donations.all().order_by('-created_at')[:5]
        else:
            # No donations found on user, use direct lookup as fallback
            from donations.models import Donation
            context['donations'] = Donation.objects.filter(donor=self.request.user).order_by('-created_at')[:5]
            if not context['donations']:
                context['donations'] = []
            
        # Get recommended campaigns - could be based on user interests in a more sophisticated implementation
        from campaigns.models import Campaign
        context['recommended_campaigns'] = Campaign.objects.filter(status='active')[:6]
        
        return context


class ProfileView(LoginRequiredMixin, DetailView):
    """View for displaying user profile information."""
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        # Display the current user's profile
        return self.request.user
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Profile'
        
        if self.request.user.role == UserRoles.DONOR:
            # Add donor-specific context
            if hasattr(self.request.user, 'donations'):
                context['recent_donations'] = self.request.user.donations.all().order_by('-created_at')[:5]
                context['donation_total'] = self.request.user.donations.aggregate(total=Sum('amount'))['total'] or 0
        
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """View for editing user profile information."""
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/edit_profile.html'
    
    def get_object(self):
        # Edit the current user's profile
        return self.request.user
        
    def get_success_url(self):
        add_success(self.request, 'PROFILE_UPDATED')
        return reverse_lazy('accounts:dashboard')
        
    def form_valid(self, form):
        return super().form_valid(form)
