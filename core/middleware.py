"""
Custom middleware components for the CrowdFund application.

This module contains middleware classes that handle various aspects
of request/response processing across the application.
"""
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin


class AdminIPRestrictionMiddleware(MiddlewareMixin):
    """
    Middleware to restrict admin access to specific IP addresses.
    
    This middleware checks if the request is for an admin page and,
    if so, verifies that the client IP is in the ADMIN_IP_ALLOWLIST.
    """
    
    def process_request(self, request):
        """
        Process each request to check if admin access is allowed.
        
        Args:
            request: The HTTP request object
            
        Returns:
            None if access is allowed, PermissionDenied otherwise
        """
        # Check if this is an admin request
        try:
            resolved = resolve(request.path)
            admin_request = resolved.app_name == 'admin' or resolved.namespace == 'admin'
        except:
            admin_request = False
        
        # Skip non-admin requests
        if not admin_request:
            return None
        
        # Skip if no IP allowlist is configured
        if not hasattr(settings, 'ADMIN_IP_ALLOWLIST') or not settings.ADMIN_IP_ALLOWLIST:
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            # In case of proxy, get the real IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Allow access if IP is in the allowlist
        if ip in settings.ADMIN_IP_ALLOWLIST:
            return None
        
        # Deny access
        raise PermissionDenied("Administrative access restricted.")


class UserRoleMiddleware(MiddlewareMixin):
    """
    Middleware to add user role information to the request.
    
    This middleware adds convenience properties to determine the user's role
    (donor, organization admin, etc.) for easy access in views and templates.
    """
    
    def process_request(self, request):
        """
        Process each request to add user role information.
        
        Args:
            request: The HTTP request object
            
        Returns:
            None
        """
        if not request.user.is_authenticated:
            return None
        
        # Add role properties to the request
        request.is_donor = hasattr(request.user, 'is_donor') and request.user.is_donor
        request.is_organization_admin = (hasattr(request.user, 'organization') and 
                                         request.user.organization is not None)
        request.is_admin = request.user.is_staff or request.user.is_superuser
        
        return None


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to handle application maintenance mode.
    
    When maintenance mode is enabled in settings, this middleware redirects
    all non-admin users to a maintenance page.
    """
    
    def process_request(self, request):
        """
        Process each request to check for maintenance mode.
        
        Args:
            request: The HTTP request object
            
        Returns:
            None if not in maintenance mode or user is admin,
            HttpResponseRedirect to maintenance page otherwise
        """
        # Skip if maintenance mode is not enabled
        if not getattr(settings, 'MAINTENANCE_MODE', False):
            return None
        
        # Allow admin users to access the site during maintenance
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return None
        
        # Skip for the maintenance page itself
        if request.path == reverse('maintenance'):
            return None
        
        # Skip for static files
        if request.path.startswith(settings.STATIC_URL):
            return None
        
        # Redirect to maintenance page
        return HttpResponseRedirect(reverse('maintenance'))


class ResponseTimeMiddleware(MiddlewareMixin):
    """
    Middleware to measure and log response time.
    
    This middleware tracks how long it takes to process requests
    and can log slow responses for performance monitoring.
    """
    
    def process_request(self, request):
        """Start the timer for the request."""
        import time
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        Calculate and log response time.
        
        Args:
            request: The HTTP request object
            response: The HTTP response object
            
        Returns:
            The HTTP response object
        """
        # Skip if request start time wasn't set
        if not hasattr(request, 'start_time'):
            return response
        
        # Calculate response time in milliseconds
        import time
        response_time = (time.time() - request.start_time) * 1000
        
        # Add response time header
        response['X-Response-Time-ms'] = int(response_time)
        
        # Log slow responses (over 1000ms)
        if response_time > 1000:
            import logging
            logger = logging.getLogger('django.request')
            logger.warning(
                f'Slow response ({int(response_time)}ms): {request.method} {request.path}'
            )
        
        return response
