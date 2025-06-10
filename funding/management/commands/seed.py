from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from funding.models import Organisation, Campaign, Donation

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
        
        # Retrieve the org owner for Tech Innovators to create campaigns
        try:
            campaign_creator_user = CustomUser.objects.get(username='org_owner1', organisation=org1)
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR('User org_owner1 for Tech Innovators Foundation not found. Cannot create campaigns.'))
            campaign_creator_user = None

        if campaign_creator_user and org1.verified:
            # Create Campaigns
            campaigns_data = [
                {
                    'organisation': org1,
                    'creator': campaign_creator_user,
                    'title': 'Launch New AI Learning Platform',
                    'goal': 50000,
                    'status': 'active',
                    'admin_remarks': 'Approved: Compelling project with clear objectives.'
                },
                {
                    'organisation': org1,
                    'creator': campaign_creator_user,
                    'title': 'Develop Community Coding Kits',
                    'goal': 25000,
                    'status': 'pending',
                    'admin_remarks': ''
                },
                {
                    'organisation': org1,
                    'creator': campaign_creator_user,
                    'title': 'Host Global Hackathon Series',
                    'goal': 75000,
                    'status': 'rejected',
                    'admin_remarks': 'Rejected: Budget unclear and lacks detailed timeline. Please revise and resubmit.'
                },
            ]

            for camp_data in campaigns_data:
                campaign, created = Campaign.objects.get_or_create(
                    title=camp_data['title'],
                    organisation=camp_data['organisation'],
                    defaults=camp_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Campaign "{campaign.title}" ({campaign.get_status_display()}) created for {org1.name}.'))
                else:
                    self.stdout.write(self.style.WARNING(f'Campaign "{campaign.title}" already exists.'))
        
        # Seed Donations for the active campaign
        try:
            active_campaign = Campaign.objects.get(title='Launch New AI Learning Platform', status='active')
            donor_user = CustomUser.objects.get(username='donor_user1')

            donations_data = [
                {'user': donor_user, 'amount': 100},
                {'user': donor_user, 'amount': 250},
                {'user': donor_user, 'amount': 50},
            ]

            for donation_data in donations_data:
                Donation.objects.create(
                    campaign=active_campaign,
                    user=donation_data['user'],
                    amount=donation_data['amount']
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(donations_data)} donations for "{active_campaign.title}".'))

        except Campaign.DoesNotExist:
            self.stdout.write(self.style.WARNING('Active campaign not found, skipping donation seeding.'))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.WARNING('Donor user not found, skipping donation seeding.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed.'))
