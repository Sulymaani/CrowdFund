from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import Organisation, Campaign
from .forms import CampaignForm, CampaignAdminReviewForm # Import new forms

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
            password='password'
        ) # Superuser is_staff=True by default
        print(f"DEBUG setUpTestData: admin_user created. ID: {cls.admin_user.id}, Username: {cls.admin_user.username}, is_staff: {cls.admin_user.is_staff}, is_active: {cls.admin_user.is_active}")

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
            creator=cls.org_owner_user_for_campaigns, # Added creator
            status='active' # Explicitly set active
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
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_org_queue'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/org_queue.html')
        self.assertContains(response, self.pending_org_for_applicant.name)

    def test_admin_org_queue_view_non_staff_access(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:admin_org_queue'))
        self.assertEqual(response.status_code, 403) # UserPassesTestMixin raises 403 for failed test_func

    def test_admin_org_review_view_get_staff_access(self):
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/org_review.html')
        self.assertContains(response, self.pending_org_for_applicant.name)

    def test_admin_org_review_view_get_non_staff_access(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:admin_org_review', args=[self.pending_org_for_applicant.pk]))
        self.assertEqual(response.status_code, 403)

    def test_admin_org_review_post_verify(self):
        self.client.login(username='testadmin', password='password')
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
        self.client.login(username='testadmin', password='password')
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

    # --- Campaign Creation Tests (CampaignCreateView) ---
    def test_campaign_create_view_get_verified_org_owner(self):
        self.client.login(username='testorgowner', password='password123') # Verified org owner
        response = self.client.get(reverse('funding:campaign_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/campaign_form.html')
        self.assertIsInstance(response.context['form'], CampaignForm)

    def test_campaign_create_view_get_pending_org_owner_denied(self):
        self.client.login(username='pendingowner', password='password123') # Org is pending
        response = self.client.get(reverse('funding:campaign_new'))
        self.assertEqual(response.status_code, 403)

    def test_campaign_create_view_get_rejected_org_owner_denied(self):
        self.client.login(username='rejectedowner', password='password123') # Org is rejected
        response = self.client.get(reverse('funding:campaign_new'))
        self.assertEqual(response.status_code, 403)

    def test_campaign_create_view_get_donor_denied(self):
        self.client.login(username='testdonor', password='password123')
        response = self.client.get(reverse('funding:campaign_new'))
        self.assertEqual(response.status_code, 403)

    def test_campaign_create_view_get_admin_denied(self):
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:campaign_new'))
        self.assertEqual(response.status_code, 403)

    def test_campaign_create_view_post_success(self):
        self.client.login(username='testorgowner', password='password123')
        initial_campaign_count = Campaign.objects.count()
        form_data = {
            'title': 'New Awesome Campaign',
            'goal': 15000,
        }
        response = self.client.post(reverse('funding:campaign_new'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Campaign.objects.count(), initial_campaign_count + 1)
        
        new_campaign = Campaign.objects.latest('created_at')
        self.assertEqual(new_campaign.title, 'New Awesome Campaign')
        self.assertEqual(new_campaign.goal, 15000)
        self.assertEqual(new_campaign.status, 'pending')
        self.assertEqual(new_campaign.organisation, self.org_owner_user_for_campaigns.organisation)
        self.assertEqual(new_campaign.creator, self.org_owner_user_for_campaigns)
        self.assertRedirects(response, reverse('funding:campaign_detail', kwargs={'pk': new_campaign.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('has been submitted and is pending review' in str(m) for m in messages))

    # --- Admin Campaign Queue Tests (AdminCampaignQueueListView) ---
    def test_admin_campaign_queue_view_staff_access(self):
        """Test that AdminCampaignQueueListView is accessible to staff."""
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_campaign_queue'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/campaign_queue.html')
        self.assertIn('pending_campaigns', response.context)
        self.assertContains(response, self.pending_campaign.title)
        self.assertContains(response, self.pending_campaign_for_review.title)
        self.assertContains(response, self.pending_campaign_for_rejection_test.title)
        self.assertNotContains(response, self.campaign.title) # Active campaign
        self.assertNotContains(response, self.rejected_campaign_for_listing.title) # Rejected campaign
        self.assertEqual(len(response.context['pending_campaigns']), 3)

    def test_admin_campaign_queue_view_non_staff_access(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(reverse('funding:admin_campaign_queue'))
        self.assertEqual(response.status_code, 403)

    # --- Admin Campaign Review Tests (AdminCampaignReviewView) ---
    def test_admin_campaign_review_view_get_staff_access(self):
        self.client.login(username='testadmin', password='password')
        response = self.client.get(reverse('funding:admin_campaign_review', args=[self.pending_campaign_for_review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'funding/admin/campaign_review.html')
        self.assertIsInstance(response.context['form'], CampaignAdminReviewForm)
        self.assertEqual(response.context['campaign'], self.pending_campaign_for_review)

    def test_admin_campaign_review_view_get_non_staff_access(self):
        self.client.login(username='testorgowner', password='password123')
        response = self.client.get(reverse('funding:admin_campaign_review', args=[self.pending_campaign_for_review.pk]))
        self.assertEqual(response.status_code, 403)

    def test_admin_campaign_review_post_approve(self):
        """Test approving a pending campaign via POST to AdminCampaignReviewView."""
        self.client.login(username='testadmin', password='password')
        campaign_to_approve = self.pending_campaign_for_review
        form_data = {
            'status': 'active',
            'admin_remarks': 'This campaign looks great. Approved!'
        }
        response = self.client.post(reverse('funding:admin_campaign_review', args=[campaign_to_approve.pk]), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('funding:admin_campaign_queue'))
        
        campaign_to_approve.refresh_from_db()
        self.assertEqual(campaign_to_approve.status, 'active')
        self.assertEqual(campaign_to_approve.admin_remarks, 'This campaign looks great. Approved!')

    def test_admin_campaign_review_post_reject(self):
        """Test rejecting a pending campaign via POST to AdminCampaignReviewView."""
        self.client.login(username='testadmin', password='password')
        campaign_to_reject = self.pending_campaign_for_rejection_test
        form_data = {
            'status': 'rejected',
            'admin_remarks': 'Not enough detail. Rejected.'
        }
        response = self.client.post(
            reverse('funding:admin_campaign_review', args=[campaign_to_reject.pk]),
            form_data,
            follow=True
        )
        # The initial redirect should be 302, leading to a 200 page.
        self.assertRedirects(response, reverse('funding:admin_campaign_queue'), status_code=302, target_status_code=200)
        
        campaign_to_reject.refresh_from_db()
        self.assertEqual(campaign_to_reject.status, 'rejected')
        self.assertEqual(campaign_to_reject.admin_remarks, 'Not enough detail. Rejected.')
        
        # Optionally, check content of the final page (admin_campaign_queue)
        self.assertContains(response, "Pending Campaign Submissions") # Check title of the queue page
        # Ensure the rejected campaign is not listed as pending (if logic implies it's removed or not shown)
        # self.assertNotContains(response, campaign_to_reject.title) # This depends on queue page logic

    def test_admin_campaign_queue_direct_get_context(self):
        """Test that AdminCampaignQueueListView context has 'user' on a direct GET and print response content."""
        self.client.login(username='testadmin', password='password') # Corrected password
        response = self.client.get(reverse('funding:admin_campaign_queue'))
        self.assertEqual(response.status_code, 200)



        # Check debug_request_user_from_view from the view's context
        debug_user_from_view = response.context.get('debug_request_user_from_view')
        self.assertIsNotNone(debug_user_from_view, "'debug_request_user_from_view' should be in context")
        if debug_user_from_view is not None: # Added None check before attribute access
            self.assertTrue(debug_user_from_view.is_authenticated, "'debug_request_user_from_view' should be authenticated")
            self.assertEqual(debug_user_from_view.username, 'testadmin', "'debug_request_user_from_view' username should be testadmin")

        # Check 'user' from auth context processor
        user_from_auth_ctx = response.context.get('user')
        self.assertIsNotNone(user_from_auth_ctx, "'user' from auth context processor should be in context")
        if user_from_auth_ctx is not None: # Added None check before attribute access
            self.assertTrue(user_from_auth_ctx.is_authenticated, "'user' from auth context processor should be authenticated")
            self.assertEqual(user_from_auth_ctx.username, 'testadmin', "'user' from auth context processor username should be testadmin")

        # Check 'request.user' from request context processor
        request_obj_in_ctx = response.context.get('request')
        self.assertIsNotNone(request_obj_in_ctx, "'request' object should be in context")
        if request_obj_in_ctx and hasattr(request_obj_in_ctx, 'user'):
            self.assertIsNotNone(request_obj_in_ctx.user, "'request.user' should not be None") # Added None check
            if request_obj_in_ctx.user is not None:
                self.assertTrue(request_obj_in_ctx.user.is_authenticated, "'request.user' should be authenticated")
                self.assertEqual(request_obj_in_ctx.user.username, 'testadmin', "'request.user' username should be testadmin")

    def test_admin_campaign_review_post_cannot_set_pending(self):
        self.client.login(username='testadmin', password='password')
        # Use an existing campaign that is not pending, e.g., active or rejected, or create one.
        # For this test, let's assume self.campaign1 is suitable (e.g., initially active or becomes active).
        campaign_to_test = self.campaign # Assuming campaign is available from setUp
        original_status = campaign_to_test.status

        form_data = {
            'status': 'pending', # Attempting to set to 'pending'
            'admin_remarks': 'Trying to revert to pending.'
        }
        
        review_url = reverse('funding:admin_campaign_review', args=[campaign_to_test.pk])
        response = self.client.post(review_url, form_data)
        
        # Expect a form error because 'pending' should not be a valid choice for admin action
        self.assertEqual(response.status_code, 200) # Form error usually re-renders the page with status 200
        # Pass the form instance directly from the context
        form_instance = response.context['form']

        self.assertFormError(form_instance, 'status', 'Select a valid choice. pending is not one of the available choices.')
        
        campaign_to_test.refresh_from_db()
        self.assertEqual(campaign_to_test.status, original_status, "Campaign status should not have changed.")
