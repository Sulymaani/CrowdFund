# CrowdFund URL Structure

This document outlines the accessible URLs for each user role in the application.

## Unauthenticated User

- `/`: Marketing landing page.
- `/accounts/login/`: Login page.
- `/accounts/register/donor/`: Donor registration page.
- `/accounts/register/org/`: Organisation registration page.
- `/campaigns/`: View list of all active campaigns.
- `/campaigns/<id>/`: View campaign details.

## Authenticated User: Donor

Includes all Unauthenticated URLs, plus:

- `/dashboard/donor/`: Donor dashboard to view donation history.
- `/campaigns/<id>/donate/`: Page to make a donation to a specific campaign.
- `/accounts/logout/`: Logout.

## Authenticated User: Organisation Owner

Includes all Unauthenticated URLs, plus:

- `/dashboard/org/`: Organisation dashboard to view and manage their campaigns.
- `/campaigns/new/`: Page to create a new campaign.
- `/accounts/logout/`: Logout.
- **Restriction**: Organisation owners cannot access the donation page (`/campaigns/<id>/donate/`).

## Authenticated User: Admin

Includes all Unauthenticated URLs, plus:

- `/__django_admin__/`: Full Django admin interface.
- `/admin/dashboard/`: Custom admin dashboard with site statistics.
- `/admin/campaign-queue/`: View queue of campaigns pending approval.
- `/admin/campaign-review/<id>/`: Review and approve/reject a specific campaign.
- `/accounts/logout/`: Logout.
