"""
API views for Campaign models.
"""
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from campaigns.models import Campaign
from .serializers import (
    CampaignListSerializer,
    CampaignDetailSerializer,
    CampaignCreateSerializer,
    CampaignUpdateSerializer
)
from .permissions import IsOwnerOrReadOnly


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow staff to modify, but anyone to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing campaigns.
    
    list:
    Return a list of all campaigns.
    
    retrieve:
    Return the given campaign.
    
    create:
    Create a new campaign.
    
    update:
    Update a campaign.
    
    partial_update:
    Update part of a campaign.
    
    destroy:
    Delete a campaign.
    """
    queryset = Campaign.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'organization']
    search_fields = ['title', 'description', 'content']
    ordering_fields = ['created_at', 'end_date', 'total_raised', 'funding_goal']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """
        Return different serializers based on action.
        """
        if self.action == 'list':
            return CampaignListSerializer
        elif self.action == 'retrieve':
            return CampaignDetailSerializer
        elif self.action == 'create':
            return CampaignCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CampaignUpdateSerializer
        return CampaignListSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on parameters.
        """
        queryset = Campaign.objects.all()
        
        # Filter by organization if provided
        organization_id = self.request.query_params.get('organization_id')
        if organization_id:
            queryset = queryset.filter(organization__id=organization_id)
        
        # Filter active campaigns
        active_only = self.request.query_params.get('active_only')
        if active_only == 'true':
            queryset = queryset.filter(status='active')
        
        # Order by trending if requested
        order_by = self.request.query_params.get('order_by')
        if order_by == 'trending':
            # This would ideally use analytics data to determine trending
            # For now, simple proxy of most recent + highest funded
            queryset = queryset.order_by('-total_raised', '-created_at')
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, slug=None):
        """
        Mark/unmark campaign as favorite.
        """
        campaign = self.get_object()
        user = request.user
        
        # This is a placeholder for a favorite functionality
        # that could be implemented in the future
        return Response({'status': 'Campaign favorited'})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_campaigns(self, request):
        """
        Return campaigns created by the requesting user.
        """
        campaigns = Campaign.objects.filter(creator=request.user)
        page = self.paginate_queryset(campaigns)
        
        if page is not None:
            serializer = CampaignListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = CampaignListSerializer(campaigns, many=True)
        return Response(serializer.data)
