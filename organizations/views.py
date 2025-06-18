from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.db.models import Sum, Count
import csv

from core.mixins import OrganisationOwnerRequiredMixin
from .models import Organisation
from .forms import OrganisationSettingsForm
from campaigns.models import Campaign
from donations.models import Donation
from utils.message_utils import add_success, add_error
from utils.constants import Messages


class OrganisationDetailView(DetailView):
    """
    Public view for organization profiles
    
    Displays the organization's information, active campaigns,
    and summary statistics for public viewing.
    """
    model = Organisation
    context_object_name = 'organisation'
    template_name = 'organizations/detail.html'
    
    def get_queryset(self):
        # Only show active organizations
        return Organisation.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organisation = self.get_object()
        
        # Get active campaigns for this org
        active_campaigns = Campaign.objects.filter(
            organisation=organisation,
            status='active'
        ).order_by('-created_at')
        
        # Get campaign stats
        campaign_count = active_campaigns.count()
        total_raised = Donation.objects.filter(
            campaign__organisation=organisation,
            campaign__status='active'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate success metrics
        donor_count = Donation.objects.filter(
            campaign__organisation=organisation
        ).values('donor').distinct().count()
        
        context.update({
            'active_campaigns': active_campaigns[:4],  # Just show the first few
            'campaign_count': campaign_count,
            'total_raised': total_raised,
            'donor_count': donor_count,
        })
        
        return context


class OrgDashboardView(OrganisationOwnerRequiredMixin, TemplateView):
    """
    Organization owner dashboard
    
    Central hub showing performance metrics, recent activity,
    and quick links to manage the organization.
    """
    template_name = 'organizations/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        organisation = user.organisation
        
        # Get active campaigns for this org
        active_campaigns = Campaign.objects.filter(
            organisation=organisation,
            status='active'
        ).order_by('-created_at')
        
        # Get pending campaigns awaiting review
        pending_campaigns = Campaign.objects.filter(
            organisation=organisation,
            status='pending'
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
        pending_count = pending_campaigns.count()
        
        context.update({
            'organisation': organisation,
            'active_campaigns': active_campaigns[:3],
            'pending_campaigns': pending_campaigns[:3],
            'recent_donations': recent_donations,
            'total_raised': total_raised,
            'campaign_count': campaign_count,
            'active_count': active_count,
            'pending_count': pending_count,
            'donor_count': Donation.objects.filter(
                campaign__organisation=organisation
            ).values('donor').distinct().count(),
        })
        
        return context


class OrganisationSettingsView(OrganisationOwnerRequiredMixin, View):
    """
    Organization settings management
    
    Allows organization owners to update their organization's 
    profile information, contact details, and branding assets.
    """
    template_name = 'organizations/settings.html'
    
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
            return redirect('organizations:settings')
        
        context = {
            'form': form,
            'organisation': organisation
        }
        
        return render(request, self.template_name, context)


class OrganizationListView(ListView):
    """
    List all active organizations
    
    Public view showing all active organizations that donors
    can browse and view details for.
    """
    model = Organisation
    template_name = 'organizations/list.html'
    context_object_name = 'organizations'
    paginate_by = 12
    
    def get_queryset(self):
        # Only show active organizations
        return Organisation.objects.filter(is_active=True).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add campaign counts for each organization
        orgs_with_counts = []
        for org in context['organizations']:
            active_campaigns = Campaign.objects.filter(
                organisation=org,
                status='active'
            ).count()
            
            orgs_with_counts.append({
                'organization': org,
                'campaign_count': active_campaigns
            })
            
        context['organizations_with_counts'] = orgs_with_counts
        
        return context


class ExportDonationsCSVView(OrganisationOwnerRequiredMixin, View):
    """
    Export donations data as CSV
    
    Allows organization owners to download all donation records
    for their campaigns in CSV format for external analysis.
    """
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
