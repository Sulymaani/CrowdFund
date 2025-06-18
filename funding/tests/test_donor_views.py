from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from funding.models import Donation, Campaign, Organisation
from accounts.models import CustomUser
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class DonorViewsTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.donor_user = CustomUser.objects.create_user(
            username='testdonor',
            email='donor@test.com',
            password='testpassword',
            role='donor'
        )
        
        self.org_owner = CustomUser.objects.create_user(
            username='testorg',
            email='org@test.com',
            password='testpassword',
            role='org_owner'
        )
        
        # Create test organization
        self.organisation = Organisation.objects.create(
            name='Test Organisation',
            description='Test Description',
            owner=self.org_owner,
            status='approved'
        )
        self.org_owner.organisation = self.organisation
        self.org_owner.save()
        
        # Create test campaign
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test Campaign Description',
            goal=Decimal('5000.00'),
            status='active',
            organisation=self.organisation,
            creator=self.org_owner
        )
        
        # Create test donations
        self.donation1 = Donation.objects.create(
            campaign=self.campaign,
            user=self.donor_user,
            amount=Decimal('100.00'),
            created_at=timezone.now() - timedelta(days=5)
        )
        
        self.donation2 = Donation.objects.create(
            campaign=self.campaign,
            user=self.donor_user,
            amount=Decimal('50.00'),
            created_at=timezone.now()
        )
        
        self.client = Client()

    def test_donor_dashboard_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertTrue('/login/' in response.url)

    def test_donor_dashboard_authenticated_but_not_donor(self):
        """Test that authenticated non-donor users can't access donor dashboard"""
        self.client.login(username='testorg', password='testpassword')
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_donor_dashboard_authenticated_donor(self):
        """Test that authenticated donor users can access donor dashboard"""
        self.client.login(username='testdonor', password='testpassword')
        response = self.client.get(reverse('donor_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_donor_dashboard_context(self):
        """Test that donor dashboard context contains the expected data"""
        self.client.login(username='testdonor', password='testpassword')
        response = self.client.get(reverse('donor_dashboard'))
        
        # Check page title and breadcrumbs
        self.assertEqual(response.context['page_title'], 'My Donations')
        self.assertIn('breadcrumbs', response.context)
        self.assertEqual(len(response.context['breadcrumbs']), 1)
        self.assertEqual(response.context['breadcrumbs'][0]['title'], 'My Donations')
        
        # Check summary metrics
        self.assertEqual(response.context['total_donated'], Decimal('150.00'))
        self.assertEqual(response.context['campaigns_supported'], 1)
        self.assertIsNotNone(response.context['last_donation_date'])
        
        # Check donations are returned in descending order (newest first)
        donations = list(response.context['donations'])
        self.assertEqual(len(donations), 2)
        self.assertEqual(donations[0], self.donation2)  # newest donation
        self.assertEqual(donations[1], self.donation1)  # older donation

    def test_donor_dashboard_template_content(self):
        """Test that donor dashboard template renders the expected content"""
        self.client.login(username='testdonor', password='testpassword')
        response = self.client.get(reverse('donor_dashboard'))
        
        content = response.content.decode('utf-8')
        
        # Check header elements
        self.assertIn('My Donations', content)
        self.assertIn('Manage your donation history', content)
        
        # Check summary cards
        self.assertIn('Total Donated', content)
        self.assertIn('$150.00', content)
        self.assertIn('Campaigns Supported', content)
        self.assertIn('1', content)  # One campaign supported
        
        # Check donation table headers
        self.assertIn('Campaign', content)
        self.assertIn('Amount', content)
        self.assertIn('Date', content)
        self.assertIn('Reference', content)
        
        # Check donation details
        self.assertIn('Test Campaign', content)  # Campaign title
        self.assertIn('$100.00', content)  # First donation amount
        self.assertIn('$50.00', content)  # Second donation amount
        self.assertIn('View Details', content)  # Action link text
