"""
Base forms and form utilities for consistent form behavior across the application.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm

class BaseModelForm(forms.ModelForm):
    """
    Base model form with standardized error handling and styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    def _apply_common_styles(self):
        """Apply consistent styling to form fields."""
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css_classes} form-control block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm".strip()


class BaseUserForm(UserCreationForm):
    """
    Base form for all user-related forms with consistent styling and error handling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()
        
        # Apply consistent styling to password fields
        if 'password1' in self.fields:
            self.fields['password1'].help_text = "Your password must be at least 8 characters and cannot be entirely numeric."
        
        if 'password2' in self.fields:
            self.fields['password2'].help_text = "Enter the same password as before, for verification."

    def _apply_common_styles(self):
        """Apply consistent styling to form fields."""
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{css_classes} form-control block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm".strip()
