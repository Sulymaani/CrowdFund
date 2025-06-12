# Changelog

All notable changes to this project will be documented in this file.

## [0.9.0] - 2025-06-12

### Fixed
- Impersonation redirect now uses correct 'org_dashboard' URL name.
- Impersonation session bug where logging out as an impersonated user destroyed the admin session. A new 'Stop Impersonating' banner now correctly restores the admin session without a full logout.
- The 'Delete' button for organisations in the admin console, which now correctly uses a POST form and includes a confirmation dialog.

## [0.8.1] - 2025-06-12

### Fixed
- Corrected `NoReverseMatch` errors for admin queue pages by ensuring all admin-related URLs use the `core_admin` namespace.
- Cleaned up the admin navigation bar, removing public links and ensuring a consistent layout.
- Implemented role-based access control on donor and organization dashboards to prevent access by staff users, returning a 403 Forbidden error as expected.
- Ensured the donation form is not displayed to staff users on campaign detail pages.

## [0.8.0] - 2025-06-12

### Fixed
- Corrected a `NoReverseMatch` error on admin login by renaming the admin dashboard URL from `admin_dashboard` to `dashboard`.
- Fixed a broken "Review submissions" link on the admin dashboard by pointing it to the correct `core_admin:admin_campaign_queue` URL.
- Prevented the donation form from appearing on campaign detail pages for admin users.

## [0.7.0] - 2025-06-12

### Added
- **Iteration 5: Dashboards & URL Audit**
  - Implemented detailed dashboards for Donors, Organisation Owners, and Admins, providing role-specific KPIs and actions.
  - Added smoke tests to ensure users can only access dashboards appropriate for their role, enforcing strict access control.

### Changed
- **Role-Aware Navigation Polish**
  - Implemented active link highlighting in the navigation bar to provide a clear visual cue of the user's current location.
  - Updated access control mixins to be more restrictive, preventing staff users from accessing non-admin pages.

### Fixed
- **Resolved persistent `NoReverseMatch` errors in the admin interface.** The issue was traced to incorrect URL namespaces in templates (`base_admin.html` and `funding/admin/campaign_queue.html`), where the `funding:` namespace was used instead of the correct `core_admin:` for admin-related URLs.
- Corrected dashboard access control to prevent staff from accessing non-admin dashboards.

## [Unreleased]

### Removed
- **Organisation Verification Flow**: Removed the entire admin-led organisation verification process. Organisations now self-register with full details and are active immediately.
    - Deleted `verification_status`, `verified`, and `admin_remarks` fields from the `Organisation` model.
    - Removed all related admin views (`AdminOrganisationQueueView`, `AdminOrganisationReviewView`), forms (`OrganisationAdminReviewForm`), and URL patterns from the `core` and `funding` apps.
    - Deleted obsolete organisation application forms and views.

### Added
- **Unified Registration Flow**: Implemented separate registration paths for donors and organisations under the `/accounts/` app.
    - `/accounts/register/donor/`: For donor sign-ups.
    - `/accounts/register/org/`: For organisation owners to register themselves and their organisation in a single step.
- Users are now automatically logged in and redirected to their respective dashboards upon successful registration.

## [0.3.0] - 2025-06-11

### Added
- **Iteration L1: Auth Landing + Global Redirect**
  - Implemented a combined login/registration landing page at the root URL (`/`).
  - Added `AuthRequiredMiddleware` to enforce global redirects to the landing page for all unauthenticated users.
  - Created placeholder dashboard views and URLs for Admin, Organisation Owner, and Donor roles to support role-aware redirects.
  - Implemented a new donor registration flow at `/register/donor/`.

### Changed
- The root URL (`/`) now serves the authentication landing page instead of the public campaign list.
- Replaced the default Django login flow with a custom function-based view (`landing_login_view`) to provide full control over login logic and redirects.
- Updated `LOGIN_URL` in `settings.py` to point to the root URL (`/`).

### Fixed
- Resolved persistent test failures related to login redirects by correcting the `LOGIN_URL` setting and ensuring the test client posted to the correct endpoint.
- Fixed a data integrity issue in tests where an `Organisation`'s `verified` status was being incorrectly overridden by the model's `save()` method.
- Resolved a persistent `AttributeError` in the login failure test by modifying the test to pass the form object directly to the `assertFormError` assertion.

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
