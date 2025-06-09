from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from funding.models import Organisation # For creating orgs for org_owners

CustomUser = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.org1 = Organisation.objects.create(name='Test Org For Owner', verified=True, verification_status='verified')

        self.admin_user = CustomUser.objects.create_user(username='testadmin', password='password123', role='admin')
        self.donor_user = CustomUser.objects.create_user(username='testdonor', password='password123', role='donor')
        self.org_owner_user = CustomUser.objects.create_user(username='testorgowner', password='password123', role='org_owner', organisation=self.org1)
        
        # URLs for test views
        self.admin_view_url = reverse('admin_test_view')
        self.org_owner_view_url = reverse('org_owner_test_view')
        self.donor_view_url = reverse('donor_test_view')
        self.admin_or_org_owner_view_url = reverse('admin_or_org_owner_test_view')

        # Auth URLs
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.password_change_url = reverse('password_change')
        self.password_change_done_url = reverse('password_change_done')

    def test_user_login_success(self):
        response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'password123'})
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertRedirects(response, reverse('funding:campaign_list'))
        self.assertTrue(self.client.session['_auth_user_id'] == str(self.donor_user.id))

    def test_user_login_fail_wrong_password(self):
        response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200) # Stays on login page
        form = response.context.get('form')
        self.assertIsNotNone(form, "Form not found in response context for wrong password test.")
        self.assertFormError(form, None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_user_login_fail_nonexistent_user(self):
        response = self.client.post(self.login_url, {'username': 'nouser', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertIsNotNone(form, "Form not found in response context for non-existent user test.")
        self.assertFormError(form, None, 'Please enter a correct username and password. Note that both fields may be case-sensitive.')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_user_logout(self):
        self.client.login(username='testdonor', password='password123')
        self.assertTrue('_auth_user_id' in self.client.session)
        response = self.client.post(self.logout_url) # Changed to POST
        self.assertEqual(response.status_code, 302) # Redirects
        self.assertRedirects(response, reverse('funding:campaign_list'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_password_change(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.post(self.password_change_url, {
            'old_password': 'password123',
            'new_password1': 'newpassword456',
            'new_password2': 'newpassword456',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.password_change_done_url)
        # Verify user can login with new password
        self.client.logout()
        login_response = self.client.post(self.login_url, {'username': 'testdonor', 'password': 'newpassword456'})
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    # Role decorator tests
    def test_admin_access_admin_view(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(self.admin_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin access granted.")

    def test_donor_denied_admin_view(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(self.admin_view_url)
        self.assertEqual(response.status_code, 403) # PermissionDenied

    def test_org_owner_access_org_owner_view(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(self.org_owner_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Org owner access granted.")

    def test_admin_denied_org_owner_view(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(self.org_owner_view_url)
        self.assertEqual(response.status_code, 403)

    def test_donor_access_donor_view(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(self.donor_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Donor access granted.")

    def test_org_owner_denied_donor_view(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(self.donor_view_url)
        self.assertEqual(response.status_code, 403)
        
    def test_admin_access_admin_or_org_owner_view(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(self.admin_or_org_owner_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin or Org Owner access granted.")

    def test_org_owner_access_admin_or_org_owner_view(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(self.admin_or_org_owner_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin or Org Owner access granted.")

    def test_donor_denied_admin_or_org_owner_view(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(self.admin_or_org_owner_view_url)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_redirected_from_protected_view(self):
        response = self.client.get(self.admin_view_url)
        self.assertEqual(response.status_code, 302) # Redirects to login
        self.assertRedirects(response, f'{self.login_url}?next={self.admin_view_url}')
