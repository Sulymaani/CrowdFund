from django.contrib import admin
from .models import Organisation, Campaign

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'verified', 'created_at')
    list_filter = ('verified',)
    search_fields = ('name',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'organisation', 'goal', 'status', 'created_at')
    list_filter = ('status', 'organisation')
    search_fields = ('title', 'organisation__name')

