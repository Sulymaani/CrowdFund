from django.contrib import admin
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    """Admin interface for Donation model"""
    list_display = ('reference_number', 'campaign', 'donor', 'amount', 'created_at')
    list_filter = ('created_at', 'campaign__status')
    search_fields = ('reference_number', 'campaign__title', 'donor__email', 'comment')
    readonly_fields = ('created_at', 'reference_number')
    raw_id_fields = ('campaign', 'donor')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reference_number', 'amount', 'comment')
        }),
        ('Relationships', {
            'fields': ('campaign', 'donor')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        # Optimize query with select_related to avoid N+1 queries
        return super().get_queryset(request).select_related('campaign', 'donor')
