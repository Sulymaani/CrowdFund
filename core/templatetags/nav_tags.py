from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, url_name):
    request = context['request']
    try:
        # Check if the current path matches the reversed URL
        if request.path == reverse(url_name):
            return 'bg-blue-700'
    except NoReverseMatch:
        # Handle cases where the URL name might not exist in all contexts
        pass
    return ''
