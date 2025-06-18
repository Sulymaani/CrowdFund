from utils.constants import UserRoles

def impersonation_status(request):
    """Adds impersonation status to the template context."""
    return {
        'is_impersonating': 'impersonator_id' in request.session
    }

def debug_pre_auth_processor(request):
    print(f"\nDEBUG: debug_pre_auth_processor")
    user = getattr(request, 'user', 'UserAttributeNotOnRequest')
    print(f"DEBUG: request.user is: {user}")
    if user != 'UserAttributeNotOnRequest' and hasattr(user, 'is_authenticated'):
        print(f"DEBUG: request.user.is_authenticated: {user.is_authenticated}")
    else:
        print(f"DEBUG: request.user has no is_authenticated or not present")
    return {}

def debug_post_auth_processor(request):
    print(f"\nDEBUG: debug_post_auth_processor")
    user_obj = getattr(request, 'user', 'UserAttributeNotOnRequest')
    print(f"DEBUG: request.user (in post_auth_processor) is: {user_obj}")
    is_auth_val = 'Unknown'
    if user_obj != 'UserAttributeNotOnRequest' and hasattr(user_obj, 'is_authenticated'):
        is_auth_val = user_obj.is_authenticated
        print(f"DEBUG: request.user.is_authenticated (in post_auth_processor): {is_auth_val}")
    else:
        print(f"DEBUG: request.user (in post_auth_processor) has no is_authenticated or not present")
    
    return {
        'debug_post_auth_ran': True,
        'user_from_post_auth_debug': user_obj
    }


def user_role_context(request):
    """
    Adds user role-specific context variables to all templates.
    This centralizes role checks that would otherwise be scattered throughout templates and views.
    """
    context = {
        'is_authenticated': False,
        'is_donor': False,
        'is_org_owner': False,
        'is_admin': False,
        'user_role': None
    }
    
    user = request.user
    
    if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
        return context
    
    context['is_authenticated'] = True
    
    # If user has a role attribute, add role-specific flags
    if hasattr(user, 'role'):
        context['user_role'] = user.role
        context['is_donor'] = (user.role == UserRoles.DONOR)
        context['is_org_owner'] = (user.role == UserRoles.ORG_OWNER)
        context['is_admin'] = (user.role == UserRoles.ADMIN or user.is_staff)
    elif hasattr(user, 'is_staff') and user.is_staff:
        context['is_admin'] = True
    
    return context
