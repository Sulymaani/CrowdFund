from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define URL names that do not require authentication.
        self.exempt_urls = [
            'landing',
            'login', # django.contrib.auth.urls
            'logout', # django.contrib.auth.urls
            'password_reset', # django.contrib.auth.urls
            'password_reset_done', # django.contrib.auth.urls
            'password_reset_confirm', # django.contrib.auth.urls
            'password_reset_complete', # django.contrib.auth.urls
            'accounts:register_donor',
            'funding:organisation_apply',
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
        return redirect('landing')
