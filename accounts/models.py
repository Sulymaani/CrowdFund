from django.contrib.auth.models import AbstractUser
from django.db import models
from funding.models import Organisation # Ensure funding.models is available

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('org_owner', 'Organisation Owner'),
        # ('org_manager', 'Organisation Manager'), # Optional, for future iterations
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    organisation = models.ForeignKey(
        Organisation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text='The organisation this user owns or manages, if applicable.'
    )

    def __str__(self):
        return self.username

