"""
Comprehensive formatting helpers for use in templates across the CrowdFund application.
Provides consistent formatting for currency, dates, percentages, and calculations.
"""
from datetime import datetime
from django import template
from django.db.models.query import QuerySet
from django.utils.formats import number_format
from django.utils.timezone import now
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter(name='currency')
def currency(value, decimal_places=2):
    """
    Format a value as currency with $ symbol and thousands separators.
    
    Args:
        value: The value to format (can be int, float, Decimal, or None)
        decimal_places: Number of decimal places to display
        
    Usage:
        {{ 1234.56|currency }}  --> $1,234.56
        {{ 1234|currency:0 }}   --> $1,234
        {{ None|currency }}     --> $0.00
    """
    try:
        if value is None:
            value = 0
        return f"${number_format(float(value), decimal_places, use_l10n=True)}"
    except (ValueError, TypeError):
        return f"${number_format(0, decimal_places, use_l10n=True)}"


@register.filter(name='percentage')
def percentage(value, decimal_places=0):
    """
    Format a value as a percentage.
    
    Args:
        value: The decimal value (between 0 and 1) to format as percentage
        decimal_places: Number of decimal places to display
        
    Usage:
        {{ 0.1234|percentage }}  --> 12%
        {{ 0.1234|percentage:2 }} --> 12.34%
        {{ None|percentage }}    --> 0%
    """
    try:
        if value is None:
            value = 0
        return f"{number_format(float(value) * 100, decimal_places, use_l10n=True)}%"
    except (ValueError, TypeError):
        return f"{number_format(0, decimal_places, use_l10n=True)}%"


@register.filter(name='sum_amount')
def sum_amount(queryset):
    """
    Calculate the sum of 'amount' field in a queryset.
    Enhanced version of the original sum_amount filter with robust error handling.
    
    Args:
        queryset: A Django queryset or list of objects with 'amount' attribute
        
    Usage:
        {{ donations|sum_amount }} --> Total amount
        {{ None|sum_amount }}    --> 0
    """
    try:
        # Handle None input
        if queryset is None:
            return 0
            
        # Handle QuerySet
        if isinstance(queryset, QuerySet):
            return queryset.aggregate(total=models.Sum('amount'))['total'] or 0
            
        # Handle list or iterable
        return sum(getattr(obj, 'amount', 0) or 0 for obj in queryset)
    except Exception:
        # Safely handle any other errors
        return 0


@register.filter(name='smartdate')
def smartdate(value):
    """
    Display date in a user-friendly format:
    - Today → "Today, 3:45 PM"
    - Yesterday → "Yesterday, 3:45 PM" 
    - Within 7 days → "Tuesday, 3:45 PM"
    - This year → "Jan 15, 3:45 PM" 
    - Older → "Jan 15, 2024, 3:45 PM"
    
    Args:
        value: A datetime object
        
    Usage:
        {{ some_date|smartdate }}
    """
    if value is None:
        return "Never"
        
    try:
        # Convert to datetime if only date is provided
        if not hasattr(value, 'hour'):
            value = datetime.combine(value, datetime.min.time())
            
        current = now().replace(microsecond=0)
        date_obj = value.replace(microsecond=0)
        
        # Today
        if date_obj.date() == current.date():
            return f"Today, {date_obj.strftime('%-I:%M %p')}"
            
        # Yesterday    
        yesterday = (current.date() - timedelta(days=1))
        if date_obj.date() == yesterday:
            return f"Yesterday, {date_obj.strftime('%-I:%M %p')}"
            
        # Within last 7 days
        if (current.date() - date_obj.date()).days < 7:
            return f"{date_obj.strftime('%A')}, {date_obj.strftime('%-I:%M %p')}"
            
        # This year
        if date_obj.year == current.year:
            return date_obj.strftime("%b %-d, %-I:%M %p")
            
        # Older dates
        return date_obj.strftime("%b %-d, %Y, %-I:%M %p")
    except Exception:
        return str(value)


@register.filter(name='calculate_progress')
def calculate_progress(current, goal):
    """
    Calculate progress percentage with safety bounds between 0-100%.
    
    Args:
        current: Current value (amount raised)
        goal: Target value (funding goal)
        
    Usage:
        {{ campaign.total_raised|calculate_progress:campaign.funding_goal }}
    """
    try:
        if current is None or goal is None or float(goal) == 0:
            return 0
            
        percentage = (float(current) / float(goal)) * 100
        # Constrain between 0 and 100
        return max(0, min(100, percentage))
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter(name='remaining_days')
def remaining_days(end_date):
    """
    Calculate days remaining until a date with friendly formatting:
    - If expired: "Expired"
    - If ending today: "Ends today" 
    - If 1 day: "1 day left"
    - If multiple days: "X days left"
    
    Args:
        end_date: A date or datetime object
        
    Usage:
        {{ campaign.end_date|remaining_days }}
    """
    if end_date is None:
        return ""
        
    try:
        # Handle both date and datetime objects
        end = end_date.date() if hasattr(end_date, 'date') else end_date
        today = now().date()
        
        days_left = (end - today).days
        
        if days_left < 0:
            return "Expired"
        elif days_left == 0:
            return "Ends today"
        elif days_left == 1:
            return "1 day left"
        else:
            return f"{days_left} days left"
    except Exception:
        return ""


@register.simple_tag
def format_money_range(min_value, max_value):
    """
    Format a money range with appropriate formatting.
    
    Args:
        min_value: The minimum value of the range
        max_value: The maximum value of the range
        
    Usage:
        {% format_money_range 100 1000 %}  --> $100 - $1,000
        {% format_money_range 1000 None %} --> $1,000+
    """
    try:
        if min_value is None and max_value is None:
            return "Any amount"
            
        if min_value is None:
            return f"Up to {currency(max_value)}"
            
        if max_value is None:
            return f"{currency(min_value)}+"
            
        return f"{currency(min_value)} - {currency(max_value)}"
    except Exception:
        return ""


# Fix import needed for sum_amount
from django.db import models
