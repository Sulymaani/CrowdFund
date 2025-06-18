from django.db import models
from django.conf import settings
from core.validators import FileSizeValidator, ImageDimensionsValidator, ImageFormatValidator


def org_logo_path(instance, filename):
    """
    Define upload path for organization logos
    
    File will be uploaded to MEDIA_ROOT/org_logos/org_<id>/<filename>
    """
    return f'org_logos/org_{instance.id}/{filename}'


def org_banner_path(instance, filename):
    """
    Define upload path for organization banners
    
    File will be uploaded to MEDIA_ROOT/org_banners/org_<id>/<filename>
    """
    return f'org_banners/org_{instance.id}/{filename}'


class Organisation(models.Model):
    """
    Organisation model represents charitable or non-profit organizations
    that can create fundraising campaigns.
    
    Each organization has a profile with contact information, branding assets,
    and can be associated with multiple users (org_owners) and campaigns.
    """
    # Basic information
    name = models.CharField(max_length=120, unique=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Branding assets
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
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # The related CustomUser objects are linked via related_name='organisation'
    # on the CustomUser model's organisation field
    
    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
        ordering = ['name']
        
    def __str__(self):
        return self.name
        
    @property
    def owner_count(self):
        """Returns the number of users associated with this organization"""
        return self.users.filter(role='org_owner').count()
        
    @property
    def campaign_count(self):
        """Returns the number of campaigns created by this organization"""
        return self.campaigns.count()
        
    @property
    def active_campaign_count(self):
        """Returns the number of active campaigns by this organization"""
        return self.campaigns.filter(status='active').count()
