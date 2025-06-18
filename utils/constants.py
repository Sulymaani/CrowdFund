"""
Application-wide constants for consistent patterns and behavior.
"""

# Model status choices for consistency across models
class Status:
    """Status constants for models."""
    ACTIVE = 'active'
    PENDING = 'pending'
    CLOSED = 'closed'
    REJECTED = 'rejected'
    DRAFT = 'draft'
    
    # Tuple choices for model fields
    CAMPAIGN_STATUSES = (
        (ACTIVE, 'Active'),
        (PENDING, 'Pending'),
        (CLOSED, 'Closed'),
        (REJECTED, 'Rejected'),
        (DRAFT, 'Draft'),
    )
    
    ORGANISATION_STATUSES = (
        (ACTIVE, 'Active'),
        (PENDING, 'Pending'),
    )

# Directly export status choices for easier import in model files
CAMPAIGN_STATUS_CHOICES = Status.CAMPAIGN_STATUSES
ORGANISATION_STATUS_CHOICES = Status.ORGANISATION_STATUSES

# Campaign category choices
CAMPAIGN_CATEGORY_CHOICES = (
    ('education', 'Education'),
    ('healthcare', 'Healthcare'),
    ('environment', 'Environment'),
    ('poverty', 'Poverty Relief'),
    ('arts', 'Arts & Culture'),
    ('disaster', 'Disaster Relief'),
    ('community', 'Community Development'),
    ('animals', 'Animal Welfare'),
    ('technology', 'Technology'),
    ('other', 'Other'),
)


# User role constants
class UserRoles:
    """User role constants."""
    DONOR = 'donor'
    ORG_OWNER = 'org_owner'
    ADMIN = 'admin'
    
    CHOICES = (
        (DONOR, 'Donor'),
        (ORG_OWNER, 'Organization Owner'),
        (ADMIN, 'Administrator'),
    )


# Standard message templates for consistent user feedback
class Messages:
    """Standard messages for user feedback."""
    # Success messages
    PROFILE_UPDATED = "Your profile has been updated successfully."
    LOGIN_SUCCESS = "You have logged in successfully."
    LOGOUT_SUCCESS = "You have been successfully logged out."
    
    # Account messages
    REGISTRATION_SUCCESS = "Your account has been created successfully. Welcome to CrowdFund!"
    PASSWORD_CHANGED = "Your password has been changed successfully."
    
    # Organization messages
    ORG_CREATED = "Your organization has been created successfully."
    ORG_UPDATED = "Your organization profile has been updated."
    
    # Campaign messages
    CAMPAIGN_CREATED = "Your campaign has been created successfully."
    CAMPAIGN_UPDATED = "Your campaign has been updated successfully."
    CAMPAIGN_SUBMITTED = "Your campaign has been submitted for review."
    
    # Donation messages
    DONATION_SUCCESSFUL = "Thank you for your donation!"
    
    # Error messages
    ERROR_GENERIC = "An error occurred. Please try again."
    ERROR_PERMISSIONS = "You do not have permission to perform this action."
