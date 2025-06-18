from django.contrib import admin
from .models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin interface for Campaign model"""
    list_display = ('title', 'organisation', 'funding_goal', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'organisation__name')
    readonly_fields = ('created_at', 'updated_at', 'closed_at')
    raw_id_fields = ('organisation', 'created_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'funding_goal', 'category', 'cover_image')
        }),
        ('Organization', {
            'fields': ('organisation', 'created_by')
        }),
        ('Status', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
