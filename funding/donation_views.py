from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, Http404
from django.db.models import Sum

from core.mixins import DonorRequiredMixin
from .models import Campaign, Organisation, Donation
from .forms import DonationForm

from utils.message_utils import add_success, add_error
from utils.constants import Messages

import uuid


class CreateDonationView(LoginRequiredMixin, DonorRequiredMixin, CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donation/create.html'
    
    def get_success_url(self):
        return reverse('donor:donation_detail', kwargs={
            'reference_number': self.object.reference_number
        })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign_id = self.kwargs.get('pk')
        campaign = get_object_or_404(Campaign, pk=campaign_id, status='active')
        
        # Add campaign details to context
        context['campaign'] = campaign
        
        # Calculate campaign progress
        donations = Donation.objects.filter(campaign=campaign)
        total_raised = donations.aggregate(total=Sum('amount'))['total'] or 0
        progress_percent = 0
        if campaign.funding_goal > 0:
            progress_percent = min(100, int((total_raised / campaign.funding_goal) * 100))
        
        context.update({
            'total_raised': total_raised,
            'progress_percent': progress_percent,
        })
        
        return context
    
    def form_valid(self, form):
        campaign_id = self.kwargs.get('pk')
        campaign = get_object_or_404(Campaign, pk=campaign_id, status='active')
        
        # Set donation attributes
        form.instance.campaign = campaign
        form.instance.donor = self.request.user
        form.instance.reference_number = str(uuid.uuid4())[:12].upper()
        
        response = super().form_valid(form)
        
        # Add success message
        add_success(self.request, Messages.DONATION_SUCCESS)
        return response


class DonationDetailView(DetailView):
    model = Donation
    context_object_name = 'donation'
    template_name = 'donation/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donation = self.get_object()
        
        # Calculate campaign progress
        donations = Donation.objects.filter(campaign=donation.campaign)
        total_raised = donations.aggregate(total=Sum('amount'))['total'] or 0
        progress_percent = 0
        if donation.campaign.funding_goal > 0:
            progress_percent = min(100, int((total_raised / donation.campaign.funding_goal) * 100))
        
        context.update({
            'total_raised': total_raised,
            'progress_percent': progress_percent,
        })
        
        return context
