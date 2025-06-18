from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Count, Sum, Q, Max, Subquery, OuterRef
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, View, UpdateView, DeleteView

from accounts.decorators import role_required
from accounts.models import CustomUser
from core.mixins import StaffRequiredMixin

from .forms import CampaignAdminReviewForm
from .models import Campaign, Donation, Organisation


class AdminActiveCampaignsListView(StaffRequiredMixin, ListView):
    model = Campaign
    template_name = 'admin_dashboard/active_campaigns.html'
    context_object_name = 'campaigns'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(status='active').select_related('organisation', 'creator').order_by('-created_at')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(organisation__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Active Campaigns'
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AdminOrganisationsListView(StaffRequiredMixin, ListView):
    model = Organisation
    template_name = 'admin_dashboard/organisations.html'
    context_object_name = 'organisations'
    paginate_by = 20

    def get_queryset(self):
        owner_username_subquery = CustomUser.objects.filter(
            organisation=OuterRef('pk'), role='org_owner'
        ).values('username')[:1]

        owner_id_subquery = CustomUser.objects.filter(
            organisation=OuterRef('pk'), role='org_owner'
        ).values('id')[:1]

        queryset = super().get_queryset().annotate(
            campaign_count=Count('campaigns', distinct=True),
            total_raised=Sum('campaigns__donations__amount', default=0),
            owner_username=Subquery(owner_username_subquery),
            owner_id=Subquery(owner_id_subquery)
        ).order_by('-created_at')

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(owner_username__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manage Organisations'
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AdminDonorsListView(StaffRequiredMixin, ListView):
    model = CustomUser
    template_name = 'admin_dashboard/donors.html'
    context_object_name = 'donors'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(role='donor').annotate(
            total_donated=Sum('donations__amount', default=0),
            last_donation=Max('donations__created_at')
        ).order_by('-last_donation')

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Manage Donors'
        context['search_query'] = self.request.GET.get('q', '')
        return context



class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'admin_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Admin Dashboard'
        context['pending_campaigns_count'] = Campaign.objects.filter(status='pending').count()
        context['active_campaigns_count'] = Campaign.objects.filter(status='active').count()
        context['total_organisations_count'] = Organisation.objects.count()
        context['total_donors_count'] = CustomUser.objects.filter(role='donor').count()
        return context


class AdminCampaignQueueListView(StaffRequiredMixin, ListView):
    model = Campaign
    template_name = 'admin_dashboard/campaign_queue.html'
    context_object_name = 'pending_campaigns'
    paginate_by = 10

    def get_queryset(self):
        return Campaign.objects.filter(status='pending').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Pending Campaign Submissions'
        return context


class AdminCampaignReviewView(StaffRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignAdminReviewForm
    template_name = 'admin_dashboard/campaign_review.html'
    context_object_name = 'campaign'
    success_url = reverse_lazy('core_admin:admin_campaign_queue')

    def dispatch(self, request, *args, **kwargs):
        # Capture where user came from for back navigation
        self.back_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or reverse('core_admin:admin_campaign_queue')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Review Campaign: {self.object.title}"
        context['back_url'] = self.back_url
        return context

    def get_success_url(self):
        return self.back_url

    def form_valid(self, form):
        # Save the form and update the campaign instance
        response = super().form_valid(form)

        # Get the new status and title for the message
        new_status = self.object.status
        campaign_title = self.object.title

        if new_status == 'active':
            messages.success(
                self.request,
                f"Campaign '{campaign_title}' has been approved and is now active."
            )
        elif new_status == 'rejected':
            messages.warning(
                self.request,
                f"Campaign '{campaign_title}' has been rejected."
            )
        else:
            # Fallback for any other status changes
            messages.info(
                self.request,
                f"Campaign '{campaign_title}' status has been updated to '{self.object.get_status_display()}'.."
            )

        return response


class AdminMetricsSummaryView(StaffRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = {
            'pending_campaigns_count': Campaign.objects.filter(status='pending').count(),
            'active_campaigns_count': Campaign.objects.filter(status='active').count(),
            'total_organisations_count': Organisation.objects.count(),
            'total_donors_count': CustomUser.objects.filter(role='donor').count(),
        }
        return JsonResponse(data)


@role_required('org_owner')
def org_owner_test_view(request):
    """A simple view accessible only by verified org owners."""
    return HttpResponse("Org Owner Test View Accessed", status=200)


class AdminToggleOrganisationActiveView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        org = get_object_or_404(Organisation, pk=self.kwargs['pk'])
        org.is_active = not org.is_active
        org.save()

        action = "activated" if org.is_active else "deactivated"
        messages.success(self.request, f'Organisation "{org.name}" has been {action}.')
        
        return redirect(reverse('core_admin:admin_organisations'))


class AdminOrganisationDeleteView(StaffRequiredMixin, DeleteView):
    model = Organisation
    template_name = 'admin_dashboard/organisation_confirm_delete.html'
    success_url = reverse_lazy('core_admin:admin_organisations')

    def form_valid(self, form):
        messages.success(self.request, f'Organisation "{self.object.name}" has been successfully deleted.')
        return super().form_valid(form)


class ImpersonateOrgOwnerView(StaffRequiredMixin, View):
    def get(self, request, user_id):
        if 'impersonator_id' in request.session:
            messages.error(request, "You are already impersonating a user. Stop impersonating first.")
            return redirect('core_admin:admin_organisations')

        try:
            target_user = CustomUser.objects.get(id=user_id, role='org_owner')
            request.session['impersonator_id'] = request.user.id
            login(request, target_user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"You are now logged in as {target_user.username}.")
            return redirect('org_dashboard')
        except CustomUser.DoesNotExist:
            messages.error(request, "The selected user is not a valid organisation owner.")
            return redirect('core_admin:admin_organisations')


class StopImpersonationView(View):
    def get(self, request):
        impersonator_id = request.session.pop('impersonator_id', None)
        if not impersonator_id:
            messages.error(request, "You are not currently impersonating anyone.")
            return redirect('core_admin:dashboard')

        try:
            impersonator = CustomUser.objects.get(id=impersonator_id)
            login(request, impersonator, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "You have stopped impersonating and are logged back in as yourself.")
        except CustomUser.DoesNotExist:
            messages.error(request, "Could not log you back in. Please log out and log in again.")
            return redirect('login')

        return redirect('core_admin:admin_organisations')
