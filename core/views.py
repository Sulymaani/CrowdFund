from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Serves the main marketing landing page."""
    template_name = 'home.html'


def custom_page_not_found_view(request, exception):
    return render(request, "admin/errors/404.html", status=404)


def custom_permission_denied_view(request, exception):
    return render(request, "admin/errors/403.html", status=403)

