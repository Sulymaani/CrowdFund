from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from .models import Organisation
from accounts.models import CustomUser # For finding organisation owner
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import UpdateView
from .forms import OrganisationAdminReviewForm
from django.http import HttpResponse
from accounts.decorators import role_required # For the test view
from accounts.models import CustomUser # For CustomUser model, not role constants here

class PendingOrgListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Organisation
    template_name = 'funding/admin/org_queue.html'
    context_object_name = 'pending_organisations'
    paginate_by = 10 # Optional: add pagination

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # We need to get the user who owns the organisation.
        # The Organisation model itself doesn't directly link to the owner user.
        # The CustomUser model has an 'organisation' ForeignKey.
        # We can iterate through users or prefetch related if needed, but for now, 
        # let's just list organisations. The template can then find the owner.
        return Organisation.objects.filter(verification_status='pending').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Pending Organisation Applications'
        # To display owner username, we might need to adjust how data is passed or queried.
        # For now, the template will have to look up the user or we adjust the queryset later.
        # A simple way in template (if only one owner per org): org.customuser_set.first.username
        return context


class OrgReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Organisation
    form_class = OrganisationAdminReviewForm
    template_name = 'funding/admin/org_review.html'
    context_object_name = 'organisation'
    success_url = reverse_lazy('funding:admin_org_queue')

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Review Application: {self.object.name}"
        # Find the user who submitted this organisation, if any
        # This assumes CustomUser.organisation is a ForeignKey or OneToOne to Organisation
        owner = CustomUser.objects.filter(organisation=self.object).first()
        context['applicant_user'] = owner
        return context

    def form_valid(self, form):
        original_status = self.get_object().get_verification_status_display()
        organisation = form.save(commit=False)
        
        # Mirror verification_status to boolean verified field
        if organisation.verification_status == 'verified':
            organisation.verified = True
        elif organisation.verification_status == 'rejected':
            organisation.verified = False
        # 'pending' status should not be set by this form, but if it were, verified would remain False or as is.
        
        organisation.save()
        
        new_status = organisation.get_verification_status_display()
        messages.success(
            self.request, 
            f"Organisation '{organisation.name}' status changed from {original_status} to {new_status}."
        )
        return super().form_valid(form)


@role_required('org_owner')
def org_owner_test_view(request):
    """A simple view accessible only by verified org owners."""
    return HttpResponse("Org Owner Test View Accessed", status=200)
