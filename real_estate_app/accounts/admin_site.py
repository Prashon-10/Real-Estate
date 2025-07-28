from django.contrib import admin
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.urls import path
from accounts.models import User
from properties.models import Property, Favorite, PropertyImage, PropertyMessage
from search.models import SearchHistory, Recommendation

class RealEstateAdminSite(AdminSite):
    site_header = "🏠 RealEstate Administration"
    site_title = "RealEstate Admin"
    index_title = "Welcome to RealEstate Administration Panel"
    
    def index(self, request, extra_context=None):
        """
        Custom admin index view with statistics
        """
        extra_context = extra_context or {}
        
        # Get statistics
        extra_context.update({
            'total_users': User.objects.count(),
            'total_properties': Property.objects.count(),
            'available_properties': Property.objects.filter(status='available').count(),
            'total_favorites': Favorite.objects.count(),
            'active_agents': User.objects.filter(user_type='agent', is_active=True).count(),
            'active_customers': User.objects.filter(user_type='customer', is_active=True).count(),
            'recent_searches': SearchHistory.objects.count(),
            'pending_properties': Property.objects.filter(status='pending').count(),
            'sold_properties': Property.objects.filter(status='sold').count(),
        })
        
        return super().index(request, extra_context)

# Create an instance of the custom admin site
admin_site = RealEstateAdminSite(name='realestate_admin')

# Register models with the custom admin site
from accounts.admin import UserAdmin
from properties.admin import PropertyAdmin, PropertyImageAdmin, PropertyMessageAdmin, FavoriteAdmin

admin_site.register(User, UserAdmin)
admin_site.register(Property, PropertyAdmin)
admin_site.register(PropertyImage, PropertyImageAdmin)
admin_site.register(PropertyMessage, PropertyMessageAdmin)
admin_site.register(Favorite, FavoriteAdmin)

# Register search models
from search.admin import SearchHistoryAdmin, RecommendationAdmin
admin_site.register(SearchHistory, SearchHistoryAdmin)
admin_site.register(Recommendation, RecommendationAdmin)
