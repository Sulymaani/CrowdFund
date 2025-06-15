from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.contrib import messages
from .forms import DonorRegistrationForm, OrgRegistrationForm
from .models import CustomUser  # Assuming CustomUser model is defined in .models

def get_user_dashboard_url(user):
    """Determinesthe redirect URL based on the user's role."""
    if user.is_staff:
        return reverse_lazy('core_admin:dashboard')
    elif hasattr(user, 'role'):
        if user.role == 'org_owner':
            return reverse_lazy('org:dashboard')
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
    """Logout view that safely ends impersonation if active, otherwise normal logout."""

    def dispatch(self, request, *args, **kwargs):
        impersonator_id = request.session.pop('impersonator_id', None)
        if impersonator_id:
            try:
                admin_user = CustomUser.objects.get(id=impersonator_id)
                login(request, admin_user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, "Stopped impersonating and restored your admin session.")
                return redirect('core_admin:admin_organisations')
            except CustomUser.DoesNotExist:
                # fallback: do full logout
                logout(request)
                messages.error(request, "Original admin account not found. Logged out completely.")
                return redirect('home')
        # normal path
        return super().dispatch(request, *args, **kwargs)

    def get_next_page(self):
        if 'next' in self.request.session:
            del self.request.session['next']
        return reverse_lazy('accounts:login')


def placeholder_view(request):
    """
    A placeholder view for dashboards and other pages that are not yet implemented.
    """
    return render(request, 'placeholder.html', {'page_title': 'Placeholder Page'})
