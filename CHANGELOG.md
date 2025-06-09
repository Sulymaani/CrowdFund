# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.2.0] - 2025-06-09

### Added
- **Iteration 2: User Authentication and Roles**
  - Implemented `CustomUser` model extending `AbstractUser`, with `role` (admin, donor, org_owner) and optional FK to `Organisation`.
  - Created login, logout, and registration views and templates.
  - Implemented `role_required` decorator for view access control based on user roles.
  - Added tests for authentication, registration, and role-based access.
  - Configured `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, and `AUTH_USER_MODEL`.
  - Seed command enhanced to create users with different roles.

- **Iteration 3: Organisation Application & Admin Verification**
  - Added `verification_status` (pending, verified, rejected) and `admin_remarks` to `Organisation` model.
  - Organisation application form (`OrganisationCreateView`) now sets `verification_status` to 'pending'.
  - Created admin views for organisation verification queue (`AdminOrganisationQueueView`) and review (`AdminOrganisationReviewView`).
  - Implemented POST actions in `AdminOrganisationReviewView` to verify or reject organisations, updating status and adding remarks.
  - `role_required` decorator updated to deny access to `org_owner` if their organisation is not 'verified'.
  - Added admin templates: `org_queue.html`, `org_review.html`, and `_messages.html` partial.
  - Seed command updated to create organisations with various verification statuses and corresponding owners.
  - Comprehensive tests for admin verification workflow and `role_required` decorator behavior with organisation status.

### Changed
- `Organisation.verified` boolean field removed, replaced by `verification_status` string field.
- `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL` updated to use namespaced `'funding:campaign_list'`.
- URLs in `password_change_done.html` and various tests updated to use namespaced URLs.

### Fixed
- Corrected role references in decorators and views from `CustomUser.Role.ENUM_MEMBER` to string literals (e.g., `'org_owner'`).
- Resolved `TemplateDoesNotExist` errors for admin views by guiding user to create necessary templates.
- Fixed `NoReverseMatch` errors by ensuring all relevant `reverse()` calls and `{% url %}` tags use namespaces.
- Addressed `AssertionError: 403 != 200` in `accounts.tests` by ensuring test data correctly reflected `verification_status` for organisations.

## [0.1.0] - 2025-06-09

### Added
- **Iteration 1: Core Data Models**
  - Created `funding` app.
  - Defined `Organisation` and `Campaign` models with basic fields.
  - Registered models with Django admin, including list filters for `Organisation.verified` and `Campaign.status`, `Campaign.organisation`.
  - Implemented basic class-based views:
    - `CampaignListView` (shows only `status='active'` campaigns, accessible at `/`).
    - `CampaignDetailView` (accessible at `/campaign/<pk>/`).
    - `OrganisationCreateView` for submitting new organisations (accessible at `/org/apply/`, sets `verified=False` by default).
  - Created initial HTML templates: `base.html`, `funding/home.html`, `funding/campaign_detail.html`, `funding/organisation_form.html`.
  - Added Tailwind CSS via CDN for basic styling.
  - Generated and applied database migrations for the `funding` app.
  - Added basic unit tests for views (list, detail, create) and model interactions.
  - Configured template directory in `settings.py`.
  - Updated project-level `urls.py` to include `funding.urls` and removed old scaffold view.

### Changed
- Root URL `/` now points to `CampaignListView` instead of the initial scaffold message.

### Removed
- Removed initial `crowdfund/views.py` and its associated "CrowdFund running" message.
