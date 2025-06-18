"""
Template isolation test to find recursion issues
"""
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.template import Context, Template
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from funding.models import Campaign, Organisation, Tag, Donation
from decimal import Decimal
from django.conf import settings

User = get_user_model()

class TemplateIsolationTests(TestCase):
    def setUp(self):
        # Minimal setup - create essential objects for testing
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword',
            email='test@example.com', 
            role='donor'
        )
        
        self.org = Organisation.objects.create(
            name='Test Organisation',
            mission='Test description'
        )
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            goal=Decimal('1000.00'),
            organisation=self.org,
            status='active'
        )
        
        # Create test donation
        self.donation = Donation.objects.create(
            campaign=self.campaign,
            amount=Decimal('50.00'),
            user=self.user,
            reference_number='TEST-REF-001'
        )
        
        # Set up important metrics for the campaign
        self.campaign.progress_percentage = 5  # Direct attribute rather than calculated
        self.campaign.raised_amount = Decimal('50.00')
        
        self.client = Client()
        self.factory = RequestFactory()

    def test_isolated_template_render(self):
        """Test each template component in isolation to identify recursion issues"""
        # Set up minimal context
        context = {
            'campaign': self.campaign,
            'user': self.user
        }
        
        print("\n--- Testing campaign_card.html in isolation ---")
        try:
            rendered = render_to_string('components/campaign_card.html', context)
            print("✅ campaign_card.html renders successfully")
        except RecursionError:
            print("❌ RecursionError in campaign_card.html")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n--- Testing donor_header.html in isolation ---")
        try:
            context = {'user': self.user}
            rendered = render_to_string('components/donor_header.html', context)
            print("✅ donor_header.html renders successfully")
        except RecursionError:
            print("❌ RecursionError in donor_header.html")
        except Exception as e:
            print(f"❌ Error: {e}")

    def test_campaign_list_view_without_test_client(self):
        """Test the campaign list view without using Django's test client"""
        # Create a request manually 
        request = self.factory.get(reverse('funding:campaign_list'))
        request.user = self.user
        
        # Import the view directly
        from funding.views import CampaignListView
        
        try:
            # Instantiate and call the view directly to bypass test client's context copying
            view = CampaignListView()
            view.setup(request)
            response = view.get(request)
            
            # Don't use assertContains to avoid test client context copying
            self.assertEqual(response.status_code, 200)
            print("\n✅ CampaignListView renders successfully without test client")
        except RecursionError as e:
            print(f"\n❌ RecursionError in CampaignListView: {e}")
            self.fail("RecursionError in CampaignListView")
        except Exception as e:
            print(f"\n❌ Error in CampaignListView: {e}")
            self.fail(f"Error in CampaignListView: {e}")
            
    def test_direct_render_to_string(self):
        """Test direct render_to_string with realistic but minimal context"""
        # Create minimal context similar to what would be in the real view
        context = {
            'campaigns': [self.campaign],
            'user': self.user,
            'is_impersonating': False,
            'messages': [],
            'request': self.factory.get(reverse('funding:campaign_list')),
        }
        
        try:
            # Try to render the template directly
            rendered = render_to_string('campaign_list.html', context)
            print("\n✅ Direct render_to_string of campaign_list.html succeeds")
        except RecursionError as e:
            print(f"\n❌ RecursionError in direct render_to_string: {e}")
            self.fail("RecursionError in direct render_to_string")
        except Exception as e:
            print(f"\n❌ Error in direct render_to_string: {e}")
            self.fail(f"Error in direct render_to_string: {e}")
