from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import Organisation, Campaign

CustomUser = get_user_model()

class FundingModelTests(TestCase):
    def test_organisation_save_sets_verified_flag(self):
        org_verified = Organisation.objects.create(name="Test Verified", verification_status='verified', application_notes='Test notes for verified')
        self.assertTrue(org_verified.verified)

        org_pending = Organisation.objects.create(name="Test Pending", verification_status='pending', application_notes='Test notes for pending')
        self.assertFalse(org_pending.verified)

        org_rejected = Organisation.objects.create(name="Test Rejected", verification_status='rejected', application_notes='Test notes for rejected')
        self.assertFalse(org_rejected.verified)

        # Test transition from verified to pending
        org_verified.verification_status = 'pending'
        org_verified.save()
        self.assertFalse(org_verified.verified, "Verified flag should turn False when status changes from 'verified' to 'pending'.")

        # Test transition from pending to verified
        org_pending.verification_status = 'verified'
        org_pending.save()
        self.assertTrue(org_pending.verified, "Verified flag should turn True when status changes to 'verified'.")


class FundingViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.donor_user = CustomUser.objects.create_user(
            username='testdonor', password='password123', email='donor@example.com', role='donor'
        )
        cls.verified_org = Organisation.objects.create(
            name='Verified Test Org Inc.',
            application_notes='This org is verified for testing.',
            verification_status='verified', # save() method will set verified=True
            admin_remarks='Auto-verified by test setup.'
        )
        cls.pending_org_for_applicant = Organisation.objects.create(
            name='Applicant Pending Org',
            application_notes='This org is for the applicant user.',
            verification_status='pending'
        )
        cls.applicant_user = CustomUser.objects.create_user(
            username='applicantuser', 
            password='password123', 
            email='applicant@example.com', 
            role='org_owner', # Starts as owner of a pending org
            organisation=cls.pending_org_for_applicant
        )
        cls.org_owner_user_for_campaigns = CustomUser.objects.create_user(
            username='testorgowner',
            password='password123',
            email='owner@verifiedtest.org',
            role='org_owner',
            organisation=cls.verified_org
        )
        cls.admin_user = CustomUser.objects.create_superuser(
            username='testadmin',
            email='admin@example.com',
            password='password123'
        ) # Superuser is_staff=True by default

        # Orgs and Users for decorator tests
        cls.pending_org_for_decorator_test = Organisation.objects.create(
            name='Decorator Test Pending Org',
            verification_status='pending'
        )
        cls.pending_owner = CustomUser.objects.create_user(
            username='pendingowner', password='password123', role='org_owner', organisation=cls.pending_org_for_decorator_test
        )

        cls.rejected_org_for_decorator_test = Organisation.objects.create(
            name='Decorator Test Rejected Org',
            verification_status='rejected'
        )
        cls.rejected_owner = CustomUser.objects.create_user(
            username='rejectedowner', password='password123', role='org_owner', organisation=cls.rejected_org_for_decorator_test
        )
        # self.org_owner_user_for_campaigns and self.verified_org can be used for the verified case
        cls.campaign = Campaign.objects.create(
            organisation=cls.verified_org,
            title='Live Test Campaign',
            goal=1000,
            status='active'
        )
        cls.pending_campaign = Campaign.objects.create(
            organisation=cls.verified_org,
            title='Pending Test Campaign',
            goal=500,
            status='pending'
        )

    def test_campaign_list_view(self):
        response = self.client.get(reverse('funding:campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.title)
        self.assertTemplateUsed(response, 'funding/home.html')

    def test_campaign_detail_view(self):
        response = self.client.get(reverse('funding:campaign_detail', args=[self.campaign.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.campaign.title)
        self.assertTemplateUsed(response, 'funding/campaign_detail.html')

    def test_organisation_application_create_view_get(self):
        # Test with a user who is allowed to apply (e.g., a donor or unauthenticated)
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:organisation_apply'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/organisation_apply.html')

    def test_organisation_application_create_view_get_already_owner(self):
        # Test with a user who is already an org owner (should be redirected)
        self.client.login(username='applicantuser', password='password123')
        response = self.client.get(reverse('funding:organisation_apply'))
        self.assertEqual(response.status_code, 302)
        # UserPassesTestMixin redirects to LOGIN_URL by default if test_func fails
        # and handle_no_permission is not overridden.
        # We need to ensure LOGIN_URL is defined or use a known login path.
        # Assuming default Django login URL behavior for now.
        from django.conf import settings
        self.assertRedirects(response, reverse('funding:campaign_list'))

    def test_organisation_application_create_view_post_anonymous(self):
        form_data = {'name': 'New Anonymous Org App', 'application_notes': 'Applied by an anonymous user.'}
        response = self.client.post(reverse('funding:organisation_apply'), form_data, follow=True)
        self.assertEqual(response.status_code, 200) # Follows redirect to success_url (home)
        self.assertTrue(Organisation.objects.filter(name='New Anonymous Org App').exists())
        new_org = Organisation.objects.get(name='New Anonymous Org App')
        self.assertEqual(new_org.verification_status, 'pending')
        self.assertFalse(new_org.verified)
        self.assertEqual(new_org.application_notes, 'Applied by an anonymous user.')
        # No direct 'applicant' field on Organisation model. Linkage is via CustomUser.organisation.
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Your organisation application for "{new_org.name}" has been submitted and is pending review.')

    def test_organisation_application_create_view_post_authenticated_donor(self):
        self.client.login(username='testdonor', password='password123')
        form_data = {'name': 'Donor Applied Org', 'application_notes': 'Applied by a logged-in donor.'}
        response = self.client.post(reverse('funding:organisation_apply'), form_data, follow=True)
        self.assertEqual(response.status_code, 200) # Follows redirect to success_url (home)
        self.assertTrue(Organisation.objects.filter(name='Donor Applied Org').exists())
        new_org = Organisation.objects.get(name='Donor Applied Org')
        self.assertEqual(new_org.verification_status, 'pending')
        self.assertFalse(new_org.verified)
        self.assertEqual(new_org.application_notes, 'Applied by a logged-in donor.')
        # Refresh user from DB to get updated role and organisation
        user = CustomUser.objects.get(username='testdonor') 
        self.assertEqual(user.role, 'org_owner')
        self.assertEqual(user.organisation, new_org)
        self.assertEqual(user.organisation, new_org) # Check user is linked to the new org
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Thank you, {user.username}! Your organisation application for "{new_org.name}" has been submitted and is pending review. You have been assigned as the Organisation Owner.')

    def test_organisation_application_create_view_post_authenticated_already_org_owner(self):
        self.client.login(username='applicantuser', password='password123') # This user already owns 'Applicant Pending Org'
        initial_org_count = Organisation.objects.count()
        form_data = {'name': 'Second Org By Existing Owner', 'application_notes': 'Attempt by existing org owner.'}
        response = self.client.post(reverse('funding:organisation_apply'), form_data, follow=True)
        # UserPassesTestMixin should redirect. Default is LOGIN_URL, but view overrides to 'home' with a message.
        self.assertEqual(response.status_code, 200) # Follows redirect to home
        self.assertTemplateUsed(response, 'funding/home.html') # Check it lands on the campaign list page
        self.assertEqual(Organisation.objects.count(), initial_org_count) # No new org created
        self.assertFalse(Organisation.objects.filter(name='Second Org By Existing Owner').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('You are already associated with an organisation or have an application pending.' in str(m) for m in messages))

    # --- Admin Organisation Review Tests ---

    def test_admin_org_queue_view_staff_access(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(reverse('funding:admin_org_queue'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/org_queue.html')
        self.assertContains(response, self.pending_org_for_applicant.name)

    def test_admin_org_queue_view_non_staff_access(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:admin_org_queue'))
        self.assertEqual(response.status_code, 403) # UserPassesTestMixin raises 403 for failed test_func

    def test_admin_org_review_view_get_staff_access(self):
        self.client.login(username='testadmin', password='password123')
        response = self.client.get(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/org_review.html')
        self.assertContains(response, self.pending_org_for_applicant.name)

    def test_admin_org_review_view_get_non_staff_access(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]))
        self.assertEqual(response.status_code, 403)

    def test_admin_org_review_post_verify(self):
        self.client.login(username='testadmin', password='password123')
        initial_pending_count = Organisation.objects.filter(verification_status='pending').count()
        form_data = {
            'verification_status': 'verified',
            'admin_remarks': 'Looks good. Approved.'
        }
        response = self.client.post(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('funding:admin_org_queue'))
        
        self.pending_org_for_applicant.refresh_from_db()
        self.assertEqual(self.pending_org_for_applicant.verification_status, 'verified')
        self.assertTrue(self.pending_org_for_applicant.verified)
        self.assertEqual(self.pending_org_for_applicant.admin_remarks, 'Looks good. Approved.')
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Organisation '{self.pending_org_for_applicant.name}' status changed" in str(m) for m in messages))
        self.assertEqual(Organisation.objects.filter(verification_status='pending').count(), initial_pending_count - 1)

    def test_admin_org_review_post_reject(self):
        self.client.login(username='testadmin', password='password123')
        # Create a new pending org for this test to avoid state interference
        another_pending_org = Organisation.objects.create(
            name='Another Pending Review Org',
            application_notes='Needs rejection test.',
            verification_status='pending'
        )
        initial_pending_count = Organisation.objects.filter(verification_status='pending').count()

        form_data = {
            'verification_status': 'rejected',
            'admin_remarks': 'Information missing. Rejected.'
        }
        response = self.client.post(reverse('funding:admin_org_review', args=[another_pending_org.pk]), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('funding:admin_org_queue'))
        
        another_pending_org.refresh_from_db()
        self.assertEqual(another_pending_org.verification_status, 'rejected')
        self.assertFalse(another_pending_org.verified)
        self.assertEqual(another_pending_org.admin_remarks, 'Information missing. Rejected.')
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(f"Organisation '{another_pending_org.name}' status changed" in str(m) for m in messages))
        self.assertEqual(Organisation.objects.filter(verification_status='pending').count(), initial_pending_count - 1)

    # --- Decorator Tests ---

    def test_role_required_org_owner_pending_org_access_denied(self):
        self.client.login(username='pendingowner', password='password123')
        response = self.client.get(reverse('funding:test_org_owner_view'))
        self.assertEqual(response.status_code, 403)

    def test_role_required_org_owner_rejected_org_access_denied(self):
        self.client.login(username='rejectedowner', password='password123')
        response = self.client.get(reverse('funding:test_org_owner_view'))
        self.assertEqual(response.status_code, 403)

    def test_role_required_org_owner_verified_org_access_granted(self):
        self.client.login(username='testorgowner', password='password123') # Owner of self.verified_org
        response = self.client.get(reverse('funding:test_org_owner_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Org Owner Test View Accessed")

    def test_role_required_org_owner_no_org_access_denied(self):
        # Create an org owner without an org assigned (should ideally not happen with current flows but good to test decorator robustness)
        no_org_owner = CustomUser.objects.create_user(username='noorgowner', password='password123', role='org_owner', organisation=None)
        self.client.login(username='noorgowner', password='password123')
        response = self.client.get(reverse('funding:test_org_owner_view'))
        self.assertEqual(response.status_code, 403)
