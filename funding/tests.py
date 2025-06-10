from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import Organisation, Campaign, Donation
from .forms import CampaignForm, CampaignAdminReviewForm

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
            verification_status='verified',  # save() method will set verified=True
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
            role='org_owner',  # Starts as owner of a pending org
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
            password='password'
        )  # Superuser is_staff=True by default

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

        cls.active_campaign = Campaign.objects.create(
            organisation=cls.verified_org,
            title='Live Test Campaign',
            goal=1000,
            creator=cls.org_owner_user_for_campaigns,
            status='active'
        )
        cls.pending_campaign_for_review = Campaign.objects.create(
            organisation=cls.verified_org,
            creator=cls.org_owner_user_for_campaigns,
            title='Pending Review Test Campaign',
            goal=2000,
            status='pending'
        )
        cls.pending_campaign_for_rejection_test = Campaign.objects.create(
            organisation=cls.verified_org,
            creator=cls.org_owner_user_for_campaigns,
            title='Pending Campaign for Rejection Test',
            goal=1600,
            status='pending'
        )
        cls.rejected_campaign_for_listing = Campaign.objects.create(
            organisation=cls.verified_org,
            creator=cls.org_owner_user_for_campaigns,
            title='Rejected Test Campaign',
            goal=3000,
            status='rejected',
            admin_remarks='Previously rejected.'
        )
        cls.pending_campaign = Campaign.objects.create(
            organisation=cls.verified_org,
            title='Pending Test Campaign',
            goal=500,
            status='pending',
            creator=cls.org_owner_user_for_campaigns
        )

    def test_campaign_list_view(self):
        response = self.client.get(reverse('funding:campaign_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_campaign.title)
        self.assertTemplateUsed(response, 'funding/home.html')

    def test_campaign_detail_view(self):
        response = self.client.get(reverse('funding:campaign_detail', args=[self.active_campaign.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.active_campaign.title)
        self.assertTemplateUsed(response, 'funding/campaign_detail.html')

    def test_organisation_application_create_view_get(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:organisation_apply'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/organisation_apply.html')

    def test_organisation_application_create_view_get_already_owner(self):
        self.client.login(username='applicantuser', password='password123')
        response = self.client.get(reverse('funding:organisation_apply'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('funding:campaign_list'))

    def test_organisation_application_create_view_post_anonymous(self):
        form_data = {'name': 'New Anonymous Org App', 'application_notes': 'Applied by an anonymous user.'}
        response = self.client.post(reverse('funding:organisation_apply'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Organisation.objects.filter(name='New Anonymous Org App').exists())
        new_org = Organisation.objects.get(name='New Anonymous Org App')
        self.assertEqual(new_org.verification_status, 'pending')
        self.assertFalse(new_org.verified)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Your organisation application for "{new_org.name}" has been submitted and is pending review.')

    def test_organisation_application_create_view_post_authenticated_donor(self):
        donor_for_app = CustomUser.objects.create_user(username='donor_for_app', password='password123', role='donor')
        self.client.login(username='donor_for_app', password='password123')
        form_data = {'name': 'Donor Applied Org', 'application_notes': 'Applied by a logged-in donor.'}
        response = self.client.post(reverse('funding:organisation_apply'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Organisation.objects.filter(name='Donor Applied Org').exists())
        new_org = Organisation.objects.get(name='Donor Applied Org')
        donor_for_app.refresh_from_db()
        self.assertEqual(donor_for_app.role, 'org_owner')
        self.assertEqual(donor_for_app.organisation, new_org)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(f'Thank you, {donor_for_app.username}!', str(messages[0]))

    def test_organisation_application_create_view_post_authenticated_already_org_owner(self):
        self.client.login(username='applicantuser', password='password123')
        initial_org_count = Organisation.objects.count()
        form_data = {'name': 'Second Org By Existing Owner', 'application_notes': 'Attempt by existing org owner.'}
        response = self.client.post(reverse('funding:organisation_apply'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/home.html')
        self.assertEqual(Organisation.objects.count(), initial_org_count)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('You are already associated with an organisation' in str(m) for m in messages))

    # --- Admin Organisation Review Tests ---
    def test_admin_org_queue_view_staff_access(self):
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_org_queue'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/org_queue.html')
        self.assertContains(response, self.pending_org_for_applicant.name)

    def test_admin_org_queue_view_non_staff_access(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:admin_org_queue'))
        self.assertEqual(response.status_code, 403)

    def test_admin_org_review_view_get_staff_access(self):
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/org_review.html')
        self.assertContains(response, self.pending_org_for_applicant.name)

    def test_admin_org_review_post_verify(self):
        self.client.login(username='testadmin', password='password')
        form_data = {'verification_status': 'verified', 'admin_remarks': 'Looks good. Approved.'}
        response = self.client.post(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]), form_data, follow=True)
        self.assertRedirects(response, reverse('funding:admin_org_queue'))
        self.pending_org_for_applicant.refresh_from_db()
        self.assertEqual(self.pending_org_for_applicant.verification_status, 'verified')
        self.assertTrue(self.pending_org_for_applicant.verified)

    # --- Decorator Tests ---
    def test_role_required_org_owner_pending_org_access_denied(self):
        self.client.login(username='pendingowner', password='password123')
        response = self.client.get(reverse('funding:test_org_owner_view'))
        self.assertEqual(response.status_code, 403)

    def test_role_required_org_owner_verified_org_access_granted(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(reverse('funding:test_org_owner_view'))
        self.assertEqual(response.status_code, 200)

    # --- Campaign Creation Tests ---
    def test_campaign_create_view_get_verified_org_owner(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(reverse('funding:campaign_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/campaign_form.html')

    def test_campaign_create_view_post_success(self):
        self.client.login(username='testorgowner', password='password123')
        initial_campaign_count = Campaign.objects.count()
        form_data = {'title': 'New Awesome Campaign', 'goal': 15000}
        response = self.client.post(reverse('funding:campaign_new'), form_data, follow=True)
        self.assertEqual(Campaign.objects.count(), initial_campaign_count + 1)
        new_campaign = Campaign.objects.latest('created_at')
        self.assertRedirects(response, reverse('funding:campaign_detail', kwargs={'pk': new_campaign.pk}))

    # --- Admin Campaign Queue Tests ---
    def test_admin_campaign_queue_view_staff_access(self):
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_campaign_queue'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/campaign_queue.html')
        self.assertEqual(len(response.context['pending_campaigns']), 3)

    # --- Admin Campaign Review Tests ---
    def test_admin_campaign_review_post_approve(self):
        self.client.login(username='testadmin', password='password')
        campaign_to_approve = self.pending_campaign_for_review
        form_data = {'status': 'active', 'admin_remarks': 'Approved!'}
        self.client.post(reverse('funding:admin_campaign_review', args=[campaign_to_approve.pk]), form_data)
        campaign_to_approve.refresh_from_db()
        self.assertEqual(campaign_to_approve.status, 'active')

    def test_admin_campaign_review_post_reject(self):
        self.client.login(username='testadmin', password='password')
        campaign_to_reject = self.pending_campaign_for_rejection_test
        form_data = {'status': 'rejected', 'admin_remarks': 'Rejected.'}
        self.client.post(reverse('funding:admin_campaign_review', args=[campaign_to_reject.pk]), form_data)
        campaign_to_reject.refresh_from_db()
        self.assertEqual(campaign_to_reject.status, 'rejected')

    # --- Donation Tests ---
    def test_create_donation_authenticated_user_active_campaign(self):
        self.client.login(username='testdonor', password='password123')
        donation_amount = 100
        response = self.client.post(reverse('funding:campaign_donate', args=[self.active_campaign.pk]), {'amount': donation_amount}, follow=True)
        self.assertRedirects(response, reverse('funding:campaign_detail', args=[self.active_campaign.pk]))
        self.assertTrue(Donation.objects.filter(campaign=self.active_campaign, user=self.donor_user, amount=donation_amount).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'Thank you for your generous donation of ${donation_amount}!')

    def test_create_donation_anonymous_user_redirects_to_login(self):
        donation_url = reverse('funding:campaign_donate', args=[self.active_campaign.pk])
        response = self.client.post(donation_url, {'amount': 50})
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={donation_url}')
        self.assertEqual(Donation.objects.count(), 0)

    def test_donation_rejected_for_non_active_campaign(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.post(reverse('funding:campaign_donate', args=[self.pending_campaign.pk]), {'amount': 50}, follow=True)
        self.assertRedirects(response, reverse('funding:campaign_detail', args=[self.pending_campaign.pk]))
        self.assertEqual(Donation.objects.filter(campaign=self.pending_campaign).count(), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Donations are only allowed for active campaigns.')

    def test_total_donations_displayed_on_campaign_detail(self):
        Donation.objects.create(campaign=self.active_campaign, user=self.donor_user, amount=100)
        Donation.objects.create(campaign=self.active_campaign, user=self.donor_user, amount=150)
        total_donated = 250
        response = self.client.get(reverse('funding:campaign_detail', args=[self.active_campaign.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'${total_donated} raised of ${self.active_campaign.goal} goal')
        self.assertEqual(response.context['total_donations'], total_donated)
        self.assertEqual(response.context['width_percentage'], int((total_donated / self.active_campaign.goal) * 100))
