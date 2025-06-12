from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import UpdateView

from accounts.decorators import role_required
from accounts.models import CustomUser
from core.mixins import StaffRequiredMixin

from .forms import CampaignAdminReviewForm
from .models import Campaign, Organisation


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'funding/admin/dashboard.html'

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
    template_name = 'funding/admin/campaign_queue.html'
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
    template_name = 'funding/admin/campaign_review.html'
    context_object_name = 'campaign'
    success_url = reverse_lazy('funding:admin_campaign_queue')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Review Campaign: {self.object.title}"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Campaign '{self.object.title}' has been reviewed and its status updated to {self.object.get_status_display()}."
        )
        return response


@role_required('org_owner')
def org_owner_test_view(request):
    """A simple view accessible only by verified org owners."""
    return HttpResponse("Org Owner Test View Accessed", status=200)
