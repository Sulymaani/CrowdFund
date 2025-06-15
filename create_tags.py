#!/usr/bin/env python
"""
Script to create default tags for campaigns.
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdfund.settings')
django.setup()

from funding.models import Tag
from django.utils.text import slugify

def main():
    # List of default tags to create
    default_tags = [
        {'name': 'Education', 'description': 'Educational initiatives and scholarship programs'},
        {'name': 'Health', 'description': 'Medical expenses, healthcare initiatives, and wellness programs'},
        {'name': 'Environment', 'description': 'Environmental conservation, climate action, and sustainability'},
        {'name': 'Community', 'description': 'Community development and local initiatives'},
        {'name': 'Technology', 'description': 'Technology, innovation, and digital projects'},
        {'name': 'Arts', 'description': 'Arts, culture, creative projects, and performances'},
        {'name': 'Emergency Relief', 'description': 'Disaster response, emergency aid, and crisis support'},
        {'name': 'Children', 'description': 'Programs focusing on children and youth welfare'},
        {'name': 'Animals', 'description': 'Animal welfare, rescue, and conservation efforts'},
        {'name': 'Other', 'description': 'Miscellaneous campaigns that don\'t fit other categories'}
    ]
    
    # Create tags if they don't exist
    created_count = 0
    existing_count = 0
    
    for tag_info in default_tags:
        tag, created = Tag.objects.get_or_create(
            name=tag_info['name'],
            defaults={
                'slug': slugify(tag_info['name']),
                'description': tag_info['description']
            }
        )
        
        if created:
            created_count += 1
            print(f"Created tag: {tag.name}")
        else:
            existing_count += 1
            print(f"Tag already exists: {tag.name}")
    
    print(f"\nCompleted! Created {created_count} new tags, {existing_count} already existed.")
    
    # Show all available tags
    all_tags = Tag.objects.all()
    print(f"\nAll available tags ({all_tags.count()}):")
    for tag in all_tags:
        print(f"- {tag.name} (slug: {tag.slug})")

if __name__ == "__main__":
    main()
