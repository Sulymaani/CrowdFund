from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from funding.models import Organisation

CustomUser = get_user_model()

class DonorRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register_donor')
        self.login_url = reverse('accounts:login')

    def test_registration_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_donor.html')

    def test_donor_registration_success(self):
        user_data = {
            'username': 'newdonor',
            'first_name': 'New',
            'last_name': 'Donor',
            'email': 'newdonor@example.com',
            'password': 'a-much-stronger-password-123!',
        }
        form_data = user_data.copy()
        form_data['password2'] = form_data.pop('password')
        form_data['password1'] = form_data['password2']

        response = self.client.post(self.register_url, form_data, follow=True)
        self.assertRedirects(response, reverse('donor_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(CustomUser.objects.filter(username='newdonor').exists())
        new_user = CustomUser.objects.get(username='newdonor')
        self.assertEqual(new_user.role, 'donor')

class AuthMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.protected_url = reverse('funding:campaign_list')
        self.login_url = reverse('accounts:login')

    def test_unauthenticated_user_redirected(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

class LoginLogoutFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('logout')
        self.home_url = reverse('home')

        self.admin_user = CustomUser.objects.create_superuser(username='testadmin', password='password123', email='admin@test.com', role='admin')
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')
        self.org = Organisation.objects.create(name='Test Org')
        self.owner = CustomUser.objects.create_user(username='owner', password='password123', role='org_owner', organisation=self.org)

    def test_login_redirects_admin_to_admin_dashboard(self):
        response = self.client.post(self.login_url, {'username': 'testadmin', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('core_admin:dashboard'))

    def test_login_redirects_donor_to_donor_dashboard(self):
        response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('donor_dashboard'))

    def test_login_redirects_verified_owner_to_org_dashboard(self):
        response = self.client.post(self.login_url, {'username': 'owner', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('org_dashboard'))

    def test_login_failure(self):
        response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_redirects_to_home_page(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.post(self.logout_url, follow=True)
        self.assertRedirects(response, self.home_url)
        self.assertEqual(response.status_code, 200)


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_superuser(username='testadmin', password='password123', email='admin@test.com', role='admin')
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')
        self.org = Organisation.objects.create(name='Test Org')
        self.owner = CustomUser.objects.create_user(username='owner', password='password123', role='org_owner', organisation=self.org)

        self.admin_dashboard_url = reverse('core_admin:dashboard')
        self.donor_dashboard_url = reverse('donor_dashboard')
        self.org_dashboard_url = reverse('org_dashboard')

    def test_admin_access(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.donor_dashboard_url)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.org_dashboard_url)
        self.assertEqual(response.status_code, 403)

    def test_donor_access(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(self.donor_dashboard_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.org_dashboard_url)
        self.assertEqual(response.status_code, 403)

    def test_org_owner_access(self):
        self.client.login(username='owner', password='password123')
        response = self.client.get(self.org_dashboard_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(self.donor_dashboard_url)
        self.assertEqual(response.status_code, 403)
