# CrowdFund - Modular Django Project

CrowdFund is a comprehensive fundraising platform that connects donors with organizations running charitable campaigns.

## Project Architecture

The project follows a domain-driven modular architecture, with dedicated apps for each major functional area:

### Core Apps

- **accounts**: User authentication, registration, and profile management
  - Handles all user types (donors, organization owners, admin)
  - Custom user model with role-based permissions

- **campaigns**: Campaign management
  - Campaign creation, editing, and lifecycle management
  - Campaign approval workflow and status management
  - Public campaign browsing and discovery

- **organizations**: Organization management
  - Organization profiles and settings
  - Organization owner dashboard
  - Public organization directory

- **donations**: Donation processing
  - Donation creation and tracking
  - Donation history for donors and organizations
  - Donation reporting and exports

- **core**: Shared functionality
  - Base mixins and utilities
  - Shared validators
  - Context processors

### Supplementary Components

- **utils**: Helper utilities
  - Constants (messages, status choices)
  - Message utilities
  - Custom validators

- **static**: Static assets
  - CSS, JavaScript, and image files
  - Organized by component

- **templates**: HTML templates
  - Organized by app and role
  - Componentized for reusability

## Project Setup

### Prerequisites

- Python 3.8+
- Django 5.0+
- PostgreSQL (recommended) or SQLite

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crowdfund.git
cd crowdfund
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update database settings and secret key

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

8. Access the site at http://localhost:8000

## Development Guidelines

### URL Naming Conventions

- Use namespaced URLs for all apps (e.g., `campaigns:detail`)
- Keep URL names consistent across related views (list, detail, create, edit)
- Group URLs by user role where appropriate (donor, org, admin)

### Template Organization

- Templates are stored in app-specific directories
- Role-specific templates use subdirectories (donor, org, admin)
- Reusable components are in the shared template directory

### Database Models

- Follow Django's model best practices
- Use descriptive related_name attributes for reverse relationships
- Add verbose docstrings to all models
- Use appropriate field types and constraints

### Testing

- Write tests for all critical functionality
- Separate unit tests and integration tests
- Use factories for test data
- Test all authentication and permission requirements

## Authentication Flow

The platform supports three main user roles:

1. **Donors**: Register to make donations to campaigns
2. **Organization Owners**: Register and create an organization profile to launch campaigns
3. **Admins**: Manage the platform, review campaigns, and moderate content

Each role has specific permissions and views tailored to their needs.

## License

[MIT License](LICENSE)

## Contributors

- Your Name - Initial work and architecture
