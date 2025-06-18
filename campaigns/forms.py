from django import forms
from django.core.exceptions import ValidationError
from .models import Campaign


class CampaignForm(forms.ModelForm):
    """
    Form for creating and editing campaigns
    
    Handles validation for campaign details including:
    - Title and description requirements
    - Funding goal limits ($100 to $2,000,000)
    - Image upload validation
    """
    
    class Meta:
        model = Campaign
        fields = [
            'title', 
            'description', 
            'funding_goal',
            'category', 
            'cover_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'funding_goal': forms.NumberInput(attrs={'min': 100, 'max': 2000000, 'step': 0.01}),
        }
        
    def clean_funding_goal(self):
        """Ensure funding goal is between $100 and $2,000,000"""
        funding_goal = self.cleaned_data.get('funding_goal')
        
        if funding_goal < 100:
            raise ValidationError("Funding goal must be at least $100.")
            
        if funding_goal > 2000000:
            raise ValidationError("Funding goal cannot exceed $2,000,000.")
            
        return funding_goal
        
    def clean_cover_image(self):
        """Validate campaign cover image if provided"""
        cover_image = self.cleaned_data.get('cover_image')
        
        if cover_image:
            # Check file size (max 5 MB)
            if cover_image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size cannot exceed 5 MB.")
                
            # Check file type
            if not cover_image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError("Only JPG, JPEG, PNG, and GIF files are allowed.")
                
        return cover_image


class CampaignAdminReviewForm(forms.ModelForm):
    """
    Form for admin review of campaigns
    
    Used by staff to approve or reject campaigns with optional rejection reason
    """
    
    class Meta:
        model = Campaign
        fields = ['status', 'rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Required if rejecting the campaign'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        # Require rejection reason if status is 'rejected'
        if status == 'rejected' and not rejection_reason:
            self.add_error('rejection_reason', 
                           "Please provide a reason for rejecting this campaign.")
            
        return cleaned_data
