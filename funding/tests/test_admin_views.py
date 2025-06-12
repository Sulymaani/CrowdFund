from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Organisation
from funding.models import Campaign

class AdminViewsTest(TestCase):

    def setUp(self):
        """Set up the necessary users and objects for testing."""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='password123',
            email='admin@test.com'
        )
        self.org_user = User.objects.create_user(
            username='orgowner',
            password='password123',
            email='org@test.com',
            user_type='organisation'
        )
        self.donor_user = User.objects.create_user(
            username='donoruser',
            password='password123',
            email='donor@test.com',
            user_type='donor'
        )
        self.organisation = Organisation.objects.create(
            name='Test Org',
            owner=self.org_user
        )
        self.campaign = Campaign.objects.create(
            name='Test Campaign',
            description='A test campaign.',
            goal=1000,
            organisation=self.organisation,
            status='pending'
        )

    def test_admin_dashboard_access_and_tile_links(self):
        """Test that an admin can access the dashboard and tile links are correct."""
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('core_admin:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('core_admin:admin_campaign_queue'))
        self.assertContains(response, reverse('core_admin:admin_active_campaigns'))
        self.assertContains(response, reverse('core_admin:admin_organisations'))
        self.assertContains(response, reverse('core_admin:admin_donors'))

    def test_admin_campaign_approval(self):
        """Test the campaign approval process."""
        self.client.login(username='adminuser', password='password123')
        campaign = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(campaign.status, 'pending')
        review_url = reverse('core_admin:admin_campaign_review', args=[campaign.pk])
        response = self.client.post(review_url, {'action': 'approve'})
        self.assertRedirects(response, reverse('core_admin:admin_campaign_queue'))
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'active')
        response = self.client.get(reverse('core_admin:admin_campaign_queue'))
        self.assertContains(response, 'Campaign &quot;Test Campaign&quot; has been approved.')

    def test_admin_campaign_rejection(self):
        """Test the campaign rejection process."""
        self.client.login(username='adminuser', password='password123')
        campaign = Campaign.objects.get(pk=self.campaign.pk)
        self.assertEqual(campaign.status, 'pending')
        review_url = reverse('core_admin:admin_campaign_review', args=[campaign.pk])
        response = self.client.post(review_url, {'action': 'reject'})
        self.assertRedirects(response, reverse('core_admin:admin_campaign_queue'))
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'rejected')
        response = self.client.get(reverse('core_admin:admin_campaign_queue'))
        self.assertContains(response, 'Campaign &quot;Test Campaign&quot; has been rejected.')

    def test_admin_organisation_deactivation_and_activation(self):
        """Test that an admin can deactivate and reactivate an organisation."""
        self.client.login(username='adminuser', password='password123')
        org = Organisation.objects.get(pk=self.organisation.pk)
        self.assertTrue(org.is_active)

        # Deactivate
        toggle_url = reverse('core_admin:admin_org_toggle_active', args=[org.pk])
        response = self.client.post(toggle_url)
        self.assertRedirects(response, reverse('core_admin:admin_organisations'))
        org.refresh_from_db()
        self.assertFalse(org.is_active)
        response = self.client.get(reverse('core_admin:admin_organisations'))
        self.assertContains(response, f'Organisation &quot;{org.name}&quot; has been deactivated.')

        # Activate
        response = self.client.post(toggle_url)
        self.assertRedirects(response, reverse('core_admin:admin_organisations'))
        org.refresh_from_db()
        self.assertTrue(org.is_active)
        response = self.client.get(reverse('core_admin:admin_organisations'))
        self.assertContains(response, f'Organisation &quot;{org.name}&quot; has been activated.')
