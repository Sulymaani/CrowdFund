from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.db.models import Sum, Value, F, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from core.mixins import DonorRequiredMixin, OrganisationOwnerRequiredMixin
from accounts.models import CustomUser
from .models import Campaign, Organisation, Donation
from .forms import CampaignForm, DonationForm, OrganisationSettingsForm


class CampaignListView(ListView):
    model = Campaign
    template_name = 'funding/campaign_list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        return Campaign.objects.filter(status='active').order_by('-created_at')


class CampaignDetailView(DetailView):
    model = Campaign
    context_object_name = 'campaign'
    
    def get_template_names(self):
        # Select template based on campaign status and user role
        campaign = self.get_object()
        user = self.request.user
        
        # Debug status and template selection
        print(f"DEBUG: Campaign ID: {campaign.id}, Title: {campaign.title}, Status: '{campaign.status}'")
        
        if user.is_authenticated and user.role == 'org_owner' and hasattr(user, 'organisation'):
            # Is this the org owner's own campaign?
            if campaign.organisation.id == user.organisation.id:
                if campaign.status == 'rejected':
                    print(f"DEBUG: Selected template: campaign_rejected.html")
                    return ['funding/campaign_rejected.html']
                elif campaign.status == 'closed':
                    print(f"DEBUG: Selected template: campaign_closed.html")
                    return ['funding/campaign_closed.html']
                elif campaign.status == 'active':
                    print(f"DEBUG: Selected template: campaign_active.html")
                    return ['funding/campaign_active.html']
                elif campaign.status == 'pending':
                    print(f"DEBUG: Selected template: campaign_pending.html")
                    return ['funding/campaign_pending.html']
                    
        # Debug fallback template
        print(f"DEBUG: Fallback to default template: campaign_detail.html")
        
        # Default template for active campaigns and other users
        return ['funding/campaign_detail.html']

    def get_queryset(self):
        # Show active campaigns to public, but allow org owners to see their own campaigns regardless of status
        user = self.request.user
        if user.is_authenticated and user.role == 'org_owner' and hasattr(user, 'organisation'):
            # Get campaigns where user is the org owner
            org_campaigns = Campaign.objects.filter(organisation=user.organisation)
            return org_campaigns
        else:
            # Others only see active campaigns
            return Campaign.objects.filter(status='active')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        total_donations = campaign.donations.aggregate(total=Sum('amount'))['total'] or 0

        if campaign.goal > 0:
            width_percentage = min(int((total_donations / campaign.goal) * 100), 100)
        else:
            width_percentage = 0

        context['total_donations'] = total_donations
        context['width_percentage'] = width_percentage
        context['total_amount'] = total_donations  # For closed campaign template
        context['total_raised'] = total_donations  # For active campaign template
        
        # For active campaign template
        context['num_donations'] = campaign.donations.count()
        context['recent_donations'] = campaign.donations.order_by('-created_at')[:5]

        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'donor':
            context['donation_form'] = DonationForm()
            
        return context


class CreateDonationView(LoginRequiredMixin, DonorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs['pk'])

        if campaign.status != 'active':
            messages.error(request, 'Donations are only allowed for active campaigns.')
            return redirect('funding:campaign_detail', pk=campaign.pk)

        form = DonationForm(request.POST)

        if form.is_valid():
            donation = form.save(commit=False)
            donation.campaign = campaign
            donation.user = request.user
            donation.save()
            messages.success(request, f'Thank you for your generous donation of ${donation.amount}!')
        else:
            messages.error(request, 'There was an error with your donation. Please check the amount.')

        return redirect('org:campaign_detail', pk=campaign.pk)


class CampaignCreateView(OrganisationOwnerRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'funding/campaign_form.html'
    success_url = reverse_lazy('org:dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Enforce max pending campaigns limit
        user = request.user
        if user.is_authenticated and hasattr(user, 'organisation'):
            pending_count = Campaign.objects.filter(
                organisation=user.organisation,
                status='pending'
            ).count()
            if pending_count >= 3:
                messages.error(request, 'You can have a maximum of 3 pending campaigns. Please wait for admin approval before submitting more.')
                return redirect('org:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Use transaction.atomic to prevent race conditions
        from django.db import transaction
        
        with transaction.atomic():
            # Check if this same campaign was recently submitted (prevent duplicates)
            title = form.cleaned_data.get('title')
            recent_duplicate = Campaign.objects.filter(
                organisation=self.request.user.organisation,
                title=title
            ).exists()
            
            if recent_duplicate:
                messages.warning(
                    self.request, 
                    f'A campaign with the title "{title}" already exists. Please use a different title or check your campaigns list.'
                )
                return self.form_invalid(form)
            
        # Set required fields
        form.instance.organisation = self.request.user.organisation
        form.instance.creator = self.request.user
        
        # Enforce goal limits
        if form.cleaned_data['goal'] < 100:
            form.add_error('goal', 'Campaign goal must be at least $100.')
            return self.form_invalid(form)
        if form.cleaned_data['goal'] > 2000000:
            form.add_error('goal', 'Campaign goal cannot exceed $2,000,000.')
            return self.form_invalid(form)
            
        response = super().form_valid(form)
        messages.success(self.request, f'Your campaign "{form.instance.title}" has been submitted and is pending review.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Campaign'
        if self.request.user.is_authenticated and isinstance(self.request.user, CustomUser) and self.request.user.organisation:
            context['organisation_name'] = self.request.user.organisation.name
        return context


class OrganisationListView(ListView):
    model = Organisation
    template_name = 'funding/organisation_list.html'
    context_object_name = 'organisations'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Browse Organisations'
        return context


# --- Dashboards ---

class DonorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'funding/donor_dashboard.html'

    def test_func(self):
        return self.request.user.role == 'donor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Donations'
        context['donations'] = Donation.objects.filter(user=self.request.user).order_by('-created_at')
        return context


class OrgCampaignsListView(OrganisationOwnerRequiredMixin, ListView):
    model = Campaign
    template_name = 'funding/org_campaigns.html'
    context_object_name = 'campaigns'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Debug campaign statuses in list
        for campaign in context['campaigns']:
            print(f"LIST DEBUG: Campaign {campaign.id} - {campaign.title} has status '{campaign.status}'")
        return context
    
    def get_queryset(self):
        # Filter campaigns by the org owner's organization
        org = self.request.user.organisation
        status_filter = self.request.GET.get('status')
        
        # Base queryset with total donation amounts
        queryset = Campaign.objects.filter(organisation=org)
        
        # Apply status filter if provided
        if status_filter and status_filter in ['draft', 'pending', 'active', 'rejected', 'closed']:
            queryset = queryset.filter(status=status_filter)
            
        # Annotate with total raised
        return queryset.annotate(
            total_raised=Coalesce(Sum('donations__amount'), Value(0))
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Campaigns'
        # Add status for tab highlighting
        context['current_status'] = self.request.GET.get('status', 'all')
        return context


class OrgDashboardView(OrganisationOwnerRequiredMixin, TemplateView):
    template_name = 'funding/org_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.request.user.organisation
        import json
        import random
        from datetime import datetime, timedelta

        # KPI Calculations
        total_raised = Donation.objects.filter(campaign__organisation=org).aggregate(Sum('amount'))['amount__sum'] or 0
        active_campaigns = Campaign.objects.filter(organisation=org, status='active').count()
        total_donors = Donation.objects.filter(campaign__organisation=org).values('user').distinct().count()
        campaigns_pending = Campaign.objects.filter(organisation=org, status='pending').count()
        
        # Get the number of new donors this month
        first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_donors_this_month = Donation.objects.filter(
            campaign__organisation=org,
            created_at__gte=first_day_of_month
        ).values('user').distinct().count()

        # Sample trend data for sparklines (if no real data available)
        def generate_trend_data(length=12, growth_factor=1.2):
            base = random.randint(10, 20)
            data = []
            for i in range(length):
                # Create realistic growth pattern with some randomness
                val = base * (1 + (random.random() * 0.3 - 0.1)) * (growth_factor ** (i/6))
                data.append(int(val))
            return json.dumps(data)

        # Get period-based donation data for the chart
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        current_day = now.day
        
        # Weekly data - last 7 days
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        weekly_labels = []
        weekly_values = []
        
        for i in range(7):
            day = now - timedelta(days=i)
            day_name = day.strftime('%a')
            weekly_labels.insert(0, day_name)
            
            # Get donations for this day
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            day_donations = Donation.objects.filter(
                campaign__organisation=org,
                created_at__gte=day_start,
                created_at__lte=day_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            weekly_values.insert(0, day_donations)
        
        # Monthly data - last 4 weeks
        weekly_labels_month = []
        weekly_values_month = []
        
        for i in range(4):
            week_end = now - timedelta(days=i*7)
            week_start = week_end - timedelta(days=6)
            week_label = f"Week {4-i}"
            weekly_labels_month.insert(0, week_label)
            
            week_donations = Donation.objects.filter(
                campaign__organisation=org,
                created_at__gte=week_start,
                created_at__lte=week_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            weekly_values_month.insert(0, week_donations)
            
        # Yearly data - last 12 months
        months = []
        monthly_values = []
        
        # Try to get actual monthly donation data
        for i in range(12):
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
        
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
            month_name = start_date.strftime('%b')
            months.insert(0, month_name)
        
            # Get actual donations for this month
            month_donations = Donation.objects.filter(
                campaign__organisation=org,
                created_at__gte=start_date,
                created_at__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum'] or 0
        
            monthly_values.insert(0, month_donations)
    
        # Check if we have real data or need sample data
        if sum(monthly_values) == 0:
            # Use sample data if no real data exists
            monthly_values = [1200, 1900, 3000, 2400, 1800, 3200, 2100, 2800, 3500, 4200, 3800, 4500]
        
        if sum(weekly_values) == 0:
            # Sample data for weekly
            weekly_values = [125, 232, 187, 290, 346, 402, 501]
            
        if sum(weekly_values_month) == 0:
            # Sample data for monthly (weeks)
            weekly_values_month = [1250, 1432, 1687, 1890]
    
        # Calculate month-over-month growth for KPI card
        current_month_donations = monthly_values[-1] if monthly_values else 0
        prev_month_donations = monthly_values[-2] if len(monthly_values) > 1 and monthly_values[-2] > 0 else 1
        raised_percentage = int((current_month_donations / prev_month_donations - 1) * 100) if prev_month_donations else 0
    
        # Get donation sources data (try real data first, then fallback to samples)
        source_categories = {}
        source_donations = Donation.objects.filter(campaign__organisation=org)
        
        # Try to analyze real donation sources if we have data
        if source_donations.exists():
            # Sample logic for categorizing sources - adapt to your actual data model
            for donation in source_donations:
                source = 'Direct'  # Default category
                
                # Example logic - replace with your actual referral source logic
                if hasattr(donation, 'source') and donation.source:
                    source = donation.source
                elif hasattr(donation, 'referrer') and donation.referrer:
                    if 'facebook' in donation.referrer.lower() or 'twitter' in donation.referrer.lower() or 'instagram' in donation.referrer.lower():
                        source = 'Social Media'
                    elif 'email' in donation.referrer.lower() or 'newsletter' in donation.referrer.lower():
                        source = 'Email'
                    elif donation.referrer != '':
                        source = 'Referral'
                
                if source not in source_categories:
                    source_categories[source] = 0
                source_categories[source] += donation.amount
            
            # Convert to format needed for the chart
            sources = {
                'labels': list(source_categories.keys()),
                'values': list(source_categories.values())
            }
        else:
            # Sample data if no real data
            sources = {
                'labels': ['Direct', 'Social Media', 'Email', 'Referral', 'Other'],
                'values': [3500, 2200, 1800, 950, 550]  # Sample values
            }

        # Prepare trends data for the chart periods
        donation_trends_data = {
            'weekly': {
                'labels': weekly_labels,
                'values': weekly_values
            },
            'monthly': {
                'labels': weekly_labels_month,
                'values': weekly_values_month
            },
            'yearly': {
                'labels': months,
                'values': monthly_values
            }
        }

        context['page_title'] = 'My Organisation Dashboard'
        context['organisation'] = org
        context['kpis'] = {
            'total_raised': total_raised,
            'active_campaigns': active_campaigns,
            'total_donors': total_donors,
            'campaigns_pending': campaigns_pending,
            'raised_percentage': raised_percentage,
            'new_donors': new_donors_this_month,
            'monthly_donations': ','.join(map(str, monthly_values[-6:])),  # Last 6 months
            'donations_trend': generate_trend_data(),
            'campaigns_trend': generate_trend_data(growth_factor=1.1),
            'donors_trend': generate_trend_data(growth_factor=1.3),
            'donations_chart_data': json.dumps(donation_trends_data),
            'donation_sources': json.dumps(sources)
        }
    
        context['campaigns'] = Campaign.objects.filter(
            organisation=self.request.user.organisation
        ).annotate(
            total_raised=Coalesce(Sum('donations__amount'), Value(0))
        ).order_by('-created_at')
    
        return context


class CampaignEditView(OrganisationOwnerRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'funding/campaign_form.html'
    
    def get_queryset(self):
        # Allow editing of any campaign belonging to this organization for now
        # We'll add status restrictions back once we fix the core issue
        queryset = Campaign.objects.filter(
            organisation=self.request.user.organisation
        )
        print(f"DEBUG: EditView queryset has {queryset.count()} items with pk={self.kwargs.get('pk')}")
        return queryset
    
    def get_success_url(self):
        return reverse_lazy('org:campaign_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Enforce goal limits
        if form.cleaned_data['goal'] < 100:
            form.add_error('goal', 'Campaign goal must be at least $100.')
            return self.form_invalid(form)
        if form.cleaned_data['goal'] > 2000000:
            form.add_error('goal', 'Campaign goal cannot exceed $2,000,000.')
            return self.form_invalid(form)
        
        # Check if any changes were made to the campaign
        original = Campaign.objects.get(pk=self.object.pk)
        has_changes = False
        
        # Compare each field to see if it changed
        if form.cleaned_data['title'] != original.title:
            has_changes = True
        elif form.cleaned_data['description'] != original.description:
            has_changes = True
        elif form.cleaned_data['goal'] != original.goal:
            has_changes = True
        elif form.cleaned_data['cover_image'] and form.cleaned_data['cover_image'] != original.cover_image:
            has_changes = True
        
        # If no changes were made, don't submit and show a message
        if not has_changes:
            messages.warning(self.request, 'No changes detected. Please make changes before resubmitting the campaign.')
            return self.render_to_response(self.get_context_data(form=form))
        
        # Always set status to 'pending' when editing a campaign
        # This ensures rejected campaigns go back for admin review
        self.object = form.save(commit=False)
        self.object.status = 'pending'
        self.object.save()
            
        messages.success(self.request, f'Your campaign "{self.object.title}" has been updated and is pending review.')
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        """Override post method to ensure proper object handling"""
        try:
            self.object = self.get_object()
            print(f"DEBUG: Found object for editing with pk={self.object.pk}, status={self.object.status}")
            return super().post(request, *args, **kwargs)
        except Exception as e:
            print(f"DEBUG: Error in CampaignEditView.post: {e}")
            messages.error(request, f"Error processing form: {str(e)}")
            return redirect('org:campaigns')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Campaign'
        context['is_edit'] = True
        context['organisation_name'] = self.request.user.organisation.name
        return context

class CampaignCloseView(OrganisationOwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=kwargs['pk'], organisation=request.user.organisation)
        
        # Only allow closing active campaigns
        if campaign.status != 'active':
            # Don't show an error for closed campaigns - they're already closed
            if campaign.status == 'closed':
                # Redirect to the closed campaign view instead
                return redirect('org:campaign_detail', pk=campaign.pk)
            else:
                messages.error(request, 'Only active campaigns can be closed.')
                return redirect('funding:campaign_detail', pk=campaign.pk)
                
        return render(request, 'funding/campaign_close.html', {
            'campaign': campaign,
            'page_title': f'Close Campaign: {campaign.title}'
        })
    
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=kwargs['pk'], organisation=request.user.organisation)
        
        if campaign.status != 'active':
            messages.error(request, 'Only active campaigns can be closed.')
            return redirect('org:campaign_detail', pk=campaign.pk)
        else:
            campaign.status = 'closed'
            campaign.save()
            messages.success(request, f'Your campaign "{campaign.title}" has been closed.')
            # Fix: Use the fully qualified URL name with namespace to avoid redirect errors
            return redirect('org:campaigns')
        
        # This line should never be reached, but just in case
        return redirect('org_dashboard')


class CampaignReactivateView(OrganisationOwnerRequiredMixin, View):
    """
    View for reactivating a closed campaign.
    This allows organizations to run a campaign again after it was closed.
    """
    def get(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=kwargs['pk'], organisation=request.user.organisation)
        
        # Only allow reactivating closed campaigns
        if campaign.status != 'closed':
            if campaign.status == 'active':
                messages.info(request, 'This campaign is already active.')
            else:
                messages.error(request, f'Only closed campaigns can be reactivated. Current status: {campaign.get_status_display()}')
            
            return redirect('org:campaign_detail', pk=campaign.pk)
        
        # Show confirmation page
        return render(request, 'funding/campaign_reactivate.html', {
            'campaign': campaign,
            'page_title': f'Reactivate Campaign: {campaign.title}'
        })
    
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=kwargs['pk'], organisation=request.user.organisation)
        
        if campaign.status != 'closed':
            messages.error(request, 'Only closed campaigns can be reactivated.')
            return redirect('org:campaign_detail', pk=campaign.pk)
        else:
            campaign.status = 'active'
            campaign.save()
            messages.success(request, f'Your campaign "{campaign.title}" has been reactivated and is now accepting donations.')
            return redirect('org:campaign_detail', pk=campaign.pk)
        
        # This line should never be reached, but just in case
        return redirect('org:dashboard')


class CampaignDeleteView(OrganisationOwnerRequiredMixin, View):
    """
    View for deleting a campaign.
    Only closed, rejected, or pending campaigns can be deleted.
    """
    def get(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=kwargs['pk'], organisation=request.user.organisation)
        
        # Only allow deleting campaigns that are closed, rejected, or pending
        if campaign.status not in ['closed', 'rejected', 'pending']:
            messages.error(request, 'Only closed, rejected, or pending campaigns can be deleted.')
            return redirect('org:campaign_detail', pk=campaign.pk)
        
        # Show confirmation page
        return render(request, 'funding/campaign_delete.html', {
            'campaign': campaign,
            'page_title': f'Delete Campaign: {campaign.title}'
        })
    
    def post(self, request, *args, **kwargs):
        # Use try/except to handle the case where the campaign doesn't exist
        try:
            campaign = Campaign.objects.get(pk=kwargs['pk'], organisation=request.user.organisation)
            
            # Only allow deleting campaigns that are closed, rejected, or pending
            if campaign.status not in ['closed', 'rejected', 'pending']:
                messages.error(request, 'Only closed, rejected, or pending campaigns can be deleted.')
                return redirect('org:campaign_detail', pk=campaign.pk)
            
            # Check if the campaign has donations
            has_donations = campaign.donations.exists()
            
            if has_donations:
                messages.error(request, 'Cannot delete this campaign because it has donations associated with it.')
                return redirect('org:campaign_detail', pk=campaign.pk)
            
            # Store campaign title and status for success message before deletion
            campaign_title = campaign.title
            campaign_status = campaign.status
            
            # Delete the campaign
            campaign.delete()
            
            # Show success message
            messages.success(request, f'Your campaign "{campaign_title}" has been permanently deleted.')
            
            # Redirect to the campaigns page with the appropriate tab selected
            from django.urls import reverse
            return redirect(reverse('org:campaigns') + f'?status={campaign_status}')
            
        except Campaign.DoesNotExist:
            # If campaign doesn't exist (might have been deleted already), just redirect to campaigns page
            messages.info(request, 'This campaign may have been already deleted.')
            return redirect('org:campaigns')


class DonationsListView(OrganisationOwnerRequiredMixin, ListView):
    template_name = 'funding/donations_list.html'
    context_object_name = 'donations'
    paginate_by = 25
    
    def get_queryset(self):
        org = self.request.user.organisation
        # Only show donations for active campaigns
        queryset = Donation.objects.filter(campaign__organisation=org, campaign__status='active')
        
        # Handle search filter if provided
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(campaign__title__icontains=search_query) | 
                Q(user__username__icontains=search_query)
            )
            
        # Handle campaign filter if provided
        campaign_filter = self.request.GET.get('campaign')
        if campaign_filter:
            queryset = queryset.filter(campaign__pk=campaign_filter)
        
        return queryset.select_related('campaign', 'user').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Donations'
        context['total_amount'] = self.get_queryset().aggregate(Sum('amount'))['amount__sum'] or 0
        context['campaigns'] = Campaign.objects.filter(organisation=self.request.user.organisation)
        context['search_query'] = self.request.GET.get('q', '')
        context['campaign_filter'] = self.request.GET.get('campaign', '')
        return context


class OrgCampaignDetailView(OrganisationOwnerRequiredMixin, DetailView):
    model = Campaign
    context_object_name = 'campaign'
    template_name = 'funding/campaign_active.html'  # Default template
    
    def get_queryset(self):
        # Only allow org owners to see their own campaigns
        return Campaign.objects.filter(organisation=self.request.user.organisation)
    
    def get_template_names(self):
        # Select template based on campaign status
        campaign = self.get_object()
        
        if campaign.status == 'rejected':
            return ['funding/campaign_rejected.html']
        elif campaign.status == 'closed':
            return ['funding/campaign_closed.html']
        elif campaign.status == 'active':
            return ['funding/campaign_active.html']
        elif campaign.status == 'pending':
            return ['funding/campaign_pending.html']
        else:  # draft or any other status
            return ['funding/campaign_active.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        total_donations = campaign.donations.aggregate(total=Sum('amount'))['total'] or 0

        if campaign.goal > 0:
            width_percentage = min(int((total_donations / campaign.goal) * 100), 100)
        else:
            width_percentage = 0

        context['total_donations'] = total_donations
        context['width_percentage'] = width_percentage
        context['total_amount'] = total_donations
        context['total_raised'] = total_donations
        
        # Only show donation details for active campaigns
        if campaign.status == 'active':
            context['num_donations'] = campaign.donations.count()
            context['recent_donations'] = campaign.donations.order_by('-created_at')[:5]
        else:
            context['num_donations'] = 0
            context['recent_donations'] = []
            
        context['page_title'] = 'Campaign Details'
        
        return context


class DonationDetailView(LoginRequiredMixin, DetailView):
    model = Donation
    context_object_name = 'donation'
    template_name = 'funding/donation_detail.html'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'donor':
            # Donors can only see their own donations
            return Donation.objects.filter(user=user)
        else:
            # Admins can see all donations, org_owners handled by OrgDonationDetailView
            return Donation.objects.all() if user.is_staff else Donation.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Donation Details'
        return context


class OrgDonationDetailView(OrganisationOwnerRequiredMixin, DetailView):
    model = Donation
    context_object_name = 'donation'
    template_name = 'funding/org_donation_detail.html'
    slug_field = 'reference_number'
    slug_url_kwarg = 'reference_number'
    
    def get_queryset(self):
        # Allow viewing donations for any campaign owned by this organization
        return Donation.objects.filter(
            campaign__organisation=self.request.user.organisation
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Donation Details'
        return context


class ExportDonationsCSVView(OrganisationOwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        org = request.user.organisation
        queryset = Donation.objects.filter(campaign__organisation=org)
        
        # Handle filters if provided (same as in DonationsListView)
        search_query = request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(campaign__title__icontains=search_query) | 
                Q(user__username__icontains=search_query)
            )
            
        campaign_filter = request.GET.get('campaign')
        if campaign_filter:
            queryset = queryset.filter(campaign__pk=campaign_filter)
        
        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="donations_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Campaign', 'Donor', 'Amount'])
        
        for donation in queryset.select_related('campaign', 'user'):
            writer.writerow([
                donation.created_at.strftime('%Y-%m-%d %H:%M'),
                donation.campaign.title,
                donation.user.username,
                donation.amount
            ])
            
        return response


class OrganisationSettingsView(OrganisationOwnerRequiredMixin, View):
    template_name = 'funding/org_settings.html'
    
    def get(self, request, *args, **kwargs):
        organisation = request.user.organisation
        # Explicitly force view mode by default
        # Only enter edit mode if edit=true is EXPLICITLY passed
        edit_param = request.GET.get('edit', None)
        edit_mode = (edit_param is not None and edit_param.lower() == 'true')
        
        form = None
        if edit_mode:
            form = OrganisationSettingsForm(instance=organisation)
        
        return render(request, self.template_name, {
            'form': form,
            'edit_mode': edit_mode,
            'page_title': 'Organisation Settings',
            'organisation': organisation
        })
    
    def post(self, request, *args, **kwargs):
        organisation = request.user.organisation
        form = OrganisationSettingsForm(request.POST, request.FILES, instance=organisation)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your organisation profile has been updated.')
            # Explicitly redirect to view mode after successful update
            return redirect('org:settings')
        
        return render(request, self.template_name, {
            'form': form,
            'edit_mode': True,
            'page_title': 'Organisation Settings',
            'organisation': organisation
        })
