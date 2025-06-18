# CrowdFund Code Documentation Standards

## Overview

This document outlines the standards for code documentation in the CrowdFund project. Consistent documentation improves code maintainability, helps onboard new developers, and makes the codebase more accessible.

## Python Docstrings

### Module-Level Docstrings

Each Python module (.py file) should begin with a docstring describing its purpose:

```python
"""
Module for campaign management functionality.
Handles campaign creation, editing, and status management.
"""
```

### Class Docstrings

Document classes with a brief description and any important attributes:

```python
class Campaign(models.Model):
    """
    Represents a fundraising campaign in the system.
    
    Campaigns are linked to an organization and can receive donations.
    Campaign status follows a lifecycle from draft to active to completed.
    """
```

### Method and Function Docstrings

Document methods and functions with a description, parameters, and return values:

```python
def calculate_total_raised(self):
    """
    Calculate the total amount raised for this campaign.
    
    Aggregates all confirmed donations and returns the sum.
    
    Returns:
        Decimal: The total amount raised for the campaign
    """
```

For complex functions, include parameter descriptions and return value information:

```python
def process_donation(campaign_id, amount, donor, payment_method):
    """
    Process a donation to a campaign.
    
    Args:
        campaign_id (int): ID of the campaign receiving the donation
        amount (Decimal): Amount to donate
        donor (CustomUser): User making the donation
        payment_method (str): Payment method to use
        
    Returns:
        tuple: (bool, str) - (success status, message or reference number)
        
    Raises:
        Campaign.DoesNotExist: If campaign with given ID doesn't exist
        ValueError: If amount is negative or zero
    """
```

## Models Documentation

### Model Classes

Each model should have a docstring describing its purpose and important relationships:

```python
class Donation(models.Model):
    """
    Represents a donation made to a campaign.
    
    Tracks donation amount, donor information, payment status,
    and related campaign. Used for financial reporting and 
    campaign progress tracking.
    """
```

### Model Fields

Add comments to explain non-obvious fields or choices:

```python
class Campaign(models.Model):
    # Status choices
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_PAUSED = 'paused'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),      # Not publicly visible
        (STATUS_ACTIVE, 'Active'),    # Accepting donations
        (STATUS_PAUSED, 'Paused'),    # Temporarily not accepting donations
        (STATUS_COMPLETED, 'Completed'),  # Campaign period ended
        (STATUS_CANCELLED, 'Cancelled'),  # Terminated before completion
    ]
    
    # Fields
    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_DRAFT,
        help_text="Controls campaign visibility and ability to receive donations"
    )
```

## Views Documentation

### View Classes

Each view class should describe its purpose and any required permissions:

```python
class CampaignDetailView(DetailView):
    """
    Display detailed information about a campaign.
    
    Shows campaign details, progress, donation history,
    and allows authenticated users to make donations.
    
    No special permissions required to view (public access).
    """
```

### View Methods

Document overridden methods and their purpose:

```python
def get_context_data(self, **kwargs):
    """
    Enhance context with campaign statistics and donation data.
    
    Adds donation history, funding progress percentage,
    and time remaining to the template context.
    """
```

## Forms Documentation

Document the purpose of each form and any validation logic:

```python
class DonationForm(forms.ModelForm):
    """
    Form for processing donations to campaigns.
    
    Validates donation amount against campaign minimum and
    collects optional donor message and anonymity preference.
    """
    
    def clean_amount(self):
        """
        Validate that donation amount meets campaign minimum.
        """
```

## Template Tags Documentation

Each custom template tag should be thoroughly documented:

```python
@register.filter(name='currency')
def currency(value, decimal_places=2):
    """
    Format a value as currency with $ symbol and thousands separators.
    
    Args:
        value: The value to format (can be int, float, Decimal, or None)
        decimal_places: Number of decimal places to display
        
    Usage:
        {{ 1234.56|currency }}  --> $1,234.56
        {{ 1234|currency:0 }}   --> $1,234
        {{ None|currency }}     --> $0.00
    """
```

## JavaScript Documentation

Use JSDoc format for JavaScript functions:

```javascript
/**
 * Updates the donation progress bar for a campaign
 * 
 * @param {string} campaignId - ID of the campaign
 * @param {number} currentAmount - Current amount raised
 * @param {number} goalAmount - Funding goal amount
 * @returns {void}
 */
function updateProgressBar(campaignId, currentAmount, goalAmount) {
    // Function implementation
}
```

## URLs and Views Documentation

Include a comment for each URL pattern explaining its purpose:

```python
urlpatterns = [
    # Campaign list - shows all active campaigns
    path('', views.CampaignListView.as_view(), name='list'),
    
    # Campaign detail - shows single campaign with donations and updates
    path('<slug:slug>/', views.CampaignDetailView.as_view(), name='detail'),
    
    # Create new campaign - requires organization role
    path('create/', views.CampaignCreateView.as_view(), name='create'),
]
```

## Best Practices

1. **Keep Comments Updated**: Always update comments when changing code
2. **Document "Why" Not Just "What"**: Explain reasoning behind non-obvious implementations
3. **Use Clear Language**: Write in simple, clear English
4. **Be Concise**: Avoid overly verbose comments that state the obvious
5. **Document Edge Cases**: Mention edge cases and how they're handled
6. **Include Examples**: Where helpful, provide usage examples

## Tools

- Use pylint or flake8 to enforce docstring presence
- Consider using Sphinx for generating documentation
