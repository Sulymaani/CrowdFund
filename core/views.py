from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from funding.models import Organisation
from accounts.models import CustomUser # For role check
from .forms import OrganisationAdminReviewForm


class AdminOrganisationQueueView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Organisation
    template_name = 'core/admin_organisation_queue.html' # To be created
    context_object_name = 'pending_organisations'
    paginate_by = 20 # Optional: if the list can get long

    def test_func(self):
        """Allow access if user is_staff or has 'admin' role."""
        return self.request.user.is_staff or (isinstance(self.request.user, CustomUser) and self.request.user.role == 'admin')

    def get_queryset(self):
        """Return organisations with 'pending' verification status."""
        return Organisation.objects.filter(verification_status='pending').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Organisation Verification Queue'
        return context


class AdminOrganisationReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organisation
    form_class = OrganisationAdminReviewForm
    template_name = 'core/admin_organisation_review.html' # To be created
    context_object_name = 'organisation'
    success_url = reverse_lazy('core_admin:admin_organisation_queue')

    def test_func(self):
        """Allow access if user is_staff or has 'admin' role."""
        return self.request.user.is_staff or (isinstance(self.request.user, CustomUser) and self.request.user.role == 'admin')

    def get_queryset(self):
        """Admins can review any organisation, but typically this view is accessed for pending ones."""
        # No specific filtering here, pk from URL determines the object.
        # Could filter to ensure only non-verified are directly editable if desired, but form controls status.
        return super().get_queryset()

    def form_valid(self, form):
        messages.success(self.request, f'Organisation "{self.object.name}" has been updated successfully.')
        # The model's save() method handles updating the 'verified' boolean field based on 'verification_status'.
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Review Application: {self.object.name}'
        # We can also pass the original applicant's details if available and needed
        # For example, if the CustomUser who submitted it is linked directly or via a signal
        applicant = CustomUser.objects.filter(organisation=self.object, role='org_owner').first()
        context['applicant'] = applicant
        return context

