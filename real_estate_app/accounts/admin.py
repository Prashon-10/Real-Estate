from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 
        'email', 
        'full_name',
        'user_type', 
        'is_active', 
        'date_joined',
        'last_login_display'
    )
    list_filter = (
        'user_type', 
        'is_active', 
        'is_staff', 
        'date_joined',
        'last_login'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('user_type', 'profile_image', 'phone_number', 'unique_key')
        }),
    )
    
    readonly_fields = ('unique_key', 'date_joined', 'last_login')
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "-"
    full_name.short_description = "Name"
    
    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%Y-%m-%d %H:%M")
        return "Never"
    last_login_display.short_description = "Last Login"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

# Customize admin site headers
admin.site.site_header = "RealEstate Administration"
admin.site.site_title = "RealEstate Admin"
admin.site.index_title = "Welcome to RealEstate Administration Panel"