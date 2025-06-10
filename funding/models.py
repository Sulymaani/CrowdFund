from django.db import models
from django.conf import settings
from django.utils import timezone

class Organisation(models.Model):
    VERIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=120, unique=True)
    application_notes = models.TextField(null=True, blank=True, help_text="Notes submitted by the organisation during application.")
    verification_status = models.CharField(
        max_length=10, 
        choices=VERIFICATION_CHOICES, 
        default='pending', 
        help_text="The current verification status of the organisation."
    )
    admin_remarks = models.TextField(null=True, blank=True, help_text="Internal remarks from an admin regarding the verification.")
    verified = models.BooleanField(default=False, help_text="True if the organisation has been verified by an admin.") # Existing field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_verification_status_display()})"

    def save(self, *args, **kwargs):
        if self.verification_status == 'verified':
            self.verified = True
        else:
            self.verified = False # Ensure it's False for 'pending' or 'rejected'
        super().save(*args, **kwargs)

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='campaigns')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns_created', null=True, blank=True)
    title = models.CharField(max_length=120)
    goal = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_remarks = models.TextField(null=True, blank=True, help_text="Internal remarks from an admin regarding the campaign's status.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Donation(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='donations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'${self.amount} by {self.user.username} for {self.campaign.title}'

