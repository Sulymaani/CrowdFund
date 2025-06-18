# CrowdFund Project Structure Documentation

## Overview

CrowdFund is a Django-based crowdfunding platform that allows organizations to create fundraising campaigns and donors to support causes they care about. This document provides an overview of the project's structure and organization to help developers understand how different components work together.

## Directory Structure

```
CrowdFund/
├── accounts/               # User authentication and profile management
├── api/                    # Global API endpoints and configuration
├── campaigns/              # Campaign management functionality
├── core/                   # Core functionality shared across the application
├── crowdfund/              # Project configuration (settings, main urls)
├── donations/              # Donation processing and management
├── funding/                # Legacy app (gradually being phased out)
├── organizations/          # Organization management functionality
├── static/                 # Static files (CSS, JS, images)
├── tags/                   # Tagging functionality for campaigns
├── templates/              # Global templates
├── tests/                  # Test utilities and global tests
├── .coveragerc             # Coverage configuration
├── manage.py               # Django management script
└── run_coverage.py         # Script to run test coverage analysis
```

## App-Specific Structure

Each app follows a similar structure with these key components:

### Accounts App

The accounts app handles user authentication, registration, and profile management.

```
accounts/
├── api/                    # API endpoints for user data
├── forms/                  # Forms for user authentication and profiles
├── migrations/             # Database migrations
├── templates/              # Account-specific templates
│   └── accounts/           # Account template namespace
├── __init__.py             # Package initialization
├── admin.py                # Admin configuration
├── apps.py                 # App configuration
├── models.py               # CustomUser and profile models
├── tests.py                # Test cases
├── urls.py                 # URL routing
├── urls_donor.py           # URL routing for donor-specific views
└── views.py                # View functions and classes
```

### Campaigns App

The campaigns app manages fundraising campaigns, including creation, updates, and browsing.

```
campaigns/
├── api/                    # API endpoints for campaigns
├── migrations/             # Database migrations
├── static/                 # Campaign-specific static files
├── templates/              # Campaign-specific templates
│   └── campaigns/          # Campaign template namespace
├── __init__.py             # Package initialization
├── admin.py                # Admin configuration
├── apps.py                 # App configuration
├── forms.py                # Forms for campaign management
├── models.py               # Campaign models
├── tests.py                # Test cases
├── urls.py                 # URL routing
└── views.py                # View functions and classes
```

### Donations App

The donations app handles processing and tracking donations to campaigns.

```
donations/
├── api/                    # API endpoints for donations
├── migrations/             # Database migrations
├── templates/              # Donation-specific templates
│   └── donations/          # Donation template namespace
├── __init__.py             # Package initialization
├── admin.py                # Admin configuration
├── apps.py                 # App configuration
├── forms.py                # Forms for donation processing
├── models.py               # Donation models
├── tests.py                # Test cases
├── urls.py                 # URL routing
└── views.py                # View functions and classes
```

### Organizations App

The organizations app manages organization profiles, members, and associated campaigns.

```
organizations/
├── api/                    # API endpoints for organizations
├── migrations/             # Database migrations
├── templates/              # Organization-specific templates
│   └── organizations/      # Organization template namespace
├── __init__.py             # Package initialization
├── admin.py                # Admin configuration
├── apps.py                 # App configuration
├── forms.py                # Forms for organization management
├── models.py               # Organization models
├── tests.py                # Test cases
├── urls.py                 # URL routing
└── views.py                # View functions and classes
```

### Core App

The core app contains functionality shared across the application.

```
core/
├── forms/                  # Shared form utilities and base classes
├── templatetags/           # Custom template tags/filters
├── tests/                  # Shared test utilities
├── utils/                  # Utility functions and helpers
├── views/                  # Shared view components and mixins
├── __init__.py             # Package initialization
├── admin.py                # Admin customizations
├── apps.py                 # App configuration
├── models.py               # Shared models
├── urls.py                 # URL routing
└── views.py                # View functions and classes
```

## Key Design Patterns

### Template Inheritance

We use a hierarchical template inheritance structure:

1. `base_structure.html`: Base layout with common structure
2. Role-specific bases (e.g., `donor/base.html`, `organizations/base.html`)
3. Feature-specific templates that extend the role bases

### View Mixins

Common view behaviors are encapsulated in mixins:

- `MessageMixin`: Standardized message handling
- `RoleMixin`: Role-based access control
- `OwnershipMixin`: Object ownership verification
- `OrganizationMemberMixin`: Organization membership verification
- `AjaxFormMixin`: AJAX form handling
- `FormControlMixin`: Form styling and behavior

### API Structure

The API follows a RESTful design pattern:

- Each app has its own API module with serializers, views, and URLs
- ViewSets provide consistent CRUD operations
- Permissions control access based on user roles and object ownership

## Frontend Assets

Frontend assets are organized by feature and component:

```
static/
├── css/                   # CSS and SCSS files
├── js/                    # JavaScript files
├── images/                # Image assets
└── vendor/                # Third-party libraries
```

## Database Models and Relationships

Key model relationships:

- `CustomUser` ↔ `Organisation`: Users can belong to organizations
- `Campaign` → `Organisation`: Campaigns are owned by organizations
- `Campaign` ← `Donation`: Campaigns receive donations
- `CustomUser` ← `Donation`: Users make donations

## Authentication and Authorization

- Django's built-in authentication system handles user sessions
- Custom role-based authorization through mixins
- Object-level permissions based on ownership and organization membership

## Testing Strategy

- Unit tests for models and utilities
- Integration tests for view functionality
- Test assertions are centralized for consistency
- Coverage reporting to identify untested code

## Development Workflow

1. Run the development server: `python manage.py runserver`
2. Run tests: `python manage.py test`
3. Generate test coverage: `python run_coverage.py`
4. Apply migrations: `python manage.py migrate`
