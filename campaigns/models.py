from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from utils.constants import CAMPAIGN_STATUS_CHOICES, CAMPAIGN_CATEGORY_CHOICES


class Campaign(models.Model):
    """
    Campaign model for fundraising initiatives.
    
    Each campaign is created by an organization and must go through
    an approval workflow before becoming active and visible to donors.
    """
    # Basic information
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    description = models.TextField()
    funding_goal = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CAMPAIGN_CATEGORY_CHOICES)
    
    # Media
    cover_image = models.ImageField(upload_to='campaign_covers/', blank=True, null=True)
    
    # Foreign keys
    organisation = models.ForeignKey(
        'organizations.Organisation', 
        on_delete=models.CASCADE, 
        related_name='campaigns'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='mod_campaigns_created'
    )
    
    # Status and workflow
    status = models.CharField(
        max_length=20, 
        choices=CAMPAIGN_STATUS_CHOICES, 
        default='draft'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        permissions = [
            ('review_campaign', 'Can review campaigns'),
            ('close_campaign', 'Can close campaigns'),
            ('reactivate_campaign', 'Can reactivate campaigns'),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('campaigns:detail', kwargs={'pk': self.pk})
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_closed(self):
        return self.status == 'closed'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def days_active(self):
        if not self.created_at:
            return 0
            
        if self.closed_at:
            delta = self.closed_at - self.created_at
        else:
            delta = timezone.now() - self.created_at
            
        return delta.days
        
    def close(self):
        """Close this campaign and record the closing timestamp."""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()
        
    def reactivate(self):
        """Reactivate a closed campaign."""
        if self.status == 'closed':
            self.status = 'active'
            self.closed_at = None
            self.save()
