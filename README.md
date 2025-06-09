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
