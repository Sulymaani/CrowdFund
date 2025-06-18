"""
Centralized test assertions for the CrowdFund application.

This module provides reusable assertion methods for common test patterns,
ensuring consistent verification across test cases.
"""

from django.test import TestCase
from django.urls import reverse


class CrowdFundAssertionMixin:
    """
    Mixin providing common assertion methods for CrowdFund tests.
    """
    
    def assertContainsMessage(self, response, message_text, level=None):
        """
        Assert that the response contains a specific message.
        
        Args:
            response: The test client response
            message_text: Text content to look for in messages
            level: Optional message level (e.g., messages.SUCCESS, messages.ERROR)
        """
        messages = list(response.context['messages']) if 'messages' in response.context else []
        matching_messages = [m for m in messages if message_text.lower() in str(m).lower()]
        
        if not matching_messages:
            messages_str = ", ".join([str(m) for m in messages])
            self.fail(f"Message '{message_text}' not found in messages: {messages_str}")
            
        if level is not None:
            matching_level_messages = [m for m in matching_messages if m.level == level]
            if not matching_level_messages:
                self.fail(f"Message '{message_text}' found but not with level {level}")
    
    def assertFormError(self, response, form_name, field_name, error_message):
        """
        Enhanced form error assertion that provides better error messages.
        
        Args:
            response: The test client response
            form_name: Name of the form in the response context
            field_name: Name of the field with the error
            error_message: Expected error message
        """
        if form_name not in response.context:
            self.fail(f"Form '{form_name}' not found in response context. Available: {list(response.context.keys())}")
            
        form = response.context[form_name]
        if field_name not in form.errors:
            self.fail(f"Field '{field_name}' has no errors. Fields with errors: {list(form.errors.keys())}")
            
        field_errors = form.errors[field_name]
        for error in field_errors:
            if error_message.lower() in error.lower():
                return
                
        self.fail(f"Error '{error_message}' not found in field '{field_name}' errors: {field_errors}")
    
    def assertRedirectsWithMessage(self, response, expected_url, message_text=None, status_code=302, target_status_code=200):
        """
        Assert that response redirects to expected URL and contains expected message.
        
        Args:
            response: The test client response
            expected_url: URL that the response should redirect to
            message_text: Optional text to check in messages after redirect
            status_code: Expected redirect status code (default: 302)
            target_status_code: Expected status code after redirect (default: 200)
        """
        self.assertRedirects(response, expected_url, status_code, target_status_code)
        
        if message_text:
            redirect_response = self.client.get(expected_url)
            self.assertContainsMessage(redirect_response, message_text)
    
    def assertContainsElement(self, response, element_selector, expected_count=None):
        """
        Assert that response HTML contains specific elements.
        Uses simple string contains approach - not full DOM parsing.
        
        Args:
            response: The test client response
            element_selector: String identifying the element (e.g., '<div class="card">')
            expected_count: Optional - number of elements expected
        """
        content = response.content.decode('utf-8')
        occurrences = content.count(element_selector)
        
        if expected_count is not None:
            self.assertEqual(
                occurrences, expected_count,
                f"Expected {expected_count} occurrences of '{element_selector}', found {occurrences}"
            )
        else:
            self.assertGreater(
                occurrences, 0,
                f"Element '{element_selector}' not found in response"
            )
    
    def assertModelExists(self, model_class, **kwargs):
        """
        Assert that a model with the given attributes exists.
        
        Args:
            model_class: The model class to query
            **kwargs: Filter attributes to look for
        """
        self.assertTrue(
            model_class.objects.filter(**kwargs).exists(),
            f"No {model_class.__name__} found with attributes: {kwargs}"
        )
    
    def assertModelDoesNotExist(self, model_class, **kwargs):
        """
        Assert that no model with the given attributes exists.
        
        Args:
            model_class: The model class to query
            **kwargs: Filter attributes to look for
        """
        self.assertFalse(
            model_class.objects.filter(**kwargs).exists(),
            f"{model_class.__name__} unexpectedly found with attributes: {kwargs}"
        )
    
    def assertLoginRequired(self, url, method='get', data=None):
        """
        Assert that a URL requires login.
        
        Args:
            url: The URL to test
            method: HTTP method to use (default: 'get')
            data: Optional data to send with request
        """
        # Force logout
        self.client.logout()
        
        # Make the request
        request_method = getattr(self.client, method.lower())
        response = request_method(url, data=data or {})
        
        # Check if redirected to login
        login_url = reverse('login')
        self.assertRedirects(
            response, 
            f"{login_url}?next={url}",
            msg_prefix=f"URL '{url}' does not require login"
        )
    
    def assertPermissionRequired(self, url, user, method='get', data=None):
        """
        Assert that a URL requires specific permissions.
        
        Args:
            url: The URL to test
            user: User without required permissions
            method: HTTP method to use (default: 'get')
            data: Optional data to send with request
        """
        # Login as user
        self.client.force_login(user)
        
        # Make the request
        request_method = getattr(self.client, method.lower())
        response = request_method(url, data=data or {})
        
        # Check for permission denied (403)
        self.assertEqual(
            response.status_code, 403,
            f"URL '{url}' did not return permission denied (403) for user {user}"
        )
