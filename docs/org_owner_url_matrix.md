# Organization Owner URL Matrix

This document provides a comprehensive list of URLs available to Organization Owners in the CrowdFund application.

## Base URLs

| URL | Description | View | Template |
|-----|-------------|------|----------|
| `/dashboard/org/` | Organization owner dashboard | `OrgDashboardView` | `funding/org_dashboard.html` |
| `/dashboard/org/settings/` | Organization settings | `OrganisationSettingsView` | `funding/org_settings.html` |

## Campaign Management

| URL | Description | View | Template |
|-----|-------------|------|----------|
| `/campaigns/` | List all campaigns | `CampaignListView` | `funding/campaign_list.html` |
| `/campaigns/new/` | Create a new campaign | `CampaignCreateView` | `funding/campaign_form.html` |
| `/campaigns/<id>/` | View campaign details | `CampaignDetailView` | `funding/campaign_detail.html` |
| `/campaigns/<id>/edit/` | Edit a draft/rejected campaign | `CampaignEditView` | `funding/campaign_form.html` |
| `/campaigns/<id>/close/` | Close an active campaign | `CampaignCloseView` | `funding/campaign_close.html` |

## Donation Management

| URL | Description | View | Template |
|-----|-------------|------|----------|
| `/donations/` | List all donations to org campaigns | `DonationsListView` | `funding/donations_list.html` |
| `/donations/export/` | Export donations as CSV | `ExportDonationsCSVView` | N/A (CSV download) |

## Business Rules

1. Organization owners can only have 3 pending campaigns at a time
2. Campaign goals must be between $100 and $2,000,000
3. Organization owners can only edit campaigns with status "draft" or "rejected"
4. Organization owners can only close campaigns with status "active"
5. Organization owners cannot donate to their own campaigns
6. Organization owner access requires:
   - User must be authenticated
   - User must have role "org_owner"
   - User must be associated with an organization
   - Organization must be active
