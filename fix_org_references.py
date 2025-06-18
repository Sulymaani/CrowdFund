"""
Script to fix orphaned organization references between funding_organisation and organizations_organisation tables.

This copies missing organizations from the old table to the new one, preserving IDs.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdfund.settings')
django.setup()

from django.db import connection
from organizations.models import Organisation
from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("Starting organization reference fix...")
    
    # Get existing organizations in a new table
    existing_org_ids = set(Organisation.objects.values_list('id', flat=True))
    print(f"Existing organization IDs in new table: {existing_org_ids}")
    
    # Get all users with organization references
    users_with_orgs = User.objects.filter(organisation__isnull=False)
    print(f"Users with organization references: {users_with_orgs.count()}")
    
    # Directly query the old organization table
    cursor = connection.cursor()
    cursor.execute('SELECT id, name, website, mission, contact_phone, is_active, created_at FROM funding_organisation')
    old_orgs = cursor.fetchall()
    
    # Map of old organization records
    old_orgs_map = {org[0]: org for org in old_orgs}
    print(f"Organizations in old table: {len(old_orgs_map)}")
    
    # Find users with orphaned organization references
    orphaned_users = []
    for user in users_with_orgs:
        if user.organisation_id not in existing_org_ids:
            orphaned_users.append(user)
            print(f"User {user.username} (ID: {user.id}) has orphaned reference to organization ID {user.organisation_id}")
            
            # Get the organization data from the old table
            if user.organisation_id in old_orgs_map:
                old_org = old_orgs_map[user.organisation_id]
                print(f"  Found matching organization in old table: {old_org[1]}")
                
                # Create the organization in the new table with the same ID
                new_org = Organisation(
                    id=old_org[0],
                    name=old_org[1],
                    website=old_org[2],
                    mission=old_org[3],
                    contact_phone=old_org[4],
                    is_active=old_org[5],
                    created_at=old_org[6]
                )
                
                # Save with raw SQL to preserve ID
                cursor = connection.cursor()
                cursor.execute('''
                    INSERT INTO organizations_organisation 
                    (id, name, website, mission, contact_phone, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', [
                    new_org.id, new_org.name, new_org.website, 
                    new_org.mission, new_org.contact_phone, 
                    new_org.is_active, new_org.created_at
                ])
                print(f"  Created organization {new_org.name} (ID: {new_org.id}) in new table")
            else:
                print(f"  WARNING: Could not find organization ID {user.organisation_id} in old table")
                # Set the user's organization reference to NULL
                user.organisation = None
                user.save()
                print(f"  Set user {user.username} organization reference to NULL")
    
    print(f"Fixed {len(orphaned_users)} users with orphaned organization references")
    print("Organization reference fix complete!")

if __name__ == "__main__":
    main()
