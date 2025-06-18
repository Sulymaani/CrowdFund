"""
API serializers for Campaign models.
"""
from rest_framework import serializers
from campaigns.models import Campaign
from organizations.models import Organisation
from accounts.models import CustomUser


class OrganizationMiniSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Organization model used in nested relationships.
    """
    class Meta:
        model = Organisation
        fields = ['id', 'name', 'logo', 'website']


class UserMiniSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for User model used in nested relationships.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name']


class CampaignListSerializer(serializers.ModelSerializer):
    """
    Serializer for Campaign model list view.
    Provides a summary of campaign data.
    """
    organization = OrganizationMiniSerializer(read_only=True)
    creator = UserMiniSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'slug', 'description', 'cover_image',
            'funding_goal', 'end_date', 'created_at', 'status',
            'organization', 'creator', 'days_remaining',
            'progress_percentage', 'total_raised'
        ]
    
    def get_days_remaining(self, obj):
        """
        Calculate days remaining until campaign end date.
        """
        if not obj.end_date:
            return None
            
        from django.utils import timezone
        from datetime import date
        
        today = timezone.now().date() if isinstance(obj.end_date, date) else timezone.now()
        delta = obj.end_date - today if isinstance(obj.end_date, date) else obj.end_date - today.date()
        
        if delta.days < 0:
            return 0
        return delta.days
    
    def get_progress_percentage(self, obj):
        """
        Calculate percentage of funding goal achieved.
        """
        if not obj.funding_goal or obj.funding_goal <= 0:
            return 0
            
        return min(100, int((obj.total_raised / obj.funding_goal) * 100))


class CampaignDetailSerializer(CampaignListSerializer):
    """
    Serializer for Campaign detail view.
    Extends the list serializer with additional detailed information.
    """
    recent_donations = serializers.SerializerMethodField()
    updates = serializers.SerializerMethodField()
    
    class Meta(CampaignListSerializer.Meta):
        fields = CampaignListSerializer.Meta.fields + [
            'content', 'category', 'recent_donations', 'updates'
        ]
    
    def get_recent_donations(self, obj):
        """
        Get recent donations for this campaign.
        """
        try:
            # Return 5 most recent donations
            recent = obj.mod_donations.order_by('-created_at')[:5]
            return [{
                'id': d.id,
                'amount': str(d.amount),
                'donor_name': d.donor.get_full_name() if d.donor else 'Anonymous',
                'date': d.created_at
            } for d in recent]
        except Exception:
            return []
    
    def get_updates(self, obj):
        """
        Get campaign updates if available.
        """
        # This is a placeholder for campaign updates feature
        # that could be implemented in the future
        return []


class CampaignCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Campaign creation.
    """
    class Meta:
        model = Campaign
        fields = [
            'title', 'description', 'content', 'cover_image',
            'funding_goal', 'end_date', 'category', 'organization'
        ]
    
    def create(self, validated_data):
        """
        Create a new campaign and generate a unique slug.
        """
        # Set the creator from the current user
        validated_data['creator'] = self.context['request'].user
        
        # Generate a unique slug from the title
        from django.utils.text import slugify
        from datetime import datetime
        
        base_slug = slugify(validated_data['title'])
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        validated_data['slug'] = f"{base_slug}-{timestamp}"
        
        # Create the campaign
        campaign = super().create(validated_data)
        return campaign


class CampaignUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Campaign updates.
    """
    class Meta:
        model = Campaign
        fields = [
            'title', 'description', 'content', 'cover_image',
            'funding_goal', 'end_date', 'category', 'status'
        ]
        read_only_fields = ['organization', 'creator', 'slug']
