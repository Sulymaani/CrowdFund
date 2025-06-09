from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from funding.models import Organisation

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data for development and testing.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Clean up existing data to make the command idempotent
        CustomUser.objects.all().delete()
        Organisation.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing Users and Organisations.'))

        # Create Admin User
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'admin@example.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('adminpass123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user "{admin_user.username}" created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Admin user "{admin_user.username}" already exists.'))

        # Create Organisations
        org_verified, created = Organisation.objects.get_or_create(
            name='Verified Org Inc.',
            defaults={
                'application_notes': 'This organisation is fully vetted and approved.',
                'verification_status': 'verified',
                'admin_remarks': 'Automatically verified by seed script.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Organisation "{org_verified.name}" created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Organisation "{org_verified.name}" already exists.'))

        org_pending, created = Organisation.objects.get_or_create(
            name='Pending Solutions Ltd.',
            defaults={
                'application_notes': 'A new application awaiting review.',
                'verification_status': 'pending'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Organisation "{org_pending.name}" created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Organisation "{org_pending.name}" already exists.'))
        
        org_rejected, created = Organisation.objects.get_or_create(
            name='Rejected Ventures Co.',
            defaults={
                'application_notes': 'This application did not meet criteria.',
                'verification_status': 'rejected',
                'admin_remarks': 'Rejected due to incomplete information during seed.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Organisation "{org_rejected.name}" created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Organisation "{org_rejected.name}" already exists.'))

        # Create Organisation Owner for Verified Org
        org_owner, created = CustomUser.objects.get_or_create(
            username='owner_verified_org',
            defaults={
                'email': 'owner@verified.org',
                'role': 'org_owner',
                'organisation': org_verified
            }
        )
        if created:
            org_owner.set_password('ownerpass123')
            org_owner.save()
            self.stdout.write(self.style.SUCCESS(f'Org Owner "{org_owner.username}" for {org_verified.name} created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Org Owner "{org_owner.username}" already exists.'))

        # Create Donor User
        donor_user, created = CustomUser.objects.get_or_create(
            username='donor_user',
            defaults={
                'email': 'donor@example.com',
                'role': 'donor'
            }
        )
        if created:
            donor_user.set_password('donorpass123')
            donor_user.save()
            self.stdout.write(self.style.SUCCESS(f'Donor user "{donor_user.username}" created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Donor user "{donor_user.username}" already exists.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))
