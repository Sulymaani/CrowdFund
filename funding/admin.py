from django.contrib import admin
from .models import Organisation, Campaign, Tag, Donation

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'contact_phone', 'created_at')
    search_fields = ('name', 'website')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'organisation', 'goal', 'status', 'get_tags', 'created_at')
    list_filter = ('status', 'organisation', 'tags')
    search_fields = ('title', 'organisation__name', 'tags__name')
    filter_horizontal = ('tags',)
    
    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    
    get_tags.short_description = 'Tags'


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'amount', 'user', 'campaign', 'created_at')
    list_filter = ('campaign', 'created_at')
    search_fields = ('reference_number', 'user__username', 'user__email', 'campaign__title')
    readonly_fields = ('reference_number',)
