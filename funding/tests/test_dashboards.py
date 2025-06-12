from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser, Organisation
from funding.models import Campaign, Donation


class DashboardAccessTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users for each role
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')
        self.org_owner_user = CustomUser.objects.create_user(username='testorgowner', password='password123', role='org_owner')
        self.admin_user = CustomUser.objects.create_superuser(username='testadmin', password='password123', email='admin@test.com')

        # Create an organisation for the org owner
        self.organisation = Organisation.objects.create(name='Test Org', owner=self.org_owner_user)
        self.org_owner_user.organisation = self.organisation
        self.org_owner_user.save()

        # URLs for dashboards
        self.donor_dashboard_url = reverse('funding:donor_dashboard')
        self.org_dashboard_url = reverse('funding:org_dashboard')
        self.admin_dashboard_url = reverse('core:admin_dashboard')

    def test_unauthenticated_access_redirects_to_login(self):
        """Verify unauthenticated users are redirected to the login page."""
        response = self.client.get(self.donor_dashboard_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.donor_dashboard_url}")

        response = self.client.get(self.org_dashboard_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.org_dashboard_url}")

        response = self.client.get(self.admin_dashboard_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.admin_dashboard_url}")

    def test_donor_access(self):
        """A donor can access their dashboard but not others."""
        self.client.login(username='testdonor', password='password123')
        
        response = self.client.get(self.donor_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/donor_dashboard.html')

        response = self.client.get(self.org_dashboard_url)
        self.assertEqual(response.status_code, 403) # Forbidden

        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_org_owner_access(self):
        """An organisation owner can access their dashboard but not others."""
        self.client.login(username='testorgowner', password='password123')

        response = self.client.get(self.org_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/org_dashboard.html')

        response = self.client.get(self.donor_dashboard_url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_access(self):
        """An admin can access the admin dashboard."""
        self.client.login(username='testadmin', password='password123')

        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/dashboard.html')

        # Staff/Admins are not donors or org owners, so they should be blocked
        response = self.client.get(self.donor_dashboard_url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(self.org_dashboard_url)
        self.assertEqual(response.status_code, 403)


class DashboardContentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')
        self.org_owner_user = CustomUser.objects.create_user(username='testorgowner', password='password123', role='org_owner')
        self.organisation = Organisation.objects.create(name='Test Org', owner=self.org_owner_user)
        self.org_owner_user.organisation = self.organisation
        self.org_owner_user.save()

        self.campaign = Campaign.objects.create(title='Test Campaign', organisation=self.organisation, goal=1000)
        self.donation = Donation.objects.create(user=self.donor_user, campaign=self.campaign, amount=50)

    def test_donor_dashboard_content(self):
        """The donor dashboard shows the correct donations."""
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:donor_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Donor Dashboard')
        self.assertIn(self.donation, response.context['donations'])
        self.assertContains(response, f'${self.donation.amount}')

    def test_org_dashboard_content(self):
        """The org dashboard shows the correct campaigns and KPIs."""
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(reverse('funding:org_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Organisation Dashboard')
        self.assertIn(self.campaign, response.context['campaigns'])
        self.assertEqual(response.context['kpis']['total_raised'], 50)

