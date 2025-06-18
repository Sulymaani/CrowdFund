from django.contrib import admin
from django.utils.html import format_html

from .models import Organisation

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_logo', 'website', 'is_active', 'created_at', 'owner_count', 'campaign_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'website', 'mission')
    readonly_fields = ('created_at',)
    
    def display_logo(self, obj):
        """Display organization logo in the admin list view if available."""
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "No logo"
    
    display_logo.short_description = 'Logo'
    
    def owner_count(self, obj):
        """Display number of org owners."""
        return obj.owner_count
    owner_count.short_description = 'Owners'
    
    def campaign_count(self, obj):
        """Display total number of campaigns."""
        return obj.campaign_count
    campaign_count.short_description = 'Campaigns'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'website', 'mission', 'contact_phone'),
        }),
        ('Branding', {
            'fields': ('logo', 'banner'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active', 'created_at'),
        }),
    )
