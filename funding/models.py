from django.db import models
from django.utils.text import slugify

# Import models from modularized apps - these replace the original models that were here
from organizations.models import Organisation
from campaigns.models import Campaign
from donations.models import Donation

# These functions are kept for backward compatibility with existing migrations
def org_logo_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/org_logos/org_<id>/<filename>
    return f'org_logos/org_{instance.id}/{filename}'

def org_banner_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/org_banners/org_<id>/<filename>
    return f'org_banners/org_{instance.id}/{filename}'

# Keep the Tag model which hasn't been modularized yet
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# This file now uses the modularized models instead of defining them directly
# The original Organisation, Campaign, and Donation models have been moved to their respective apps

