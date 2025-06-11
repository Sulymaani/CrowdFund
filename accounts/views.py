from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import CustomUser # Ensure CustomUser is imported to access roles if needed directly, though decorator handles strings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from .forms import DonorRegistrationForm

def get_user_dashboard_url(user):
    """Determines the redirect URL based on the user's role and status."""
    if user.is_staff:
        return reverse_lazy('funding:admin_dashboard')
    elif hasattr(user, 'role') and user.role == 'org_owner':
        if hasattr(user, 'organisation') and user.organisation and user.organisation.verified:
            return reverse_lazy('funding:org_dashboard')
        else:
            return reverse_lazy('funding:org_status')
    elif hasattr(user, 'role') and user.role == 'donor':
        return reverse_lazy('funding:donor_dashboard')

    return reverse_lazy('landing')

class DonorRegistrationView(CreateView):
    form_class = DonorRegistrationForm
    template_name = 'accounts/register_donor.html'
    success_url = reverse_lazy('landing')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Register as a Donor'
        return context

def landing_login_view(request):
    """Handles landing page, login, and redirects."""
    if request.user.is_authenticated:
        return redirect(get_user_dashboard_url(request.user))

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(get_user_dashboard_url(user))
        else:
            # Invalid login, re-render the page with errors
            return render(request, 'accounts/landing.html', {
                'form': form,
                'page_title': 'Welcome to CrowdFund'
            })
    else:
        # GET request, show a blank form
        form = AuthenticationForm()
        return render(request, 'accounts/landing.html', {
            'form': form,
            'page_title': 'Welcome to CrowdFund'
        })


# Dummy view for dashboard placeholders
def placeholder_view(request):
    """A temporary view for role-based dashboards until they are built."""
    user = request.user
    role = 'Guest'
    if user.is_authenticated:
        # Capitalize role for display, handle staff case
        role = getattr(user, 'role', 'admin' if user.is_staff else 'unknown')
        role = role.replace('_', ' ').title()

    logout_url = reverse('logout')
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Placeholder Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 2rem; line-height: 1.5; background-color: #f8f9fa; color: #343a40; }}
            h1 {{ color: #007bff; }}
            strong {{ color: #28a745; }}
            a {{ color: #dc3545; text-decoration: none; font-weight: bold; }}
            a:hover {{ text-decoration: underline; }}
            div {{ max-width: 600px; margin: auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <div>
            <h1>Placeholder Dashboard</h1>
            <p>Welcome, <strong>{user.username}</strong> (Role: {role}).</p>
            <p>This page is a placeholder. The full dashboard content will be built in a future iteration.</p>
            <hr style="margin: 1rem 0; border: 0; border-top: 1px solid #dee2e6;">
            <p><a href="{logout_url}">Log Out</a></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)



