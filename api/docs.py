from django.views.generic import TemplateView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# Simple API documentation view
class ApiDocsView(TemplateView):
    template_name = 'api/docs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CrowdFund API Documentation'
        return context

# API root view that lists available endpoints
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'campaigns': reverse('api:campaign-list', request=request, format=format),
        'organizations': reverse('api:organisation-list', request=request, format=format),
        'donations': reverse('api:donation-list', request=request, format=format),
        'tags': reverse('api:tag-list', request=request, format=format),
        'users': reverse('api:user-list', request=request, format=format),
        'auth': reverse('api:api-auth-root', request=request, format=format),
    })
    
# Create view instances
api_docs_view = ApiDocsView.as_view()
