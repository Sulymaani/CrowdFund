from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Organisation, Campaign

CustomUser = get_user_model()

class FundingViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.donor_user = CustomUser.objects.create_user(
            username='testdonor', password='password123', email='donor@example.com', role='donor'
        )
        cls.organisation = Organisation.objects.create(
            name='Test Org Inc.'
        )
        cls.org_owner_user = CustomUser.objects.create_user(
            username='testorgowner',
            password='password123',
            email='owner@test.org',
            role='org_owner',
            organisation=cls.organisation
        )
        cls.admin_user = CustomUser.objects.create_superuser(
            username='testadmin',
            email='admin@example.com',
            password='password'
        )

        cls.active_campaign = Campaign.objects.create(
            organisation=cls.organisation,
            title='Live Test Campaign',
            description='A campaign that is active.',
            goal=1000,
            creator=cls.org_owner_user,
            status='active'
        )
        cls.pending_campaign = Campaign.objects.create(
            organisation=cls.organisation,
            creator=cls.org_owner_user,
            title='Pending Review Test Campaign',
            description='A campaign that is pending.',
            goal=2000,
            status='pending'
        )

    def test_campaign_list_view_shows_only_active_campaigns(self):
        """
        The main campaign list should only show active campaigns to any user.
        """
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_campaign.title)
        self.assertNotContains(response, self.pending_campaign.title)
        self.assertTemplateUsed(response, 'funding/campaign_list.html')

    def test_campaign_detail_view_for_active_campaign(self):
        """
        The detail view for an active campaign should be visible.
        """
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:campaign_detail', args=[self.active_campaign.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_campaign.title)
        self.assertTemplateUsed(response, 'funding/campaign_detail.html')

    def test_pending_campaign_not_visible_in_detail_view(self):
        """
        Pending campaigns should not be publicly accessible via detail view and should 404.
        """
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:campaign_detail', args=[self.pending_campaign.pk]))
        self.assertEqual(response.status_code, 404)

class CampaignCreationTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name='Test Org for Campaigns')
        self.org_owner = CustomUser.objects.create_user(
            username='campaigncreator',
            password='password123',
            role='org_owner',
            organisation=self.organisation
        )
        self.donor_user = CustomUser.objects.create_user(
            username='donor_no_create',
            password='password123',
            role='donor'
        )
        self.create_url = reverse('org:campaign_new')

    def test_org_owner_can_access_create_campaign_page(self):
        self.client.login(username='campaigncreator', password='password123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/campaign_form.html')

    def test_donor_cannot_access_create_campaign_page(self):
        self.client.login(username='donor_no_create', password='password123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_unauthenticated_user_redirected_from_create_campaign_page(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_successful_campaign_creation(self):
        self.client.login(username='campaigncreator', password='password123')
        form_data = {
            'title': 'My New Awesome Campaign',
            'description': 'This is a test description.',
            'goal': '5000.00',
        }
        response = self.client.post(self.create_url, form_data, follow=True)
        self.assertRedirects(response, reverse('org_dashboard'))
        self.assertTrue(Campaign.objects.filter(title='My New Awesome Campaign').exists())
        new_campaign = Campaign.objects.get(title='My New Awesome Campaign')
        self.assertEqual(new_campaign.status, 'pending')
        self.assertEqual(new_campaign.creator, self.org_owner)
