from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView

from .forms import DonorRegistrationForm, OrgRegistrationForm


def get_user_dashboard_url(user):
    """Determines the redirect URL based on the user's role."""
    if user.is_staff:
        return reverse_lazy('core_admin:dashboard')
    elif hasattr(user, 'role'):
        if user.role == 'org_owner':
            return reverse_lazy('org_dashboard')
        elif user.role == 'donor':
            return reverse_lazy('donor_dashboard')

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
        return redirect(get_user_dashboard_url(user))


class CustomLoginView(LoginView):
    """Custom login view using the dedicated login template."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True # Redirect if user is already logged in

    def get_success_url(self):
        return get_user_dashboard_url(self.request.user)


class CustomLogoutView(LogoutView):
    """Custom logout view to ensure session cleanup and proper redirect."""
    def get_next_page(self):
        # Clear any stale 'next' parameter from the session
        if 'next' in self.request.session:
            del self.request.session['next']
        return reverse_lazy('home') # Always redirect to the marketing homepage


def placeholder_view(request):
    """
    A placeholder view for dashboards and other pages that are not yet implemented.
    """
    return render(request, 'placeholder.html', {'page_title': 'Placeholder Page'})
