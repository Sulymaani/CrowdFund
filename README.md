# CrowdFund

A lean, role-based crowdfunding web app built with Django.

## Phase 1 Development

This project is being developed incrementally. This README will be updated as new features, commands, or environment variables are added.

## Setup (Initial)

1.  Clone the repository.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run migrations:
    ```bash
    python manage.py migrate
    ```
5.  Start the development server:
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

## User Authentication

This project follows an **authentication-first** design. There are no public-facing pages; all users are required to have an account and be logged in to access the application.

- **Landing Page**: All users (both authenticated and unauthenticated) are directed to a combined login and registration landing page at the root URL (`/`).
- **Global Redirects**: Any attempt to access a protected page without being authenticated will result in a redirect to the landing page.
- **Role-Based Dashboards**: Upon successful login, users are redirected to a dashboard specific to their role:
  - **Donors**: Redirected to their personal dashboard.
  - **Organisation Owners**: Redirected to their organisation's dashboard (if verified) or a status page (if pending or rejected).
  - **Admins**: Redirected to the admin console.
