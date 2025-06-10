from django import forms
from .models import Organisation, Campaign, Donation

class OrganisationApplicationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['name', 'application_notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'application_notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        help_texts = {
            'name': 'The official name of your organisation.',
            'application_notes': 'Please provide a brief description of your organisation and its mission. This will be reviewed by an administrator.'
        }


class OrganisationAdminReviewForm(forms.ModelForm):
    verification_status = forms.ChoiceField(
        choices=Organisation.VERIFICATION_CHOICES,
        widget=forms.RadioSelect,
        label="Verification Status"
    )
    admin_remarks = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="Admin Remarks"
    )

    class Meta:
        model = Organisation
        fields = ['verification_status', 'admin_remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter out 'pending' from choices as admin must pick 'verified' or 'rejected'
        self.fields['verification_status'].choices = [
            (choice, label) for choice, label in Organisation.VERIFICATION_CHOICES 
            if choice in ['verified', 'rejected']
        ]
        if self.instance and self.instance.pk:
            # If updating, set initial value for verification_status if it's not pending
            if self.instance.verification_status != 'pending':
                self.initial['verification_status'] = self.instance.verification_status
            else:
                # Default to no selection if the current status is 'pending'
                self.initial['verification_status'] = None
class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'goal'] # 'organisation' and 'status' are set in the view
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'goal': forms.NumberInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm', 'min': '1'}),
        }
        help_texts = {
            'title': 'The title of your fundraising campaign.',
            'goal': 'The target amount you aim to raise (in whole currency units).',
        }


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
