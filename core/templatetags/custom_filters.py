from django import template
from django.utils.safestring import SafeString
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Add a CSS class to the 'class' attribute of an HTML element.
    
    Usage:
        {{ form.field|add_class:"form-control" }}  # For form fields
        {{ field|safe|add_class:"some-class" }}   # For raw HTML/SafeString
    """
    # Check if this is a form field
    if isinstance(value, BoundField):
        css_classes = value.field.widget.attrs.get('class', '')
        
        if css_classes:
            # If there are already classes, add the new one
            if arg not in css_classes:
                return value.as_widget(attrs={'class': f"{css_classes} {arg}"})
        else:
            # If there are no classes yet, set this one
            return value.as_widget(attrs={'class': arg})
    
    # If it's a SafeString or raw HTML string, handle differently
    elif isinstance(value, (str, SafeString)):
        # For SafeString/raw HTML, we'll just return the string as is
        # The template should handle this case manually with inline classes
        return value
    
    # For any other type or if the class is already present, return unchanged
    return value
