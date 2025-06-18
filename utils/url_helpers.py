"""
URL helpers for consistent URL handling across the application.
"""

def get_namespaced_url(namespace, name):
    """
    Return a consistently formatted namespaced URL string.
    
    Args:
        namespace (str): The URL namespace (e.g., 'donor', 'accounts')
        name (str): The URL name (e.g., 'dashboard', 'profile')
    
    Returns:
        str: Properly formatted namespace:name string
    """
    return f"{namespace}:{name}"


# Common URL constants to avoid typos and ensure consistency
class URLNames:
    """Constants for URL names used throughout the application."""
    
    class Accounts:
        """URL names for accounts app."""
        LOGIN = "login"
        LOGOUT = "logout"
        REGISTER_DONOR = "register_donor"
        REGISTER_ORG = "register_org"
        EDIT_PROFILE = "edit_profile"
        
    class Donor:
        """URL names for donor app."""
        DASHBOARD = "dashboard"
        PROFILE = "profile"
        CAMPAIGNS = "campaigns"
        ORGANIZATIONS = "organizations"
        DONATIONS = "donations"
        DONATION_DETAIL = "donation_detail"
        
    class Org:
        """URL names for organization app."""
        DASHBOARD = "dashboard"
        SETTINGS = "settings"
        CAMPAIGNS = "campaigns"
        CAMPAIGN_CREATE = "campaign_create"
        CAMPAIGN_EDIT = "campaign_edit"


class Namespaces:
    """Constants for URL namespaces used throughout the application."""
    ACCOUNTS = "accounts"
    DONOR = "donor"
    ORG = "org"
    ADMIN = "core_admin"
