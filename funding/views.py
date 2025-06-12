from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from core.mixins import DonorRequiredMixin, OrganisationOwnerRequiredMixin
from accounts.models import CustomUser
from .models import Campaign, Organisation, Donation
from .forms import CampaignForm, DonationForm


class CampaignListView(ListView):
    model = Campaign
    template_name = 'funding/campaign_list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        return Campaign.objects.filter(status='active').order_by('-created_at')


class CampaignDetailView(DetailView):
    model = Campaign
    template_name = 'funding/campaign_detail.html'
    context_object_name = 'campaign'

    def get_queryset(self):
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

        return redirect('funding:campaign_detail', pk=campaign.pk)


class CampaignCreateView(OrganisationOwnerRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'funding/campaign_form.html'

    def form_valid(self, form):
        campaign = form.save(commit=False)
        campaign.organisation = self.request.user.organisation
        campaign.creator = self.request.user
        campaign.save()
        messages.success(self.request, f'Your campaign "{campaign.title}" has been submitted and is pending review.')
        return redirect(reverse_lazy('org_dashboard'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Campaign'
        if self.request.user.is_authenticated and isinstance(self.request.user, CustomUser) and self.request.user.organisation:
            context['organisation_name'] = self.request.user.organisation.name
        return context


<<<<<<< HEAD
=======
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

>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
class DonorDashboardView(LoginRequiredMixin, DonorRequiredMixin, ListView):
    model = Donation
    template_name = 'funding/donor_dashboard.html'
    context_object_name = 'donations'

    def get_queryset(self):
<<<<<<< HEAD
        # Return all donations made by the current user, ordered by most recent.
=======
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
        return Donation.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
<<<<<<< HEAD
        context['page_title'] = 'My Donations'
=======
        context['page_title'] = 'My Donor Dashboard'
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
        return context


class OrgDashboardView(LoginRequiredMixin, OrganisationOwnerRequiredMixin, ListView):
<<<<<<< HEAD
=======
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.request.user.organisation

        # KPI Calculations
        total_raised = Donation.objects.filter(campaign__organisation=org).aggregate(Sum('amount'))['amount__sum'] or 0
        active_campaigns = Campaign.objects.filter(organisation=org, status='active').count()
        total_donors = Donation.objects.filter(campaign__organisation=org).values('user').distinct().count()

        context['page_title'] = 'My Organisation Dashboard'
        context['organisation'] = org
        context['kpis'] = {
            'total_raised': total_raised,
            'active_campaigns': active_campaigns,
            'total_donors': total_donors,
        }
        return context
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
    model = Campaign
    template_name = 'funding/org_dashboard.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
<<<<<<< HEAD
        # Return all campaigns associated with the user's organisation,
        # annotated with the total amount raised.
=======
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
        return Campaign.objects.filter(
            organisation=self.request.user.organisation
        ).annotate(
            total_raised=Coalesce(Sum('donations__amount'), Value(0))
        ).order_by('-created_at')

<<<<<<< HEAD
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organisation = self.request.user.organisation
        campaigns = context['campaigns']

        # KPI Calculations
        total_raised = campaigns.aggregate(total=Sum('total_raised'))['total'] or 0
        campaign_count = campaigns.count()
        
        # Get unique donor count
        unique_donors_count = CustomUser.objects.filter(
            donations__campaign__organisation=organisation
        ).distinct().count()

        context['page_title'] = f'{organisation.name} Dashboard'
        context['organisation'] = organisation
        context['total_raised'] = total_raised
        context['campaign_count'] = campaign_count
        context['unique_donors_count'] = unique_donors_count
        return context
=======
    
>>>>>>> b159ebea713ab9275604dd11ff8e712a671f3f30
