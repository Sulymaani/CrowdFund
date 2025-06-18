from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os
from organizations.models import Organisation # Import from modularized organizations app
from core.validators import FileSizeValidator, ImageDimensionsValidator, ImageFormatValidator

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
    profile_picture = models.ImageField(
        upload_to=user_profile_path, 
        blank=True, 
        null=True, 
        validators=[
            FileSizeValidator(1),  # 1 MB limit
            ImageDimensionsValidator(512, 512),  # 512x512px max
            ImageFormatValidator(['JPEG', 'PNG']),  # Profile picture formats
        ],
        help_text='Profile picture (max 512x512px, 1MB, formats: JPEG, PNG)'
    )
    organisation = models.ForeignKey(
        'organizations.Organisation', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='users',
        help_text='The organisation this user owns or manages, if applicable.'
    )

    def __str__(self):
        return self.username

