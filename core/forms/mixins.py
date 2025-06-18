"""
Form mixins for consistent validation patterns and error handling across the application.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class FormControlMixin:
    """
    Mixin to automatically add form-control class to all form fields.
    Used to ensure Bootstrap styling is applied consistently.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect', 'CheckboxSelectMultiple']:
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class EnhancedErrorHandlingMixin:
    """
    Mixin to provide enhanced error handling and validation for forms.
    """
    error_css_class = 'is-invalid'
    required_css_class = 'required'
    
    def add_form_error(self, message):
        """Add a form-level (non-field) error with standardized formatting."""
        if not hasattr(self, 'non_field_errors'):
            self._errors['__all__'] = self.error_class([message])
        else:
            self._errors['__all__'].append(message)
    
    def clean(self):
        """Enhanced clean method with additional error handling."""
        cleaned_data = super().clean()
        try:
            return self.enhanced_validation(cleaned_data)
        except ValidationError as e:
            self.add_form_error(str(e))
        return cleaned_data
    
    def enhanced_validation(self, cleaned_data):
        """
        Override this method in subclasses to provide additional validation.
        This method should return the cleaned_data or raise ValidationError.
        """
        return cleaned_data


class PasswordStrengthMixin:
    """
    Mixin to enforce password strength requirements.
    """
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    def clean_password1(self):
        """
        Validate that the password meets strength requirements.
        """
        password = self.cleaned_data.get('password1')
        if not password:
            return password
            
        errors = []
        
        if len(password) < self.MIN_LENGTH:
            errors.append(_("Password must be at least {} characters long.").format(self.MIN_LENGTH))
            
        if self.REQUIRE_UPPERCASE and not any(char.isupper() for char in password):
            errors.append(_("Password must contain at least one uppercase letter."))
            
        if self.REQUIRE_LOWERCASE and not any(char.islower() for char in password):
            errors.append(_("Password must contain at least one lowercase letter."))
            
        if self.REQUIRE_DIGIT and not any(char.isdigit() for char in password):
            errors.append(_("Password must contain at least one digit."))
            
        if self.REQUIRE_SPECIAL and not any(not char.isalnum() for char in password):
            errors.append(_("Password must contain at least one special character."))
            
        if errors:
            raise ValidationError(errors)
            
        return password


class DateValidationMixin:
    """
    Mixin to provide date validation methods for forms with date fields.
    """
    def validate_date_order(self, start_date_field, end_date_field, message=None):
        """
        Validate that start_date comes before end_date.
        """
        start_date = self.cleaned_data.get(start_date_field)
        end_date = self.cleaned_data.get(end_date_field)
        
        if start_date and end_date and start_date > end_date:
            if not message:
                message = _(f"{start_date_field} must be before {end_date_field}")
            self._errors[start_date_field] = self.error_class([message])
            self._errors[end_date_field] = self.error_class([message])
            
            # Remove invalid data
            if start_date_field in self.cleaned_data:
                del self.cleaned_data[start_date_field]
            if end_date_field in self.cleaned_data:
                del self.cleaned_data[end_date_field]
                
        return self.cleaned_data
        

class MoneyValidationMixin:
    """
    Mixin to provide money amount validation methods.
    """
    def validate_positive_amount(self, field_name, message=None):
        """
        Validate that a money amount is positive.
        """
        amount = self.cleaned_data.get(field_name)
        
        if amount and amount <= 0:
            if not message:
                message = _(f"{field_name.title()} must be greater than zero")
            self._errors[field_name] = self.error_class([message])
            
            # Remove invalid data
            if field_name in self.cleaned_data:
                del self.cleaned_data[field_name]
                
        return self.cleaned_data
        
    def validate_min_amount(self, field_name, min_value, message=None):
        """
        Validate that a money amount is at least min_value.
        """
        amount = self.cleaned_data.get(field_name)
        
        if amount and amount < min_value:
            if not message:
                message = _(f"{field_name.title()} must be at least {min_value}")
            self._errors[field_name] = self.error_class([message])
            
            # Remove invalid data
            if field_name in self.cleaned_data:
                del self.cleaned_data[field_name]
                
        return self.cleaned_data


class BaseModelForm(FormControlMixin, EnhancedErrorHandlingMixin, forms.ModelForm):
    """
    Base model form with enhanced validation and Bootstrap styling.
    All model forms should inherit from this class.
    """
    pass


class BaseForm(FormControlMixin, EnhancedErrorHandlingMixin, forms.Form):
    """
    Base form with enhanced validation and Bootstrap styling.
    All non-model forms should inherit from this class.
    """
    pass
