from django import template

register = template.Library()

@register.filter
def sum_amount(donations):
    """
    Calculate the sum of donation amounts from a queryset of donations.
    
    Usage:
    {{ donations|sum_amount }}
    """
    return sum(donation.amount for donation in donations)
