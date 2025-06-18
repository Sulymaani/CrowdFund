from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from campaigns.models import Campaign
from organizations.models import Organisation
from donations.models import Donation
from tags.models import Tag
from accounts.models import CustomUser

from .serializers import (
    CampaignSerializer, OrganisationSerializer,
    DonationSerializer, TagSerializer, UserSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows tags to be viewed.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    lookup_field = 'slug'


class OrganisationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows organizations to be viewed or edited.
    """
    queryset = Organisation.objects.filter(is_active=True)
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'mission']
    ordering_fields = ['name', 'created_at']
    
    def get_permissions(self):
        """
        Custom permissions:
        - List and retrieve are available to anyone
        - Create, update, partial_update and destroy require authentication
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
    
    @action(detail=True)
    def campaigns(self, request, pk=None):
        """
        Return all campaigns for the specified organization.
        """
        organisation = self.get_object()
        campaigns = Campaign.objects.filter(organisation=organisation)
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)


class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows campaigns to be viewed or edited.
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'end_date', 'current_amount']
    
    def get_queryset(self):
        """
        Filter campaigns based on query parameters:
        - status: Filter by campaign status
        - organisation: Filter by organisation ID
        - active: Filter by active campaigns (not ended)
        """
        queryset = Campaign.objects.all()
        
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        organisation_id = self.request.query_params.get('organisation', None)
        if organisation_id:
            queryset = queryset.filter(organisation__id=organisation_id)
        
        active = self.request.query_params.get('active', None)
        if active and active.lower() == 'true':
            queryset = queryset.filter(end_date__gt=timezone.now())
        
        return queryset
    
    def get_permissions(self):
        """
        Custom permissions:
        - List and retrieve are available to anyone
        - Create, update, partial_update and destroy require authentication
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    @action(detail=True)
    def donations(self, request, pk=None):
        """
        Return all donations for the specified campaign.
        """
        campaign = self.get_object()
        donations = Donation.objects.filter(campaign=campaign)
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)


class DonationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows donations to be viewed or created.
    """
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        Filter donations based on query parameters and user permissions:
        - If admin, see all donations
        - If authenticated, see own donations and public anonymous donations
        - If not authenticated, see only public anonymous donations
        """
        user = self.request.user
        
        if user.is_staff:
            return Donation.objects.all()
        
        if user.is_authenticated:
            # User can see their own donations and public non-anonymous donations
            return Donation.objects.filter(
                user=user
            ) | Donation.objects.filter(
                is_anonymous=False
            )
        
        # Unauthenticated users can only see public non-anonymous donations
        return Donation.objects.filter(is_anonymous=False)
    
    def perform_create(self, serializer):
        """
        Set the user to the current authenticated user when creating a donation.
        """
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Return the authenticated user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
