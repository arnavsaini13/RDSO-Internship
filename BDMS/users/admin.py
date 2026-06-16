from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
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

