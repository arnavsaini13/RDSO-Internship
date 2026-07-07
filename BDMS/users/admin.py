from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import UserProfile

# Unregister Group and User from Django Admin Panel
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


# Disabled registration to hide this section from Admin Panel
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('username', 'email', 'user__username')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('email', 'password', 'designation', 'phone')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
    readonly_fields = ('created_at',)

