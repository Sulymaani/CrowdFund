import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdfund.settings')

import django
django.setup()

from funding.models import Donation
from django.utils import timezone
import time

def run():
    """Add reference numbers to donations that don't have them."""
    updated = 0
    counter = 1
    
    # First, let's check what donations we need to fix
    missing_refs = list(Donation.objects.filter(reference_number__isnull=True))
    empty_refs = list(Donation.objects.filter(reference_number=''))
    print(f'Found {len(missing_refs)} donations with NULL references')
    print(f'Found {len(empty_refs)} donations with empty references')
    
    # Fix NULL references
    for donation in missing_refs:
        base_timestamp = int(timezone.now().timestamp())
        # Add counter to ensure uniqueness
        donation.reference_number = f'DON-{base_timestamp}-{donation.id}-{counter}'
        donation.save()
        updated += 1
        counter += 1
        print(f'Updated donation ID: {donation.id} with reference: {donation.reference_number}')
        # Small sleep to ensure different timestamps if needed
        time.sleep(0.01)
    
    # Fix empty string references
    for donation in empty_refs:
        base_timestamp = int(timezone.now().timestamp())
        # Add counter to ensure uniqueness
        donation.reference_number = f'DON-{base_timestamp}-{donation.id}-{counter}'
        donation.save()
        updated += 1
        counter += 1
        print(f'Updated donation ID: {donation.id} with reference: {donation.reference_number}')
        # Small sleep to ensure different timestamps if needed
        time.sleep(0.01)
    
    print(f'Total donations updated: {updated}')
    
    # Verify all donations have reference numbers now
    null_count = Donation.objects.filter(reference_number__isnull=True).count()
    empty_count = Donation.objects.filter(reference_number='').count()
    print(f'Donations with NULL reference: {null_count}')
    print(f'Donations with empty reference: {empty_count}')

if __name__ == '__main__':
    # This allows the script to be run both as a standalone script or from Django shell
    run()
