#!/usr/bin/env python
"""
Script to assign default tags to campaigns that don't have any tags.
Run this script as a one-time operation to ensure all campaigns have at least one tag.
"""
import os
import django
import random
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdfund.settings')
django.setup()

from funding.models import Campaign, Tag

def main():
    # Get all campaigns that don't have any tags
    campaigns_without_tags = Campaign.objects.filter(tags__isnull=True).distinct()
    
    # Get all available tags
    all_tags = list(Tag.objects.all())
    
    if not all_tags:
        print("Error: No tags found in the database. Please create tags first.")
        sys.exit(1)
    
    # Count of campaigns to update
    count = campaigns_without_tags.count()
    print(f"Found {count} campaigns without tags.")
    
    if count == 0:
        print("All campaigns already have tags. Nothing to do.")
        return
        
    # Create default tags if they don't exist
    default_tags = ['General', 'Other']
    for tag_name in default_tags:
        Tag.objects.get_or_create(name=tag_name)
    
    # Refresh tag list after potential additions
    all_tags = list(Tag.objects.all())
    
    # Process each campaign
    for i, campaign in enumerate(campaigns_without_tags, 1):
        # Assign 1-3 random tags to each campaign
        num_tags = random.randint(1, min(3, len(all_tags)))
        selected_tags = random.sample(all_tags, num_tags)
        
        # Add tags to the campaign
        for tag in selected_tags:
            campaign.tags.add(tag)
        
        print(f"[{i}/{count}] Added tags to campaign: {campaign.title}")
        tag_names = ", ".join([t.name for t in selected_tags])
        print(f"    Tags: {tag_names}")
    
    print(f"\nCompleted! Added tags to {count} campaigns.")

if __name__ == "__main__":
    main()
