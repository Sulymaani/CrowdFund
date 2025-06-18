from django.db import models
from django.conf import settings
from django.utils import timezone


class Donation(models.Model):
    """
    Donation model for tracking financial contributions
    
    Each donation is associated with a specific campaign and donor.
    Donations include amount, reference number, optional comment,
    and timestamp information.
    """
    # Relationships
    campaign = models.ForeignKey(
        'campaigns.Campaign', 
        on_delete=models.CASCADE, 
        related_name='donations'
    )
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mod_donations'
    )
    
    # Donation details
    amount = models.PositiveIntegerField()
    reference_number = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True, 
        help_text="Unique reference number for the donation"
    )
    comment = models.TextField(
        blank=True, 
        null=True, 
        help_text="Comments from the donor"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Donation"
        verbose_name_plural = "Donations"
        ordering = ['-created_at']
        
    def __str__(self):
        return f'${self.amount} by {self.donor.get_full_name() or self.donor.username} for {self.campaign.title}'
        
    def save(self, *args, **kwargs):
        # Generate a reference number if not provided
        if not self.reference_number:
            timestamp = int(timezone.now().timestamp())
            self.reference_number = f"DON-{timestamp}-{self.donor.id if self.donor_id else 0}"
        super().save(*args, **kwargs)
    
    @property
    def formatted_amount(self):
        """Return the donation amount formatted with currency symbol"""
        return f"${self.amount:,}"
    
    @property
    def donation_date(self):
        """Return a nicely formatted donation date"""
        return self.created_at.strftime("%B %d, %Y")
    
    @property
    def is_anonymous(self):
        """Determine if this is an anonymous donation"""
        # For future use if anonymous donations are implemented
        return False
