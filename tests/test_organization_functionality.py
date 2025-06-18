"""
Unit and integration tests for organization-related functionality.

Tests the complete organization experience flow from registration through dashboard,
campaign management, donation tracking, and organization settings.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta

from accounts.forms import OrganisationRegistrationForm
from accounts.models import CustomUser
from utils.constants import UserRoles
from tests.test_base import BaseCrowdFundTestCase
from campaigns.models import Campaign
from organizations.models import Organisation
from donations.models import Donation


class OrganizationAuthTest(BaseCrowdFundTestCase):
    """Test the organization registration and authentication process."""
    
    def test_organization_registration_form(self):
        """Test that organization registration form validates properly."""
        # Valid organization registration data
        org_data = {
            'email': 'neworg@example.com',
            'password1': 'SecurePassword123',
            'password2': 'SecurePassword123',
            'first_name': 'John',
            'last_name': 'Doe',
            'user_role': UserRoles.ORGANIZATION,
            'name': 'New Test Organization',
            'mission': 'Testing organization functionality',
            'website': 'https://testorg.example.com',
            'contact_phone': '+1234567890',
        }
        
        # Create the form
        form = OrganisationRegistrationForm(data=org_data)
        self.assertTrue(form.is_valid())
    
    def test_organization_login(self):
        """Test that organization can log in."""
        # Login data
        login_data = {
            'username': self.organisation_user.email,
            'password': 'password123',
        }
        
        # Submit login form
        response = self.client.post(
            reverse('accounts:login'),
            data=login_data,
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'], self.organisation_user)


class OrganizationDashboardTest(BaseCrowdFundTestCase):
    """Test organization dashboard functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create test campaigns
        self.campaign1 = self._create_campaign(
            title="Test Campaign 1",
            description="A test campaign for donations",
            funding_goal=10000,
            organisation=self.organisation,
            status='active'
        )
        
        self.campaign2 = self._create_campaign(
            title="Test Campaign 2",
            description="Another test campaign",
            funding_goal=5000,
            organisation=self.organisation,
            status='pending'
        )
        
        # Create test donations
        self.donation1 = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign1,
            amount=100,
            reference_number='ORG001',
            created_at=timezone.now() - timedelta(days=5)
        )
        
        self.donation2 = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign1,
            amount=50,
            reference_number='ORG002',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        # Login as organization
        self._login_user('organisation_user')
    
    def test_org_dashboard_access(self):
        """Test that organization can access their dashboard."""
        response = self.client.get(reverse('organizations:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'organizations/dashboard.html')
        
        # Check context data
        self.assertEqual(response.context['organisation'], self.organisation)
        self.assertIn('active_campaigns', response.context)
        self.assertIn('pending_campaigns', response.context)
        self.assertIn('recent_donations', response.context)
        self.assertIn('total_raised', response.context)
        
        # Check that campaign and donation information is displayed
        self.assertContains(response, 'Test Campaign 1')
        self.assertContains(response, 'Test Campaign 2')
        self.assertContains(response, '$150')  # Total donations


class OrganizationCampaignTest(BaseCrowdFundTestCase):
    """Test organization campaign management functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Login as organization
        self._login_user('organisation_user')
        
        # Create a test campaign
        self.campaign = self._create_campaign(
            title="Campaign To Manage",
            description="Test campaign for management functions",
            funding_goal=10000,
            organisation=self.organisation,
            status='active'
        )
    
    def test_campaign_detail_view(self):
        """Test viewing campaign details."""
        response = self.client.get(
            reverse('campaigns:org_detail', kwargs={'pk': self.campaign.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertIn('campaign', response.context)
        self.assertEqual(response.context['campaign'], self.campaign)
        
        # Check content
        self.assertContains(response, 'Campaign To Manage')
        self.assertContains(response, 'Test campaign for management functions')
        self.assertContains(response, '$10,000')
    
    def test_campaign_close(self):
        """Test closing a campaign."""
        response = self.client.post(
            reverse('campaigns:close', kwargs={'pk': self.campaign.pk}),
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that campaign status was updated
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, 'closed')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("campaign" in str(msg).lower() and "closed" in str(msg).lower() for msg in messages),
            "Campaign closed success message should be displayed"
        )


class OrganizationSettingsTest(BaseCrowdFundTestCase):
    """Test organization settings functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Login as organization
        self._login_user('organisation_user')
    
    def test_org_settings_view(self):
        """Test accessing organization settings page."""
        response = self.client.get(reverse('organizations:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'organizations/settings.html')
        
        # Check that form is in context
        self.assertIn('form', response.context)
        self.assertEqual(response.context['organisation'], self.organisation)
    
    def test_org_settings_update(self):
        """Test updating organization settings."""
        # Settings update data
        org_data = {
            'name': 'Updated Organization Name',
            'mission': 'Updated mission statement',
            'website': 'https://updated-org.example.com',
            'contact_phone': '+9876543210',
        }
        
        # Submit settings form
        response = self.client.post(
            reverse('organizations:settings'),
            data=org_data,
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that organization was updated
        self.organisation.refresh_from_db()
        self.assertEqual(self.organisation.name, 'Updated Organization Name')
        self.assertEqual(self.organisation.mission, 'Updated mission statement')
        self.assertEqual(self.organisation.website, 'https://updated-org.example.com')
        self.assertEqual(self.organisation.contact_phone, '+9876543210')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("organization" in str(msg).lower() and "updated" in str(msg).lower() for msg in messages),
            "Organization update success message should be displayed"
        )


class OrganizationDonationManagementTest(BaseCrowdFundTestCase):
    """Test organization donation management functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create test campaign
        self.campaign = self._create_campaign(
            title="Donation Test Campaign",
            description="A campaign for testing donation management",
            funding_goal=10000,
            organisation=self.organisation,
            status='active'
        )
        
        # Create test donations
        self.donation1 = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign,
            amount=100,
            reference_number='DONATE001',
            created_at=timezone.now() - timedelta(days=5)
        )
        
        self.donation2 = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign,
            amount=50,
            reference_number='DONATE002',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        # Login as organization
        self._login_user('organisation_user')
    
    def test_org_donations_list_view(self):
        """Test that organization can view their donation list."""
        response = self.client.get(reverse('donations:org_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check that donations are displayed
        self.assertContains(response, 'DONATE001')
        self.assertContains(response, 'DONATE002')
        self.assertContains(response, '$100')
        self.assertContains(response, '$50')
    
    def test_org_donation_detail_view(self):
        """Test that organization can view donation details."""
        response = self.client.get(
            reverse('donations:org_detail', kwargs={'pk': self.donation1.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        # Check context data and content
        self.assertIn('donation', response.context)
        self.assertEqual(response.context['donation'], self.donation1)
        self.assertContains(response, 'DONATE001')
        self.assertContains(response, '$100')
        self.assertContains(response, self.donor_user.email)
    
    def test_export_donations_csv(self):
        """Test export donations to CSV."""
        response = self.client.get(reverse('organizations:export_donations'))
        self.assertEqual(response.status_code, 200)
        
        # Check response headers
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
        
        # Check CSV content (basic check)
        content = response.content.decode('utf-8')
        self.assertIn('Reference', content)
        self.assertIn('Date', content)
        self.assertIn('Campaign', content)
        self.assertIn('Donor Name', content)
        self.assertIn('Amount', content)