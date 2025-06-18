from django import forms
from django.core.exceptions import ValidationError
from .models import Organisation


class OrganisationSettingsForm(forms.ModelForm):
    """
    Form for updating organization settings
    
    Handles validation for organization details including:
    - Name uniqueness and length
    - Website URL format
    - Logo and banner image validations
    """
    
    class Meta:
        model = Organisation
        fields = [
            'name', 
            'website', 
            'mission',
            'contact_phone', 
            'logo',
            'banner'
        ]
        widgets = {
            'mission': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your organization\'s mission and goals'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'e.g. +1 (555) 123-4567'}),
            'website': forms.URLInput(attrs={'placeholder': 'e.g. https://www.example.org'}),
        }
        
    def clean_logo(self):
        """Validate logo file if provided"""
        logo = self.cleaned_data.get('logo')
        
        # If this is an update and the user didn't upload a new logo, return the existing one
        if not logo and self.instance and self.instance.logo:
            return self.instance.logo
            
        # If a new logo is provided, validate it (validators in model will handle most checks)
        if logo:
            # Extra validation beyond what's in the model could go here
            pass
            
        return logo
        
    def clean_banner(self):
        """Validate banner file if provided"""
        banner = self.cleaned_data.get('banner')
        
        # If this is an update and the user didn't upload a new banner, return the existing one
        if not banner and self.instance and self.instance.banner:
            return self.instance.banner
            
        # If a new banner is provided, validate it (validators in model will handle most checks)
        if banner:
            # Extra validation beyond what's in the model could go here
            pass
            
        return banner


class OrganisationCreateForm(forms.ModelForm):
    """
    Form for creating a new organization
    
    Used during organization owner registration process.
    Requires additional validation for new organizations.
    """
    
    class Meta:
        model = Organisation
        fields = [
            'name', 
            'website', 
            'mission',
            'contact_phone'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Organization name'}),
            'mission': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Describe your organization\'s mission and goals'
            }),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'e.g. +1 (555) 123-4567'}),
            'website': forms.URLInput(attrs={'placeholder': 'e.g. https://www.example.org'}),
        }
    
    def clean_name(self):
        """Ensure organization name is unique"""
        name = self.cleaned_data.get('name')
        
        # Check if an organization with this name already exists
        if Organisation.objects.filter(name=name).exists():
            raise ValidationError(
                "An organization with this name already exists. Please choose a different name."
            )
            
        return name
