from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from funding.models import Organisation

CustomUser = get_user_model()

class LandingPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.landing_url = reverse('landing')
        self.donor_dashboard_url = reverse('funding:donor_dashboard')
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')

    def test_landing_page_loads_for_unauthenticated_user(self):
        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/landing.html')

    def test_authenticated_user_redirected_from_landing_page(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(self.landing_url, follow=True)
        self.assertRedirects(response, self.donor_dashboard_url)
        self.assertEqual(response.status_code, 200)

class DonorRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register_donor')
        self.landing_url = reverse('landing')

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
        # The form is a UserCreationForm, so we need to post password1 and password2
        form_data = user_data.copy()
        form_data['password2'] = form_data.pop('password')
        form_data['password1'] = form_data['password2']

        response = self.client.post(self.register_url, form_data, follow=True)
        self.assertRedirects(response, self.landing_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was created
        self.assertTrue(CustomUser.objects.filter(username='newdonor').exists())
        new_user = CustomUser.objects.get(username='newdonor')
        self.assertEqual(new_user.role, 'donor')

class AuthMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.protected_url = reverse('funding:campaign_list') # A URL within the /app/ prefix
        self.landing_url = reverse('landing')

    def test_unauthenticated_user_redirected(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.landing_url)

class LoginLogoutFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.landing_url = reverse('landing')
        self.login_url = reverse('landing') # The landing page handles login POST requests
        self.logout_url = reverse('logout')

        # Create users and orgs
        self.verified_org = Organisation.objects.create(name='Verified Org', verification_status='verified')
        self.pending_org = Organisation.objects.create(name='Pending Org', verified=False)

        self.admin_user = CustomUser.objects.create_superuser(username='testadmin', password='password123', email='admin@test.com')
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')
        self.verified_owner = CustomUser.objects.create_user(username='verifiedowner', password='password123', role='org_owner', organisation=self.verified_org)
        self.pending_owner = CustomUser.objects.create_user(username='pendingowner', password='password123', role='org_owner', organisation=self.pending_org)

    def test_login_redirects_admin_to_admin_dashboard(self):
        response = self.client.post(self.login_url, {'username': 'testadmin', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('funding:admin_dashboard'))

    def test_login_redirects_donor_to_donor_dashboard(self):
        response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('funding:donor_dashboard'))

    def test_login_redirects_verified_owner_to_org_dashboard(self):
        response = self.client.post(self.login_url, {'username': 'verifiedowner', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('funding:org_dashboard'))

    def test_login_redirects_pending_owner_to_status_page(self):
        response = self.client.post(self.login_url, {'username': 'pendingowner', 'password': 'password123'}, follow=True)
        self.assertRedirects(response, reverse('funding:org_status'))

    def test_login_failure(self):
        response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200) # Stays on the landing page
        self.assertTemplateUsed(response, 'accounts/landing.html')


        form = response.context['form']
        self.assertFormError(form, None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')

    def test_logout_redirects_to_landing_page(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.post(self.logout_url, follow=True)
        self.assertRedirects(response, self.landing_url)
        self.assertEqual(response.status_code, 200)
