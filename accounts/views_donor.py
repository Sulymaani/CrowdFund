from django.views.generic import TemplateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.contrib import messages

from donations.models import Donation
from campaigns.models import Campaign
from organizations.models import Organisation
from accounts.models import CustomUser
from accounts.forms import ProfileEditForm


class DonorRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only donors can access a view"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'donor'


class DonorDashboardView(LoginRequiredMixin, DonorRequiredMixin, TemplateView):
    """
    Dashboard view for donors showing their donations, supported organizations,
    and overall donation statistics.
    """
    template_name = 'accounts/donor/dashboard.html'

    def test_func(self):
        return self.request.user.role == 'donor'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent donations by this donor - using the correct field name
        recent_donations = Donation.objects.filter(
            donor=user
        ).order_by('-created_at')[:5]
        
        # Get donation stats
        total_donated = Donation.objects.filter(donor=user).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get all donations for this user
        all_donations = Donation.objects.filter(donor=user)
        
        # Get campaigns this donor has supported
        supported_campaigns = Campaign.objects.filter(
            donations__donor=user
        ).distinct()
        
        # Get organizations this donor has supported
        supported_orgs = Organisation.objects.filter(
            campaigns__in=supported_campaigns
        ).distinct()
        
        context.update({
            'recent_donations': recent_donations,
            'total_donated': total_donated,
            'donation_count': all_donations.count(),
            'supported_orgs': supported_orgs,
            'supported_campaigns': supported_campaigns,
        })
        return context


class DonorProfileView(LoginRequiredMixin, DonorRequiredMixin, DetailView):
    """
    View for displaying donor profile information
    
    Shows personal information and account settings for the logged-in donor.
    """
    model = CustomUser
    template_name = 'accounts/donor/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self, queryset=None):
        # Always return the current user's profile
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data needed for the profile view
        return context


class DonorProfileEditView(LoginRequiredMixin, DonorRequiredMixin, UpdateView):
    """
    View for editing donor profile information
    
    Allows donors to update their personal information, preferences,
    notification settings, and other account details.
    """
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'accounts/donor/profile_edit.html'
    success_url = reverse_lazy('donor:profile')
    
    def get_object(self, queryset=None):
        # Always return the current user's profile
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully.')
        return response


class DonorCampaignListView(LoginRequiredMixin, DonorRequiredMixin, TemplateView):
    """
    Donor-focused campaign browsing
    
    Shows campaigns with donor-specific filters, saved campaigns,
    and personalized recommendations.
    """
    template_name = 'accounts/donor/campaigns.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all active campaigns
        active_campaigns = Campaign.objects.filter(status='active').order_by('-created_at')
        
        # Get campaigns this donor has already supported
        supported_campaign_ids = Donation.objects.filter(
            donor=user
        ).values_list('campaign_id', flat=True).distinct()
        
        supported_campaigns = Campaign.objects.filter(id__in=supported_campaign_ids)
        
        # Get recommended campaigns - for now, just exclude supported ones
        recommended_campaigns = active_campaigns.exclude(
            id__in=supported_campaign_ids
        )[:6]
        
        context.update({
            'active_campaigns': active_campaigns[:12],  # Show first 12 active campaigns
            'supported_campaigns': supported_campaigns,
            'recommended_campaigns': recommended_campaigns,
        })
        return context


class DonorOrganizationListView(LoginRequiredMixin, DonorRequiredMixin, TemplateView):
    """
    Donor-focused organization browsing
    
    Shows organizations with donor-specific filters, saved organizations,
    and personalized recommendations.
    """
    template_name = 'accounts/donor/organizations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all active organizations
        active_organizations = Organisation.objects.filter(is_active=True).order_by('name')
        
        # Get organizations this donor has supported
        supported_orgs = Organisation.objects.filter(
            campaigns__donations__donor=user
        ).distinct()
        
        # Get recommended organizations - for now just exclude supported ones
        recommended_orgs = active_organizations.exclude(
            id__in=supported_orgs.values_list('id', flat=True)
        )[:6]
        
        context.update({
            'active_organizations': active_organizations[:12],  # Show first 12 active orgs
            'supported_organizations': supported_orgs,
            'recommended_organizations': recommended_orgs,
        })
        return context
