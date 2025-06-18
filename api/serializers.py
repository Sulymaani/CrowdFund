from rest_framework import serializers

from campaigns.models import Campaign
from organizations.models import Organisation  
from donations.models import Donation
from tags.models import Tag
from accounts.models import CustomUser


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model with minimal fields for public use.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name']


class OrganisationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organisation model.
    """
    class Meta:
        model = Organisation
        fields = ['id', 'name', 'mission', 'website', 'contact_phone', 'logo', 'banner', 'is_active']


class CampaignSerializer(serializers.ModelSerializer):
    """
    Serializer for Campaign model.
    """
    organisation_name = serializers.ReadOnlyField(source='organisation.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'slug', 'description', 'funding_goal', 'current_amount',
            'start_date', 'end_date', 'category', 'status', 'cover_image',
            'organisation', 'organisation_name', 'created_by', 'created_by_username',
            'created_at', 'updated_at', 'progress_percentage'
        ]
    
    def get_progress_percentage(self, obj):
        """
        Calculate percentage of funding goal reached.
        """
        if not obj.funding_goal:
            return 0
        return min(100, int((obj.current_amount / obj.funding_goal) * 100))


class DonationSerializer(serializers.ModelSerializer):
    """
    Serializer for Donation model.
    """
    donor_name = serializers.SerializerMethodField()
    campaign_title = serializers.ReadOnlyField(source='campaign.title')
    
    class Meta:
        model = Donation
        fields = [
            'id', 'user', 'donor_name', 'campaign', 'campaign_title',
            'amount', 'comment', 'is_anonymous', 'reference_number', 'created_at'
        ]
    
    def get_donor_name(self, obj):
        """
        Return donor name based on anonymity preference.
        """
        if obj.is_anonymous:
            return "Anonymous"
        if obj.user:
            name = f"{obj.user.first_name} {obj.user.last_name}".strip()
            return name if name else obj.user.username
        return "Anonymous"
