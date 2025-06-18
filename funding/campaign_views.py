from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden, Http404
from django.utils import timezone

from core.mixins import OrganisationOwnerRequiredMixin
from .models import Campaign, Organisation, Donation
from .forms import CampaignForm

from utils.message_utils import add_success, add_error
from utils.constants import Messages


class CampaignListView(ListView):
    model = Campaign
    template_name = 'campaign/list.html'
    context_object_name = 'campaigns'
    paginate_by = 12
    
    def get_queryset(self):
        # Show only active campaigns for public visitors
        return Campaign.objects.filter(status='active').order_by('-created_at')


class CampaignDetailView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/detail.html'
    
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
        total_raised = donations.aggregate(Sum('amount'))['total'] or 0
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
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaign/create.html'
    
    def get_success_url(self):
        return reverse('org:campaign_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.organisation = self.request.user.organisation
        form.instance.status = 'pending'
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        add_success(self.request, Messages.CAMPAIGN_CREATED)
        return response


class CampaignEditView(OrganisationOwnerRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'campaign/edit.html'
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
        return reverse('org:campaign_detail', kwargs={'pk': self.object.pk})


class CampaignCloseView(OrganisationOwnerRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk, organisation=request.user.organisation)
        
        if campaign.status != 'active':
            add_error(request, Messages.CAMPAIGN_NOT_ACTIVE)
            return HttpResponseRedirect(reverse('org:campaign_detail', kwargs={'pk': pk}))
        
        # Close the campaign
        campaign.status = 'closed'
        campaign.closed_at = timezone.now()
        campaign.save()
        
        add_success(request, Messages.CAMPAIGN_CLOSED)
        return HttpResponseRedirect(reverse('org:campaign_detail', kwargs={'pk': pk}))


class CampaignReactivateView(OrganisationOwnerRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=pk, organisation=request.user.organisation)
        
        if campaign.status != 'closed':
            add_error(request, Messages.CAMPAIGN_NOT_CLOSED)
            return HttpResponseRedirect(reverse('org:campaign_detail', kwargs={'pk': pk}))
        
        # Reactivate the campaign
        campaign.status = 'active'
        campaign.closed_at = None
        campaign.save()
        
        add_success(request, Messages.CAMPAIGN_REACTIVATED)
        return HttpResponseRedirect(reverse('org:campaign_detail', kwargs={'pk': pk}))


class CampaignDeleteView(OrganisationOwnerRequiredMixin, DeleteView):
    model = Campaign
    template_name = 'campaign/confirm_delete.html'
    success_url = reverse_lazy('org:campaigns')
    
    def get_queryset(self):
        # Only allow org owners to delete their own campaigns
        return Campaign.objects.filter(organisation=self.request.user.organisation)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        add_success(request, Messages.CAMPAIGN_DELETED)
        return response
