from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden, Http404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q, F

from core.mixins import DonorRequiredMixin
from .models import Campaign, Organisation, Donation
from .forms import DonationForm

from utils.message_utils import add_success, add_error
from utils.constants import Messages


class DonorDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'donor/dashboard.html'

    def test_func(self):
        return self.request.user.role == 'donor'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get recent donations by this donor
        recent_donations = Donation.objects.filter(
            donor=user
        ).order_by('-created_at')[:5]
        
        # Get donation stats
        total_donated = Donation.objects.filter(donor=user).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get a list of organizations this donor has supported
        supported_orgs = Organisation.objects.filter(
            campaigns__donations__donor=user
        ).distinct()
        
        context.update({
            'recent_donations': recent_donations,
            'total_donated': total_donated,
            'donation_count': recent_donations.count(),
            'supported_orgs': supported_orgs,
        })
        return context


class DonorCampaignsView(LoginRequiredMixin, DonorRequiredMixin, ListView):
    model = Campaign
    template_name = 'donor/campaigns.html'
    context_object_name = 'campaigns'
    paginate_by = 12
    
    def get_queryset(self):
        # Show only active campaigns for donors
        return Campaign.objects.filter(status='active').order_by('-created_at')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Browse Active Campaigns'
        return context


class DonorOrganizationsView(LoginRequiredMixin, DonorRequiredMixin, ListView):
    model = Organisation
    template_name = 'donor/organizations.html'
    context_object_name = 'organizations'
    paginate_by = 12
    
    def get_queryset(self):
        # Show only active organizations
        return Organisation.objects.filter(is_active=True).order_by('name')


class DonorDonationDetailView(LoginRequiredMixin, DonorRequiredMixin, DetailView):
    model = Donation
    context_object_name = 'donation'
    template_name = 'donor/donation_detail.html'
    slug_field = 'reference_number'
    slug_url_kwarg = 'reference_number'
    
    def get_queryset(self):
        # Donors can only see their own donations
        return Donation.objects.filter(donor=self.request.user)


class DonorProfileView(LoginRequiredMixin, DonorRequiredMixin, TemplateView):
    template_name = 'donor/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get donation history
        donations = Donation.objects.filter(donor=user).order_by('-created_at')
        
        # Calculate stats
        total_donated = donations.aggregate(Sum('amount'))['amount__sum'] or 0
        campaigns_count = donations.values('campaign').distinct().count()
        orgs_count = donations.values('campaign__organisation').distinct().count()
        
        context.update({
            'user': user,
            'donations': donations,
            'total_donated': total_donated,
            'campaigns_count': campaigns_count,
            'orgs_count': orgs_count,
        })
        
        return context
