from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404
from django.contrib.auth import logout
import time
import logging

# Global variable to track server start time
SERVER_START_TIME = time.time()
logger = logging.getLogger(__name__)

# Forcing a reload to fix stale code issue.
class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define URL names that do not require authentication.
        self.exempt_urls = [
            'home',
            'accounts:login',
            'accounts:logout',
            'password_reset',
            'password_reset_done',
            'password_reset_confirm',
            'password_reset_complete',
            'accounts:register_donor',
            'accounts:register_org',
        ]
        # Define path prefixes that do not require authentication.
        self.exempt_path_prefixes = [
            '/__django_admin__/',
        ]

    def __call__(self, request):
        # If the user is authenticated, we don't need to do anything.
        if request.user.is_authenticated:
            return self.get_response(request)

        # Check if the requested path starts with an exempt prefix.
        for prefix in self.exempt_path_prefixes:
            if request.path.startswith(prefix):
                return self.get_response(request)

        # Check if the requested URL name is in the exempt list.
        try:
            resolved_path = resolve(request.path_info)
            url_name = resolved_path.view_name
            if url_name in self.exempt_urls:
                return self.get_response(request)
        except Resolver404:
            # If the path doesn't resolve, it's not a named URL.
            # We'll let it fall through to the redirect.
            pass

        # If the user is not authenticated and the URL is not exempt, redirect to the landing page.
        return redirect('home')


class ServerRestartMiddleware:
    """
    Middleware to detect server restarts and clear user sessions.
    
    This middleware stores the server start time in the user's session.
    If the stored start time doesn't match the current server start time,
    it means the server has been restarted since the user's last request.
    In that case, it logs the user out for security and UX consistency.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info(f"Server started at: {SERVER_START_TIME}")
    
    def __call__(self, request):
        # Process the request first
        response = self.get_response(request)
        
        # After request processing, handle the server restart check
        # This ensures login flows complete before we check timestamps
        if request.user.is_authenticated:
            # Store the current server time for new sessions
            current_time = request.session.get('server_start_time')
            
            if not current_time:
                # New session, just set the time
                request.session['server_start_time'] = SERVER_START_TIME
            elif float(current_time) != SERVER_START_TIME:
                # Server restart detected for existing session
                logger.info(f"Server restart detected for user {request.user.username}. Logging out.")
                logout(request)
                # Redirect to home page after logout
                return redirect('home')
        
        return response
