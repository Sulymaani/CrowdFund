"""
Unit and integration tests for donor-related functionality.

Tests the complete donor experience flow from registration through dashboard,
profile management, campaign/organization browsing, and donation actions.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta

from accounts.forms import DonorRegistrationForm, ProfileEditForm
from accounts.models import CustomUser
from utils.constants import UserRoles
from tests.test_base import BaseCrowdFundTestCase, APITestCase
from campaigns.models import Campaign
from organizations.models import Organisation
from donations.models import Donation


class DonorAuthTest(BaseCrowdFundTestCase):
    """Test the donor registration process."""
    
    def test_donor_registration_form(self):
        """Test the DonorRegistrationForm validation."""
        # Valid form data
        form_data = {
            'username': 'newdonor',
            'email': 'newdonor@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123',
            'first_name': 'New',
            'last_name': 'Donor'
        }
        
        form = DonorRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form and check user properties
        user = form.save()
        self.assertEqual(user.role, UserRoles.DONOR)
        self.assertEqual(user.email, 'newdonor@example.com')
        self.assertTrue(user.check_password('securepass123'))
    
    def test_donor_registration_view(self):
        """Test the donor registration view."""
        # Registration data
        registration_data = {
            'username': 'testdonor',
            'email': 'testdonor@example.com',
            'password1': 'securepassword',
            'password2': 'securepassword',
            'first_name': 'Test',
            'last_name': 'Donor'
        }
        
        # Submit the registration form
        response = self.client.post(
            reverse('accounts:register_donor'),
            data=registration_data,
            follow=True
        )
        
        # Check that the user was created
        self.assertTrue(
            response.wsgi_request.user.is_authenticated,
            "User should be authenticated after registration"
        )
        
        # Check that user has donor role
        self.assertEqual(
            response.wsgi_request.user.role, 
            UserRoles.DONOR,
            "User should have donor role"
        )
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("registered successfully" in str(msg) for msg in messages),
            "Registration success message should be displayed"
        )
        
        # Check redirect to donor dashboard
        self.assertRedirects(
            response,
            reverse('donor:dashboard'),
            msg_prefix="User should be redirected to donor dashboard"
        )


class DonorProfileTest(BaseCrowdFundTestCase):
    """Test donor profile functionality."""
    
    def setUp(self):
        super().setUp()
        # Ensure we're logged in as donor
        self._login_user('donor_user')
    
    def test_donor_profile_view(self):
        """Test accessing donor's profile page."""
        response = self.client.get(reverse('donor:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/donor/profile.html')
    
    def test_edit_profile_form(self):
        """Test editing donor's profile."""
        # New profile data
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Donor',
            'email': 'updated_donor@example.com'
        }
        
        # Submit the form
        response = self.client.post(
            reverse('donor:edit_profile'),
            data=profile_data,
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Refresh user from database
        self.donor_user.refresh_from_db()
        
        # Check that user data was updated
        self.assertEqual(self.donor_user.first_name, 'Updated')
        self.assertEqual(self.donor_user.last_name, 'Donor')
        self.assertEqual(self.donor_user.email, 'updated_donor@example.com')
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("profile has been updated" in str(msg) for msg in messages),
            "Profile update success message should be displayed"
        )


class DonorCampaignBrowsingTest(BaseCrowdFundTestCase):
    """Test donor campaign browsing functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create test campaigns
        self.campaign1 = self._create_campaign(
            title="Test Campaign 1",
            description="A test campaign for donations",
            goal=10000,
            organisation=self.organisation,
            status='active'
        )
        
        self.campaign2 = self._create_campaign(
            title="Test Campaign 2",
            description="Another test campaign",
            goal=5000,
            organisation=self.organisation,
            status='active'
        )
        
        # Login as donor
        self._login_user('donor_user')
    
    def test_donor_campaigns_view(self):
        """Test that donors can access the campaign browsing view."""
        response = self.client.get(reverse('donor:campaigns'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/donor/campaigns.html')
        
        # Check that both campaigns are displayed
        self.assertContains(response, 'Test Campaign 1')
        self.assertContains(response, 'Test Campaign 2')
    
    def test_donor_can_view_organizations(self):
        """Test that donors can browse organizations."""
        response = self.client.get(reverse('donor:organizations'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/donor/organizations.html')
        
        # Check that the test organization is displayed
        self.assertContains(response, self.organisation.name)


class DonorDonationTest(BaseCrowdFundTestCase):
    """Test donor donation functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create a test campaign
        self.campaign = self._create_campaign(
            title="Test Campaign",
            description="A test campaign for donations",
            funding_goal=10000,
            organisation=self.organisation,
            status='active'
        )
        
        # Login as donor
        self._login_user('donor_user')
    
    def test_donor_can_view_campaign_detail(self):
        """Test that donors can view campaign details."""
        response = self.client.get(
            reverse('campaigns:detail', kwargs={'slug': self.campaign.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Campaign')
    
    def test_donor_can_make_donation(self):
        """Test the donation process."""
        # Donation form data
        donation_data = {
            'amount': 100,
            'comment': 'Test donation comment'
        }
        
        # Submit donation form
        response = self.client.post(
            reverse('donations:create', kwargs={'campaign_id': self.campaign.id}),
            data=donation_data,
            follow=True
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Check that donation was created
        self.assertEqual(self.campaign.donations.count(), 1)
        donation = self.campaign.donations.first()
        self.assertEqual(donation.amount, 100)
        self.assertEqual(donation.donor, self.donor_user)
        self.assertEqual(donation.comment, 'Test donation comment')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("donation" in str(msg).lower() and "success" in str(msg).lower() for msg in messages),
            "Donation success message should be displayed"
        )
        
    def test_donor_can_view_receipt(self):
        """Test that donors can view donation receipts."""
        # Create a donation
        donation = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign,
            amount=50,
            reference_number='TEST123'
        )
        
        # Access the receipt
        response = self.client.get(
            reverse('donations:receipt', kwargs={'pk': donation.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donations/receipt.html')
        self.assertContains(response, 'TEST123')  # Check reference number is displayed
        self.assertContains(response, '$50')      # Check amount is displayed


class DonorDashboardTest(BaseCrowdFundTestCase):
    """Test donor dashboard functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create test campaigns
        self.campaign = self._create_campaign(
            title="Test Campaign",
            description="A test campaign for donations",
            funding_goal=10000,
            organisation=self.organisation,
            status='active'
        )
        
        # Create test donations
        self.donation1 = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign,
            amount=100,
            reference_number='TEST001',
            created_at=timezone.now() - timedelta(days=5)
        )
        
        self.donation2 = Donation.objects.create(
            donor=self.donor_user,
            campaign=self.campaign,
            amount=50,
            reference_number='TEST002',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        # Login as donor
        self._login_user('donor_user')
    
    def test_donor_dashboard_access(self):
        """Test that donors can access their dashboard."""
        response = self.client.get(reverse('donor:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/donor/dashboard.html')
    
    def test_dashboard_shows_recent_donations(self):
        """Test that dashboard displays recent donations."""
        response = self.client.get(reverse('donor:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check that donation information is displayed
        self.assertContains(response, 'TEST001')
        self.assertContains(response, 'TEST002')
        self.assertContains(response, '$100')
        self.assertContains(response, '$50')
        
        # Check that total donation amount is displayed
        self.assertContains(response, '$150')
        
    def test_dashboard_shows_supported_organizations(self):
        """Test that dashboard displays supported organizations."""
        response = self.client.get(reverse('donor:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check that organization information is displayed
        self.assertContains(response, self.organisation.name)
