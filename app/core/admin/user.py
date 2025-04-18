"""
Django admin customization
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import User


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['id', 'email', 'name']
    search_fields = ['email', 'name']
    # # list_filter = ['user_type', 'created_at']
    fieldsets = (
        (None, {'fields': ('id', 'email',)}),
        (_('Personal Info'), {'fields': ('name',)}),
        # (_('Device Info'), {'fields': ('device_token',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
        # (_('Linked To'), {
        #     'fields': ('dog_profile', 'service_profile', 'apparel_profile')
        # }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'name',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make email readonly only when editing (not on add)."""
        if obj:  # editing existing object
            return ['id', 'email', 'last_login']
        return ['id', 'last_login']


admin.site.register(User, UserAdmin)
