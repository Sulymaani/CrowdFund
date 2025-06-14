from django import forms
from django.core.validators import FileExtensionValidator
from .models import Organisation, Campaign, Donation

class OrganisationRegistrationForm(forms.ModelForm):
    """
    Form for organisations to register with their full details.
    """
    class Meta:
        model = Organisation
        fields = ['name', 'website', 'mission', 'contact_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'website': forms.URLInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'mission': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'contact_phone': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        help_texts = {
            'name': 'The official name of your organisation.',
            'website': "Your organisation's official website.",
            'mission': "Briefly describe your organisation's mission and goals.",
            'contact_phone': 'A contact phone number for the organisation.'
        }

class OrganisationSettingsForm(forms.ModelForm):
    logo = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        widget=forms.FileInput(attrs={'class': 'hidden', 'id': 'logo-upload'}),
        help_text='Upload a logo for your organization (JPG, PNG, or GIF)'
    )
    
    banner = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        widget=forms.FileInput(attrs={'class': 'hidden', 'id': 'banner-upload'}),
        help_text='Upload a banner image for your organization profile (recommended size: 1200×300 pixels)'
    )
    
    class Meta:
        model = Organisation
        fields = ['name', 'mission', 'website', 'logo', 'banner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization Name'}),
            'mission': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your organization'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),
        }
        help_texts = {
            'name': 'Your organization\'s official name',
            'mission': 'A brief description of your organization\'s mission',
            'website': 'Your organization\'s website (optional)',
        }

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'cover_image', 'goal']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 mt-2 text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 6, 
                'class': 'block w-full px-4 py-2 mt-2 text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'cover_image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 file:mr-4 file:py-2 file:px-4 file:border-0 file:text-sm file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
            'goal': forms.NumberInput(attrs={
                'class': 'block w-full pl-8 pr-4 py-2 mt-2 text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 
                'min': '100'
            }),
        }
        help_texts = {
            'title': 'The title of your fundraising campaign.',
            'description': 'Provide a detailed description of your campaign, its goals, and how the funds will be used.',
            'cover_image': 'Upload a compelling cover image for your campaign page.',
            'goal': 'The target amount you aim to raise (in whole currency units).',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure the fields are properly initialized with instance data
        if self.instance and self.instance.pk:
            if not self.is_bound:  # Only set initial if the form is not bound to POST data
                self.fields['title'].initial = self.instance.title
                self.fields['description'].initial = self.instance.description
                self.fields['goal'].initial = self.instance.goal


class CampaignAdminReviewForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=[], # Will be populated in __init__
        widget=forms.RadioSelect,
        label="Campaign Status"
    )
    admin_remarks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        required=False,
        label="Admin Remarks"
    )

    class Meta:
        model = Campaign
        fields = ['status', 'admin_remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Admin must choose to either approve (active) or reject the campaign.
        self.fields['status'].choices = [
            (choice, label) for choice, label in Campaign.STATUS_CHOICES
            if choice in ['active', 'rejected']
        ]


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']
