"""
Utility functions for standardized message handling across the application.
"""
from django.contrib import messages
from utils.constants import Messages

def add_message(request, level, message_key=None, custom_message=None, **kwargs):
    """
    Standardized way to add messages across the application.
    
    Args:
        request: Django request object
        level: Message level (messages.SUCCESS, messages.ERROR, etc.)
        message_key: Key from Messages class constants
        custom_message: Custom message text (used if message_key is None)
        **kwargs: Format parameters for the message string
    
    Example:
        add_message(request, messages.SUCCESS, 'PROFILE_UPDATED')
        add_message(request, messages.ERROR, custom_message="Something went wrong")
        add_message(request, messages.INFO, 'WELCOME_USER', name=user.first_name)
    """
    if message_key and hasattr(Messages, message_key):
        message_text = getattr(Messages, message_key)
        if kwargs:
            message_text = message_text.format(**kwargs)
    elif custom_message:
        message_text = custom_message
        if kwargs:
            message_text = message_text.format(**kwargs)
    else:
        # Fallback message
        message_text = "Action completed."
    
    messages.add_message(request, level, message_text)


def add_success(request, message_key=None, custom_message=None, **kwargs):
    """Helper for success messages."""
    add_message(request, messages.SUCCESS, message_key, custom_message, **kwargs)


def add_error(request, message_key=None, custom_message=None, **kwargs):
    """Helper for error messages."""
    add_message(request, messages.ERROR, message_key, custom_message, **kwargs)


def add_info(request, message_key=None, custom_message=None, **kwargs):
    """Helper for info messages."""
    add_message(request, messages.INFO, message_key, custom_message, **kwargs)


def add_warning(request, message_key=None, custom_message=None, **kwargs):
    """Helper for warning messages."""
    add_message(request, messages.WARNING, message_key, custom_message, **kwargs)
