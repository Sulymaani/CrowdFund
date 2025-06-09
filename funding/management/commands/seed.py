from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from funding.models import Organisation

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data, including users and organisations.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create Organisations first (if they don't exist)
        org1, created_org1 = Organisation.objects.get_or_create(
            name='Tech Innovators Foundation',
            defaults={
                'verified': True,
                'verification_status': 'verified' # Explicitly set status
            }
        )
        if created_org1:
            self.stdout.write(self.style.SUCCESS(f'Organisation "{org1.name}" created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Organisation "{org1.name}" already exists.'))

        org2, created_org2 = Organisation.objects.get_or_create(
            name='Green Future Initiative',
            defaults={
                'verified': False,
                'verification_status': 'pending', # Explicitly set status
                'application_notes': 'Seeking to fund local park renovation projects.'
            }
        )
        if created_org2:
            self.stdout.write(self.style.SUCCESS(f'Organisation "{org2.name}" created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Organisation "{org2.name}" already exists.'))

        # Create a rejected organisation
        org3, created_org3 = Organisation.objects.get_or_create(
            name='Community Builders Co-op',
            defaults={
                'verified': False,
                'verification_status': 'rejected',
                'application_notes': 'Application for a new housing cooperative.',
                'admin_remarks': 'Application rejected due to incomplete financial documentation as of initial review. Applicant advised to resubmit with required forms.'
            }
        )
        if created_org3:
            self.stdout.write(self.style.SUCCESS(f'Organisation "{org3.name}" (rejected) created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Organisation "{org3.name}" (rejected) already exists.'))


        # Create Users
        users_data = [
            {'username': 'admin_user', 'email': 'admin@example.com', 'password': 'password123', 'role': 'admin', 'organisation': None},
            {'username': 'donor_user1', 'email': 'donor1@example.com', 'password': 'password123', 'role': 'donor', 'organisation': None},
            {'username': 'org_owner1', 'email': 'owner1@techinnovators.example.com', 'password': 'password123', 'role': 'org_owner', 'organisation': org1},
            {'username': 'org_owner2', 'email': 'owner2@greenfuture.example.com', 'password': 'password123', 'role': 'org_owner', 'organisation': org2},
            {'username': 'org_owner3', 'email': 'owner3@communitybuilders.example.com', 'password': 'password123', 'role': 'org_owner', 'organisation': org3},
        ]

        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'organisation': user_data.get('organisation')
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User "{user.username}" ({user.get_role_display()}) created.'))
            else:
                self.stdout.write(self.style.WARNING(f'User "{user.username}" already exists.'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))
