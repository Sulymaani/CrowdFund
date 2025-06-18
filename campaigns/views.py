from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum
from django.utils import timezone

from core.mixins import OrganisationOwnerRequiredMixin
from .models import Campaign
from .forms import CampaignForm
from donations.models import Donation
from utils.message_utils import add_success, add_error
from utils.constants import Messages


class CampaignListView(ListView):
    """List all active campaigns for public viewing"""
    model = Campaign
    template_name = 'campaigns/list.html'
    context_object_name = 'campaigns'
    paginate_by = 12
    
    def get_queryset(self):
        # Show only active campaigns for public visitors
        return Campaign.objects.filter(status='active').order_by('-created_at')


class CampaignDetailView(DetailView):
    """
    Display a campaign's details
    
    Access control varies based on user role:
    - Public/Donors: Can only view active campaigns
    - Org Owners: Can view their own campaigns regardless of status
    - Staff/Admin: Can view all campaigns
    """
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaigns/detail.html'
    
    def get_queryset(self):
        # Only active campaigns are visible to the general public
        if not self.request.user.is_authenticated or self.request.user.role == 'donor':
            return Campaign.objects.filter(status='active')
        
        # Staff can view all campaigns
        if self.request.user.is_staff:
            return Campaign.objects.all()
            
        # Organization owners can only see their own campaigns 
        if self.request.user.role == 'org_owner':
            return Campaign.objects.filter(organisation=self.request.user.organisation)
            
        # Default case - active campaigns only
        return Campaign.objects.filter(status='active')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        
        # Add donation stats
        donations = Donation.objects.filter(campaign=campaign)
        total_raised = donations.aggregate(Sum('amount'))['amount__sum'] or 0
        donor_count = donations.values('donor').distinct().count()
        
        # Calculate progress percentage
        progress_percent = 0
        if campaign.funding_goal > 0:
            progress_percent = min(100, int((total_raised / campaign.funding_goal) * 100))
        
        # Check if the viewer is the organization owner
        is_org_owner = False
        if self.request.user.is_authenticated and self.request.user.role == 'org_owner':
            is_org_owner = self.request.user.organisation == campaign.organisation
        
        context.update({
            'donations': donations.order_by('-created_at')[:5],
            'total_raised': total_raised,
            'donor_count': donor_count,
            'progress_percent': progress_percent,
            'is_org_owner': is_org_owner,
        })
        
        return context


class CampaignCreateView(OrganisationOwnerRequiredMixin, CreateView):
    """Allow organization owners to create new campaigns"""
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/create.html'
    
    def get_success_url(self):
        return reverse('campaigns:org_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.organisation = self.request.user.organisation
        form.instance.status = 'pending'
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        add_success(self.request, Messages.CAMPAIGN_CREATED)
        return response


class CampaignEditView(OrganisationOwnerRequiredMixin, UpdateView):
    """Allow organization owners to edit their campaigns"""
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaigns/edit.html'
    context_object_name = 'campaign'
    
    def get_queryset(self):
        # Only allow org owners to edit their own campaigns
        return Campaign.objects.filter(organisation=self.request.user.organisation)
    
    def form_valid(self, form):
        # If the campaign was rejected and is being resubmitted
        if self.object.status == 'rejected':
            form.instance.status = 'pending'
            add_success(self.request, Messages.CAMPAIGN_RESUBMITTED)
        else:
            add_success(self.request, Messages.CAMPAIGN_UPDATED)
            
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('campaigns:org_detail', kwargs={'pk': self.object.pk})


class CampaignCloseView(OrganisationOwnerRequiredMixin, View):
    """Close an active campaign"""
    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk, organisation=request.user.organisation)
        
        if campaign.status != 'active':
            add_error(request, Messages.CAMPAIGN_NOT_ACTIVE)
            return HttpResponseRedirect(reverse('campaigns:org_detail', kwargs={'pk': pk}))
        
        # Close the campaign
        campaign.status = 'closed'
        campaign.closed_at = timezone.now()
        campaign.save()
        
        add_success(request, Messages.CAMPAIGN_CLOSED)
        return HttpResponseRedirect(reverse('campaigns:org_detail', kwargs={'pk': pk}))


class CampaignReactivateView(OrganisationOwnerRequiredMixin, View):
    """Reactivate a closed campaign"""
    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk, organisation=request.user.organisation)
        
        if campaign.status != 'closed':
            add_error(request, Messages.CAMPAIGN_NOT_CLOSED)
            return HttpResponseRedirect(reverse('campaigns:org_detail', kwargs={'pk': pk}))
        
        # Reactivate the campaign
        campaign.status = 'active'
        campaign.closed_at = None
        campaign.save()
        
        add_success(request, Messages.CAMPAIGN_REACTIVATED)
        return HttpResponseRedirect(reverse('campaigns:org_detail', kwargs={'pk': pk}))


class CampaignDeleteView(OrganisationOwnerRequiredMixin, DeleteView):
    """Delete a campaign (only drafts can be deleted)"""
    model = Campaign
    template_name = 'campaigns/confirm_delete.html'
    success_url = reverse_lazy('campaigns:org_list')
    
    def get_queryset(self):
        # Only allow org owners to delete their own campaigns
        return Campaign.objects.filter(organisation=self.request.user.organisation)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        add_success(request, Messages.CAMPAIGN_DELETED)
        return response


# Organization owner specific campaign views
class OrgCampaignListView(OrganisationOwnerRequiredMixin, ListView):
    """List all campaigns for an organization owner"""
    model = Campaign
    template_name = 'campaigns/org/list.html'
    context_object_name = 'campaigns'
    
    def get_queryset(self):
        # Only show campaigns belonging to this org owner's organization
        return Campaign.objects.filter(
            organisation=self.request.user.organisation
        ).order_by('-created_at')


class OrgCampaignDetailView(OrganisationOwnerRequiredMixin, DetailView):
    """Org owner view of a campaign with management functions"""
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaigns/org/detail.html'
    
    def get_queryset(self):
        # Only allow org owners to see their own campaigns
        return Campaign.objects.filter(organisation=self.request.user.organisation)
        
    def get_template_names(self):
        # Select the appropriate template based on campaign status
        campaign = self.get_object()
        if campaign.status == 'active':
            return ['campaigns/org/active.html']
        elif campaign.status == 'pending':
            return ['campaigns/org/pending.html']
        elif campaign.status == 'rejected':
            return ['campaigns/org/rejected.html']
        elif campaign.status == 'closed':
            return ['campaigns/org/closed.html']
        else:
            return [self.template_name]
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        
        # Add donation stats
        donations = Donation.objects.filter(campaign=campaign)
        total_raised = donations.aggregate(Sum('amount'))['amount__sum'] or 0
        donor_count = donations.values('donor').distinct().count()
        
        # Calculate progress percentage
        progress_percent = 0
        if campaign.funding_goal > 0:
            progress_percent = min(100, int((total_raised / campaign.funding_goal) * 100))
        
        context.update({
            'donations': donations.order_by('-created_at')[:10],
            'total_raised': total_raised,
            'donor_count': donor_count,
            'progress_percent': progress_percent,
            'is_org_owner': True,
        })
        
        return context


# Admin campaign management views
class AdminCampaignListView(UserPassesTestMixin, ListView):
    """List all campaigns for admin review"""
    model = Campaign
    template_name = 'campaigns/admin/list.html'
    context_object_name = 'campaigns'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return Campaign.objects.all().order_by('-created_at')


class AdminCampaignReviewView(UserPassesTestMixin, UpdateView):
    """Admin view to review and approve/reject campaigns"""
    model = Campaign
    template_name = 'campaigns/admin/review.html'
    fields = ['status', 'rejection_reason']
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        # Add appropriate message based on the decision
        if form.instance.status == 'active':
            add_success(self.request, f"Campaign '{form.instance.title}' has been approved")
        elif form.instance.status == 'rejected':
            add_success(self.request, f"Campaign '{form.instance.title}' has been rejected")
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('campaigns:admin_list')
