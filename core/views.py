from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Serves the main marketing landing page."""
    template_name = 'home.html'
