from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, View
# CreateView is imported twice, once from django.views.generic and once from .edit - keep one
# from django.views.generic.edit import CreateView 
from django.contrib.auth.mixins import LoginRequiredMixin # UserPassesTestMixin is now in core.mixins
from core.mixins import DonorRequiredMixin, OrganisationOwnerRequiredMixin, PublicOrNonOrgOwnerRequiredMixin

from accounts.models import CustomUser
from .models import Campaign, Organisation, Donation
from .forms import CampaignForm, DonationForm

class CampaignListView(ListView):
    model = Campaign
    template_name = 'funding/home.html'  # Will be created later
    context_object_name = 'campaigns'

    def get_queryset(self):
        return Campaign.objects.filter(status='active').order_by('-created_at')

class CampaignDetailView(DetailView):
    model = Campaign
    template_name = 'funding/campaign_detail.html' # Will be created later
    context_object_name = 'campaign'

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

        # Rule #4: Only donors should see the donation form.
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
    template_name = 'funding/campaign_form.html' # To be created
    # success_url will be set in get_success_url or form_valid

    # test_func is now handled by VerifiedOrgOwnerRequiredMixin

    def get_form_kwargs(self):
        """Hide the organisation field as it's set automatically."""
        kwargs = super().get_form_kwargs()
        # If the user's organisation is set, we can remove the field from the form
        # or make it disabled. For now, we'll rely on form_valid to set it.
        # To hide it, we would modify the form class or fields in get_form.
        return kwargs

    def get_initial(self):
        """Pre-select the user's organisation."""
        initial = super().get_initial()
        if self.request.user.is_authenticated and hasattr(self.request.user, 'organisation') and self.request.user.organisation:
            initial['organisation'] = self.request.user.organisation
        return initial

    def form_valid(self, form):
        campaign = form.save(commit=False)
        campaign.organisation = self.request.user.organisation # Assign user's organisation
        campaign.creator = self.request.user # Assign the logged-in user as the creator
        # 'status' defaults to 'pending' as per Campaign model definition
        campaign.save()
        messages.success(self.request, f'Your campaign "{campaign.title}" has been submitted and is pending review.')
        return redirect(reverse_lazy('funding:campaign_detail', kwargs={'pk': campaign.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Campaign'
        if self.request.user.is_authenticated and isinstance(self.request.user, CustomUser) and self.request.user.organisation:
            context['organisation_name'] = self.request.user.organisation.name
        return context


class DonorDashboardView(LoginRequiredMixin, DonorRequiredMixin, ListView):
    model = Donation
    template_name = 'funding/donor_dashboard.html'
    context_object_name = 'donations'

    def get_queryset(self):
        # Return all donations made by the current user, ordered by most recent.
        return Donation.objects.filter(user=self.request.user).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Donations'
        return context


class OrgDashboardView(LoginRequiredMixin, OrganisationOwnerRequiredMixin, ListView):
    model = Campaign
    template_name = 'funding/org_dashboard.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        # Return all campaigns associated with the user's organisation,
        # annotated with the total amount raised.
        return Campaign.objects.filter(
            organisation=self.request.user.organisation
        ).annotate(
            total_raised=Coalesce(Sum('donations__amount'), Value(0))
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Organisation Campaigns'
        context['organisation'] = self.request.user.organisation
        return context
