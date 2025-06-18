from django.test import TestCase, Client
from django.template.loader import render_to_string
from django.template import Context

class MinimalTemplateTest(TestCase):
    def test_render_base_template(self):
        """Test if the base template renders without recursion error"""
        # Minimal context that mimics what base.html expects
        context = {
            'user': None,  # Simulate logged out state
            'messages': [],
            'is_impersonating': False
        }
        
        # Try to render just the base template
        try:
            rendered = render_to_string('base.html', context)
            self.assertTrue(len(rendered) > 0)
        except RecursionError:
            self.fail("base.html caused RecursionError")
    
    def test_render_campaign_card(self):
        """Test if campaign_card.html renders on its own"""
        from funding.models import Campaign, Organisation
        from decimal import Decimal
        
        # Create test organization
        org = Organisation.objects.create(
            name='Test Organisation',
            mission='Test description',
            website='https://org.example.com',
            contact_phone='1234567890'
        )
        
        # Create test campaign
        campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            goal=Decimal('1000.00'),
            organisation=org,
            status='active'
        )
        
        # Minimal context for campaign card
        context = {
            'campaign': campaign,
        }
        
        # Try to render just the simplified campaign card component
        try:
            rendered = render_to_string('components/campaign_card_simple.html', context)
            self.assertTrue(len(rendered) > 0)
            print("Simple campaign card renders successfully!")
        except RecursionError:
            self.fail("campaign_card_simple.html caused RecursionError")
            
    def test_campaign_card_issues(self):
        """Test to identify problematic parts of the original campaign card"""
        from funding.models import Campaign, Organisation
        from decimal import Decimal
        import traceback
        
        # Create test organization
        org = Organisation.objects.create(
            name='Test Organisation',
            mission='Test description',
            website='https://org.example.com',
            contact_phone='1234567890'
        )
        
        # Create test campaign
        campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            goal=Decimal('1000.00'),
            organisation=org,
            status='active'
        )
        
        # Try to render the original campaign card with debugging
        context = {
            'campaign': campaign,
            # Add debug context to prevent circular references
            'debug_mode': True,
        }
        
        try:
            rendered = render_to_string('components/campaign_card.html', context)
            self.assertTrue(len(rendered) > 0)
            print("Original campaign card renders OK with debug_mode!")
        except Exception as e:
            print(f"Error rendering campaign card: {e}")
            traceback.print_exc()
            self.fail(f"Failed with error: {e}")
            
    def test_fixed_campaign_card(self):
        """Test if the fixed campaign card renders without recursion error"""
        from funding.models import Campaign, Organisation
        from decimal import Decimal
        
        # Create test organization
        org = Organisation.objects.create(
            name='Test Organisation',
            mission='Test description',
            website='https://org.example.com',
            contact_phone='1234567890'
        )
        
        # Create test campaign with progress data
        campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            goal=Decimal('1000.00'),
            organisation=org,
            status='active'
        )
        
        # Add progress percentage to campaign for testing
        campaign.progress_percentage = 45
        campaign.raised_amount = Decimal('450.00')
        
        # Context for campaign card
        context = {
            'campaign': campaign,
        }
        
        # Try to render the fixed campaign card
        try:
            rendered = render_to_string('components/campaign_card_fixed.html', context)
            self.assertTrue(len(rendered) > 0)
            print("Fixed campaign card renders successfully!")
        except Exception as e:
            print(f"Error rendering fixed campaign card: {e}")
            self.fail(f"Fixed campaign card failed with error: {e}")
            
    
    def test_render_breadcrumbs(self):
        """Test if breadcrumbs.html renders on its own"""
        # Minimal context for breadcrumbs
        context = {
            'home_url': '/',
            'home_title': 'Home',
            'breadcrumbs': [
                {'url': '/campaigns/', 'title': 'Campaigns'},
                {'title': 'Test Campaign'}
            ]
        }
        
        # Try to render just the breadcrumbs component
        try:
            rendered = render_to_string('components/breadcrumbs.html', context)
            self.assertTrue(len(rendered) > 0)
        except RecursionError:
            self.fail("breadcrumbs.html caused RecursionError")
