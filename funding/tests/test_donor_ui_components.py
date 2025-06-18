from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from funding.models import Campaign, Organisation, Tag, Donation
from decimal import Decimal
import tempfile
from PIL import Image
from io import BytesIO

User = get_user_model()

class DonorUIComponentsTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='donor'
        )
        
        # Create test organization
        self.org = Organisation.objects.create(
            name='Test Organisation',
            mission='Test description',
            website='https://org.example.com',
            contact_phone='1234567890'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='Education', slug='education')
        self.tag2 = Tag.objects.create(name='Health', slug='health')
        
        # Create test campaign
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            goal=Decimal('1000.00'),
            organisation=self.org,
            status='active'
        )
        self.campaign.tags.add(self.tag1, self.tag2)
        
        # Create test donation
        self.donation = Donation.objects.create(
            campaign=self.campaign,
            amount=Decimal('50.00'),
            user=self.user
        )
        
        # Client for testing
        self.client = Client()

    def test_breadcrumbs_component_rendering(self):
        """Test that the breadcrumbs component renders correctly"""
        context = {
            'home_url': reverse('home'),
            'home_title': 'Home',
            'breadcrumbs': [
                {'title': 'Campaigns', 'url': reverse('funding:campaign_list')},
                {'title': 'Test Campaign', 'url': ''}
            ]
        }
        
        rendered = render_to_string('components/breadcrumbs.html', context)
        
        # Check for expected content in the rendered HTML
        self.assertIn('Home', rendered)
        self.assertIn('Campaigns', rendered)
        self.assertIn('Test Campaign', rendered)
        self.assertIn(reverse('home'), rendered)
        self.assertIn(reverse('funding:campaign_list'), rendered)

    def test_campaign_card_component_rendering(self):
        """Test that the campaign card component renders correctly"""
        # Create a donation to simulate raised amount
        donation = Donation.objects.create(
            campaign=self.campaign,
            amount=500,
            user=self.user
        )
        
        context = {'campaign': self.campaign}
        rendered = render_to_string('components/campaign_card.html', context)
        
        # Check for expected content in the rendered HTML
        self.assertIn(self.campaign.title, rendered)
        self.assertIn(self.campaign.description[:100], rendered)  # Check partial description (truncated)
        self.assertIn('$1000.00', rendered)  # Goal
        self.assertIn('$500.00', rendered)  # Raised amount
        self.assertIn('50%', rendered)  # Progress percent
        
        # Check for tags
        self.assertIn('Education', rendered)
        self.assertIn('Health', rendered)
        
        # Check for status badge
        self.assertIn('Active', rendered)

    def test_donor_header_component_rendering(self):
        """Test that the donor header component renders correctly"""
        # Not logged in
        context = {'user': None}
        rendered = render_to_string('components/donor_header.html', context)
        
        # Check for expected content in the rendered HTML
        self.assertIn('CrowdFund', rendered)
        self.assertIn('Login', rendered)
        self.assertIn('Sign Up', rendered)
        self.assertNotIn('My Donations', rendered)  # Should not appear when not logged in
        
        # Logged in as donor
        self.client.login(username='testuser', password='testpassword')
        context = {'user': self.user}
        rendered = render_to_string('components/donor_header.html', context)
        
        # Check for expected content in the rendered HTML
        self.assertIn('My Donations', rendered)
        self.assertIn(self.user.first_name, rendered)

    def test_donor_footer_component_rendering(self):
        """Test that the donor footer component renders correctly"""
        context = {'user': self.user}
        rendered = render_to_string('components/donor_footer.html', context)
        
        # Check for expected content in the rendered HTML
        self.assertIn('About CrowdFund', rendered)
        self.assertIn('Quick Links', rendered)
        self.assertIn('Contact Us', rendered)
        self.assertIn('My Donations', rendered)  # Should appear when logged in as donor

    def test_campaign_list_with_components(self):
        """Test that the campaign list page renders with our components"""
        # Access the campaign list page
        response = self.client.get(reverse('funding:campaign_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check for our components in the rendered HTML
        content = response.content.decode('utf-8')
        self.assertIn('breadcrumbs.html', content)
        
        # Check that campaign data is included
        self.assertIn(self.campaign.title, content)
