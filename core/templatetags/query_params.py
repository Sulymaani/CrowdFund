from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    """
    Renders URL-encoded query parameters from the current request's GET parameters,
    allowing for updates and additions.
    """
    query_dict = context['request'].GET.copy()
    for key, value in kwargs.items():
        query_dict[key] = value
    return query_dict.urlencode()
