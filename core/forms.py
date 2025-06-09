from django import forms
from funding.models import Organisation

class OrganisationAdminReviewForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['verification_status', 'admin_remarks']
        widgets = {
            'verification_status': forms.Select(attrs={'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md'}),
            'admin_remarks': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        help_texts = {
            'verification_status': 'Select the new verification status for this organisation.',
            'admin_remarks': 'Provide any internal remarks regarding this decision. This will not be visible to the organisation.'
        }
