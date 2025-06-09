from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from .models import CustomUser # For user.organisation access

def role_required(allowed_roles):
    """
    Decorator for views that checks that the user is logged in and has one of the allowed roles.
    allowed_roles can be a string (single role) or a list/tuple of strings (multiple roles).
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # If user is not authenticated, redirect to login page, preserving the current path
                return redirect_to_login(request.get_full_path()) 

            if request.user.role not in allowed_roles:
                # If user is authenticated but does not have the required role,
                # raise PermissionDenied or redirect to an access denied page.
                raise PermissionDenied("You do not have permission to access this page.")

            # Additional check if the user's role is ORG_OWNER
            if request.user.role == 'org_owner':
                if not hasattr(request.user, 'organisation') or not request.user.organisation:
                    raise PermissionDenied("Organisation owner role requires an associated organisation.")
                if request.user.organisation.verification_status != 'verified':
                    # Customize message based on actual status if desired, e.g., pending vs. rejected
                    if request.user.organisation.verification_status == 'pending':
                        raise PermissionDenied("Your organisation's application is still pending review.")
                    elif request.user.organisation.verification_status == 'rejected':
                        raise PermissionDenied("Your organisation's application was rejected.")
                    else: # Other non-verified statuses
                        raise PermissionDenied("Your organisation must be verified to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Example usage (for later):
# from .decorators import role_required
# from .models import CustomUser
#
# @role_required(CustomUser.Role.ADMIN)
# def admin_only_view(request):
#     ...
#
# @role_required([CustomUser.Role.ORG_OWNER, CustomUser.Role.ADMIN])
# def org_owner_or_admin_view(request):
#     ...
