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

# Import from organizations app instead of accounts
from organizations.forms import OrganizationForm
from accounts.models import CustomUser
from utils.constants import UserRoles
from tests.test_base import BaseCrowdFundTestCase
from campaigns.models import Campaign
from organizations.models import Organisation
from donations.models import Donation


class OrganizationAuthTest(BaseCrowdFundTestCase):
    """Test the organization registration and login process."""
    
    def test_organization_registration_view(self):
        """Test the organization registration view."""
        # Registration data
        registration_data = {
            'username': 'neworg',
            'email': 'neworg@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'first_name': 'New',
            'last_name': 'Organization',
            'organization_name': 'New Test Organization',
            'website': 'https://newtestorg.com',
            'mission': 'New test organization mission'
        }
        
        # Submit the registration form
        response = self.client.post(
            reverse('accounts:register_organization'),
            data=registration_data,
            follow=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("registration" in str(msg).lower() and "success" in str(msg).lower() for msg in messages),
            "Registration success message should be displayed"
        )


class OrganizationCampaignTest(BaseCrowdFundTestCase):
    """Test organization campaign management functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Login as organization
        self._login_user('org_owner')
    
    def test_campaign_creation_form(self):
        """Test the campaign creation form."""
        # Campaign form data
        campaign_data = {
            'title': 'Test Campaign Creation',
            'description': 'A test campaign created through the form',
            'goal': 15000,
            'end_date': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'category': 'education'
        }
        
        # Submit the campaign form
        response = self.client.post(
            reverse('campaigns:create'),
            data=campaign_data,
            follow=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that campaign was created
        campaigns = Campaign.objects.filter(title='Test Campaign Creation')
        self.assertEqual(campaigns.count(), 1)
        
        campaign = campaigns.first()
        self.assertEqual(campaign.description, 'A test campaign created through the form')
        self.assertEqual(campaign.goal, 15000)
        self.assertEqual(campaign.organisation, self.organisation)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("campaign" in str(msg).lower() and "created" in str(msg).lower() for msg in messages),
            "Campaign creation success message should be displayed"
        )
    
    def test_campaign_list_view(self):
        """Test that organization can view their campaign list."""
        # Create test campaigns for this organization
        campaign1 = Campaign.objects.create(
            title="Org Test Campaign 1",
            description="First test campaign for org",
            goal=10000,
            organisation=self.organisation,
            status='active'
        )
        
        campaign2 = Campaign.objects.create(
            title="Org Test Campaign 2",
            description="Second test campaign for org",
            goal=5000,
            organisation=self.organisation,
            status='active'
        )
        
        # Access campaign list
        response = self.client.get(reverse('campaigns:org_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check that campaigns are listed
        self.assertContains(response, 'Org Test Campaign 1')
        self.assertContains(response, 'Org Test Campaign 2')
        self.assertContains(response, '$10,000')
        self.assertContains(response, '$5,000')
    
    def test_campaign_edit(self):
        """Test that organization can edit their campaigns."""
        # Create a campaign to edit
        campaign = Campaign.objects.create(
            title="Campaign to Edit",
            description="Original description",
            goal=5000,
            organisation=self.organisation,
            status='active'
        )
        
        # Updated campaign data
        updated_data = {
            'title': 'Updated Campaign Title',
            'description': 'Updated description text',
            'goal': 7500,
            'end_date': (timezone.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
        }
        
        # Submit the edit form
        response = self.client.post(
            reverse('campaigns:edit', kwargs={'pk': campaign.id}),
            data=updated_data,
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that campaign was updated
        campaign.refresh_from_db()
        self.assertEqual(campaign.title, 'Updated Campaign Title')
        self.assertEqual(campaign.description, 'Updated description text')
        self.assertEqual(campaign.goal, 7500)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("campaign" in str(msg).lower() and "updated" in str(msg).lower() for msg in messages),
            "Campaign updated success message should be displayed"
        )
    
    def test_campaign_deactivation(self):
        """Test that organization can deactivate their campaigns."""
        # Create a campaign to deactivate
        campaign = Campaign.objects.create(
            title="Campaign to Close",
            description="Will be deactivated",
            goal=5000,
            organisation=self.organisation,
            status='active'
        )
        
        # Request campaign deactivation
        response = self.client.post(
            reverse('campaigns:close', kwargs={'pk': campaign.id}),
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that campaign was deactivated
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'closed')
        
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
        self._login_user('org_owner')
    
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
        self.campaign = Campaign.objects.create(
            title="Donation Test Campaign",
            description="A campaign for testing donation management",
            goal=10000,
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
        self._login_user('org_owner')
    
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
