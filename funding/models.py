from django.db import models
from django.conf import settings
from django.utils import timezone
from core.validators import FileSizeValidator, ImageDimensionsValidator, ImageFormatValidator

def org_logo_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/org_logos/org_<id>/<filename>
    return f'org_logos/org_{instance.id}/{filename}'

def org_banner_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/org_banners/org_<id>/<filename>
    return f'org_banners/org_{instance.id}/{filename}'

class Organisation(models.Model):
    name = models.CharField(max_length=120, unique=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(
        upload_to=org_logo_path, 
        blank=True, 
        null=True, 
        validators=[
            FileSizeValidator(2),  # 2 MB limit
            ImageDimensionsValidator(800, 800),  # 800x800px max
            ImageFormatValidator(['JPEG', 'PNG', 'SVG']),  # Allow common logo formats
        ],
        help_text="Organization logo (max 800x800px, 2MB, formats: JPEG, PNG, SVG)"
    )
    banner = models.ImageField(
        upload_to=org_banner_path, 
        blank=True, 
        null=True,
        validators=[
            FileSizeValidator(3),  # 3 MB limit
            ImageDimensionsValidator(1920, 480),  # 1920x480px max
            ImageFormatValidator(['JPEG', 'PNG']),  # Banner formats
        ],
        help_text="Organization banner (max 1920x480px, 3MB, formats: JPEG, PNG)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='campaigns')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns_created', null=True, blank=True)
    title = models.CharField(max_length=120)
    description = models.TextField(help_text="Tell the story of your campaign.", null=True, blank=True)
    cover_image = models.ImageField(
        upload_to='campaign_covers/', 
        null=True, 
        blank=True, 
        validators=[
            FileSizeValidator(5),  # 5 MB limit
            ImageDimensionsValidator(1920, 1080),  # 1920x1080px max
            ImageFormatValidator(['JPEG', 'PNG']),  # Campaign cover formats
        ],
        help_text="A cover image for your campaign page (max 1920x1080px, 5MB, formats: JPEG, PNG)."
    )
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
    reference_number = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Unique reference number for the donation")
    comment = models.TextField(blank=True, null=True, help_text="Comments from the donor")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'${self.amount} by {self.user.username} for {self.campaign.title}'
        
    def save(self, *args, **kwargs):
        # Generate a reference number if not provided
        if not self.reference_number:
            timestamp = int(timezone.now().timestamp())
            self.reference_number = f"DON-{timestamp}-{self.user.id if self.user_id else 0}"
        super().save(*args, **kwargs)

