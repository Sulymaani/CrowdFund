from django.db import models
from django.conf import settings
from django.utils import timezone

class Organisation(models.Model):
    name = models.CharField(max_length=120, unique=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='campaigns')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns_created', null=True, blank=True)
    title = models.CharField(max_length=120)
    description = models.TextField(help_text="Tell the story of your campaign.", null=True, blank=True)
    cover_image = models.ImageField(upload_to='campaign_covers/', null=True, blank=True, help_text="A cover image for your campaign page.")
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

