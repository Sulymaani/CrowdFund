from django import forms
from django.core.exceptions import ValidationError
from .models import Donation


class DonationForm(forms.ModelForm):
    """
    Form for creating a new donation
    
    Handles validation for donation amount and optional comment.
    The campaign and donor are set automatically in the view.
    """
    
    class Meta:
        model = Donation
        fields = ['amount', 'comment']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'min': 5,  # Minimum donation amount
                'step': 1,
                'placeholder': 'Enter donation amount'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Leave a message with your donation (optional)'
            }),
        }
    
    def clean_amount(self):
        """Validate donation amount is within acceptable range"""
        amount = self.cleaned_data.get('amount')
        
        if amount < 5:
            raise ValidationError("Minimum donation amount is $5.")
            
        if amount > 1000000:
            raise ValidationError("Maximum donation amount is $1,000,000.")
            
        return amount
