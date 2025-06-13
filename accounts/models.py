from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os
from funding.models import Organisation # Ensure funding.models is available

def user_profile_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.id}/profile/{filename}'

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('org_owner', 'Organisation Owner'),
        # ('org_manager', 'Organisation Manager'), # Optional, for future iterations
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    profile_picture = models.ImageField(upload_to=user_profile_path, blank=True, null=True, help_text='Profile picture of the user')
    organisation = models.ForeignKey(
        Organisation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text='The organisation this user owns or manages, if applicable.'
    )

    def __str__(self):
        return self.username

