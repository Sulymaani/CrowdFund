from django.contrib import admin
from .models import Tag

# Only register the Tag model from funding app
# Other models (Organisation, Campaign, Donation) are now registered in their respective modularized apps
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

# Note: The following admin registrations have been moved to their respective apps:
# - OrganisationAdmin → organizations/admin.py
# - CampaignAdmin → campaigns/admin.py
# - DonationAdmin → donations/admin.py
