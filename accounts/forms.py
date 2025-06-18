from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from funding.models import Organisation
from utils.constants import UserRoles
from .forms_base import BaseUserForm, BaseModelForm

class DonorRegistrationForm(BaseUserForm):
    """
    A form for new donors to create a user account.
    The role is automatically set to 'donor'.
    """
    email = forms.EmailField(required=True, label="Email")
    
    class Meta(BaseUserForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserRoles.DONOR
        if commit:
            user.save()
        return user

class OrgRegistrationForm(BaseUserForm):
    """
    A form for new organisations to create an owner user account and an organisation profile.
    The user role is automatically set to 'org_owner'.
    """
    email = forms.EmailField(required=True, label="Email")
    org_name = forms.CharField(max_length=255, label="Organisation Name")
    website = forms.URLField(max_length=200, label="Website")
    mission = forms.CharField(widget=forms.Textarea, label="Mission")
    contact_phone = forms.CharField(max_length=20, label="Contact Phone")

    class Meta(BaseUserForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        # 1. Save the CustomUser with the role 'org_owner'
        user = super().save(commit=False)
        user.role = UserRoles.ORG_OWNER
        if commit:
            user.save()

        # 2. Create the Organisation and link it to the user
        organisation = Organisation.objects.create(
            name=self.cleaned_data['org_name'],
            website=self.cleaned_data['website'],
            mission=self.cleaned_data['mission'],
            contact_phone=self.cleaned_data['contact_phone'],
            customuser=user,
            is_active=True
        )
        
        return user


class ProfileEditForm(BaseModelForm):
    """
    Form for editing user profile information.
    """
    first_name = forms.CharField(max_length=30, required=False, label="First Name")
    last_name = forms.CharField(max_length=30, required=False, label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already in use.")
        return email

        # 3. Associate the user with the new organisation
        user.organisation = organisation
        if commit:
            user.save()

        return user

class ProfileEditForm(forms.ModelForm):
    """
    Form for users to edit their profile information.
    """
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = True
