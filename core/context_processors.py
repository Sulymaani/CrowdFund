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
