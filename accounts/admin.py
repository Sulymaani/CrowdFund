from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'organisation', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'organisation__name')
    ordering = ('username',)

    # Add 'role' and 'organisation' to fieldsets for the add/change forms
    # This extends the default UserAdmin fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Role and Organisation', {'fields': ('role', 'organisation')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role and Organisation', {'fields': ('role', 'organisation')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

