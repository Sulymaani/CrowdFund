from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden, Http404, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
import csv

from core.mixins import OrganisationOwnerRequiredMixin
from .models import Campaign, Organisation, Donation
from .forms import OrganisationSettingsForm

from utils.message_utils import add_success, add_error
from utils.constants import Messages


class OrgDashboardView(OrganisationOwnerRequiredMixin, TemplateView):
    template_name = 'org/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        organisation = user.organisation
        
        # Get active campaigns for this org
        active_campaigns = Campaign.objects.filter(
            organisation=organisation,
            status='active'
        ).order_by('-created_at')
        
        # Get recent donations to this org's campaigns
        recent_donations = Donation.objects.filter(
            campaign__organisation=organisation
        ).order_by('-created_at')[:5]
        
        # Get donation stats
        total_raised = Donation.objects.filter(
            campaign__organisation=organisation
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get campaign stats
        campaign_count = Campaign.objects.filter(organisation=organisation).count()
        active_count = active_campaigns.count()
        
        context.update({
            'organisation': organisation,
            'active_campaigns': active_campaigns,
            'recent_donations': recent_donations,
            'total_raised': total_raised,
            'campaign_count': campaign_count,
            'active_count': active_count,
            'donor_count': Donation.objects.filter(
                campaign__organisation=organisation
            ).values('donor').distinct().count(),
        })
        
        return context


class OrgCampaignsListView(OrganisationOwnerRequiredMixin, ListView):
    model = Campaign
    template_name = 'org/campaigns.html'
    context_object_name = 'campaigns'
    
    def get_queryset(self):
        # Only show campaigns belonging to this org owner's organization
        return Campaign.objects.filter(
            organisation=self.request.user.organisation
        ).order_by('-created_at')


class OrgCampaignDetailView(OrganisationOwnerRequiredMixin, DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'campaign/active.html'  # Default template
    
    def get_queryset(self):
        # Only allow org owners to see their own campaigns
        return Campaign.objects.filter(organisation=self.request.user.organisation)
        
    def get_template_names(self):
        # Select the appropriate template based on campaign status
        campaign = self.get_object()
        if campaign.status == 'active':
            return ['campaign/active.html']
        elif campaign.status == 'pending':
            return ['campaign/pending.html']
        elif campaign.status == 'rejected':
            return ['campaign/rejected.html']
        elif campaign.status == 'closed':
            return ['campaign/closed.html']
        else:
            return [self.template_name]
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        
        # Add donation stats
        donations = Donation.objects.filter(campaign=campaign)
        total_raised = donations.aggregate(total=Sum('amount'))['total'] or 0
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


class OrgDonationDetailView(OrganisationOwnerRequiredMixin, DetailView):
    model = Donation
    context_object_name = 'donation'
    template_name = 'org/donation_detail.html'
    slug_field = 'reference_number'
    slug_url_kwarg = 'reference_number'
    
    def get_queryset(self):
        # Org owners can only see donations to their organization's campaigns
        user_org = self.request.user.organisation
        return Donation.objects.filter(campaign__organisation=user_org)


class OrganisationSettingsView(OrganisationOwnerRequiredMixin, View):
    template_name = 'org/settings.html'
    
    def get(self, request, *args, **kwargs):
        organisation = request.user.organisation
        form = OrganisationSettingsForm(instance=organisation)
        
        context = {
            'form': form,
            'organisation': organisation
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        organisation = request.user.organisation
        form = OrganisationSettingsForm(
            request.POST, 
            request.FILES,
            instance=organisation
        )
        
        if form.is_valid():
            form.save()
            add_success(request, Messages.ORGANISATION_UPDATED)
            return redirect('org:settings')
        
        context = {
            'form': form,
            'organisation': organisation
        }
        
        return render(request, self.template_name, context)


class DonationsListView(OrganisationOwnerRequiredMixin, ListView):
    template_name = 'donation/list.html'
    context_object_name = 'donations'
    paginate_by = 25
    
    def get_queryset(self):
        user_org = self.request.user.organisation
        return Donation.objects.filter(campaign__organisation=user_org).order_by('-created_at')


class ExportDonationsCSVView(OrganisationOwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get all donations for this organization
        user_org = request.user.organisation
        donations = Donation.objects.filter(
            campaign__organisation=user_org
        ).select_related('campaign', 'donor').order_by('-created_at')
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{user_org.name}_donations.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Reference', 'Date', 'Campaign', 'Donor Name', 'Donor Email', 'Amount', 'Comment'
        ])
        
        # Add donation data
        for donation in donations:
            writer.writerow([
                donation.reference_number,
                donation.created_at.strftime('%Y-%m-%d %H:%M'),
                donation.campaign.title,
                f"{donation.donor.first_name} {donation.donor.last_name}",
                donation.donor.email,
                donation.amount,
                donation.comment if donation.comment else ''
            ])
        
        return response
