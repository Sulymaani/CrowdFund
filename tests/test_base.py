"""
Base test classes and utilities for the CrowdFund project.
These provide common functionality for both unit and integration tests.
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from funding.models import Organisation, Campaign
from utils.constants import UserRoles


class BaseCrowdFundTestCase(TestCase):
    """
    Base test case with utility methods for creating test users, organizations, and campaigns.
    """
    
    def setUp(self):
        """Set up common test data."""
        self.client = Client()
        
        # Create admin user
        self.admin_user = self._create_user(
            username="admin_user",
            email="admin@example.com",
            password="securepassword",
            role=UserRoles.ADMIN
        )
        
        # Create donor user
        self.donor_user = self._create_user(
            username="donor_user",
            email="donor@example.com",
            password="securepassword",
            role=UserRoles.DONOR
        )
        
        # Create organisation owner user and organisation
        self.org_owner = self._create_user(
            username="org_owner",
            email="owner@example.com",
            password="securepassword",
            role=UserRoles.ORG_OWNER
        )
        
        self.organisation = self._create_organisation(
            name="Test Organisation",
            website="https://example.org",
            mission="Test mission statement",
            owner=self.org_owner
        )
    
    def _create_user(self, username, email, password, role):
        """Create a user with the specified role."""
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        return user
    
    def _create_organisation(self, name, website, mission, owner):
        """Create an organisation and associate it with an owner."""
        org = Organisation.objects.create(
            name=name,
            website=website,
            mission=mission
        )
        
        # Associate the owner with this organisation
        owner.organisation = org
        owner.save()
        
        return org
    
    def _create_campaign(self, title, description, goal, organisation, status='active', slug=None):
        """Create a campaign for the specified organisation."""
        # Generate a unique slug if not provided
        if not slug:
            # Use timestamp to ensure uniqueness
            import time
            slug = f"{title.lower().replace(' ', '-')}-{int(time.time())}"
            
        campaign = Campaign.objects.create(
            title=title,
            description=description,
            funding_goal=goal,
            organisation=organisation,
            status=status,
            slug=slug
        )
        return campaign
    
    def _login_user(self, username, password="securepassword"):
        """Login the specified user."""
        return self.client.login(username=username, password=password)


class APITestCase(BaseCrowdFundTestCase):
    """
    Base test case for API endpoints.
    Extends BaseCrowdFundTestCase with API-specific functionality.
    """
    
    def get_api_response(self, url_name, kwargs=None, method='get', data=None, format='json', user=None):
        """
        Make an API request and return the response.
        
        Args:
            url_name: The URL name to reverse
            kwargs: Optional kwargs for URL reversing
            method: HTTP method (get, post, put, patch, delete)
            data: Request data for POST, PUT, PATCH
            format: Response format (json, multipart)
            user: User to authenticate as
        
        Returns:
            Response object
        """
        if user:
            self.client.force_login(user)
        
        url = reverse(url_name, kwargs=kwargs) if kwargs else reverse(url_name)
        
        if method.lower() == 'get':
            return self.client.get(url)
        elif method.lower() == 'post':
            return self.client.post(url, data=data)
        elif method.lower() == 'put':
            return self.client.put(url, data=data)
        elif method.lower() == 'patch':
            return self.client.patch(url, data=data)
        elif method.lower() == 'delete':
            return self.client.delete(url)
        
        raise ValueError(f"Unsupported HTTP method: {method}")
