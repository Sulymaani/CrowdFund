from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, View
# CreateView is imported twice, once from django.views.generic and once from .edit - keep one
# from django.views.generic.edit import CreateView 
from django.contrib.auth.mixins import LoginRequiredMixin # UserPassesTestMixin is now in core.mixins
from core.mixins import VerifiedOrgOwnerRequiredMixin, OrganisationOwnerRequiredMixin, PublicOrNonOrgOwnerRequiredMixin # Assuming OrganisationApplicationCreateView might use OrganisationOwnerRequiredMixin

from accounts.models import CustomUser
from .models import Campaign, Organisation, Donation
from .forms import OrganisationApplicationForm, CampaignForm, DonationForm

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
        context['donation_form'] = DonationForm()
        return context

class OrganisationCreateView(CreateView):
    model = Organisation
    template_name = 'funding/organisation_form.html' # Will be created later
    fields = ['name'] # 'verified' defaults to False, 'created_at' is auto_now_add
    success_url = reverse_lazy('campaign_list') # Redirect to campaign list after successful creation

    def form_valid(self, form):
        # verified is False by default as per model definition
        return super().form_valid(form)


class CreateDonationView(LoginRequiredMixin, View):
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


class OrganisationApplicationCreateView(PublicOrNonOrgOwnerRequiredMixin, CreateView):
    model = Organisation
    form_class = OrganisationApplicationForm
    template_name = 'funding/organisation_apply.html' # To be created
    success_url = reverse_lazy('funding:campaign_list') # Redirect to campaign list
    login_url = reverse_lazy('login') # Explicitly define login_url for LoginRequiredMixin

    # Access control is now handled by PublicOrNonOrgOwnerRequiredMixin.

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.info(self.request, "You are already associated with an organisation or have an application pending.")
            return redirect('funding:campaign_list')
        return super().handle_no_permission() # For unauthenticated, redirects to login_url

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # verification_status defaults to 'pending' as per model definition.
        # The 'verified' boolean field will be set by the model's save() method.
        self.object.save() # Save the organisation first to get an ID

        if self.request.user.is_authenticated and isinstance(self.request.user, CustomUser):
            user = self.request.user
            user.role = 'org_owner' # Directly use the string value for the role
            user.organisation = self.object
            user.save()
            messages.success(self.request, 
                             f'Thank you, {user.username}! Your organisation application for "{self.object.name}" has been submitted and is pending review. You have been assigned as the Organisation Owner.')
        else:
            messages.success(self.request, 
                             f'Your organisation application for "{self.object.name}" has been submitted and is pending review.')
        
        return redirect(self.get_success_url()) # Use redirect after manual save and messages

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Apply for Organisation'
        return context


class CampaignCreateView(VerifiedOrgOwnerRequiredMixin, CreateView):
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
        """Pre-select the user's organisation if applicable."""
        initial = super().get_initial()
        if self.request.user.is_authenticated and isinstance(self.request.user, CustomUser) and self.request.user.organisation:
            # The form's ModelChoiceField queryset already filters for verified orgs.
            # If the user's org is verified, it will be a valid choice.
            initial['organisation'] = self.request.user.organisation
        return initial

    def form_valid(self, form):
        campaign = form.save(commit=False)
        campaign.organisation = self.request.user.organisation # Assign user's verified org
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
