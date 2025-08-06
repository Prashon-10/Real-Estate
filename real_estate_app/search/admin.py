from django.contrib import admin
from django.utils.html import format_html
from .models import SearchHistory, Recommendation

class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'query_preview',
        'property',
        'timestamp_formatted'
    )
    list_filter = ('timestamp', 'user__user_type')
    search_fields = ('user__username', 'query', 'property__title')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Search Details', {
            'fields': ('user', 'query', 'property')
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('timestamp',)
    
    def query_preview(self, obj):
        if obj.query:
            return obj.query[:100] + "..." if len(obj.query) > 100 else obj.query
        return "No query"
    query_preview.short_description = "Search Query"
    
    def timestamp_formatted(self, obj):
        if obj.timestamp:
            return obj.timestamp.strftime("%Y-%m-%d %H:%M")
        return "Unknown"
    timestamp_formatted.short_description = "Searched At"
    timestamp_formatted.admin_order_field = 'timestamp'

class RecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'property',
        'property_price',
        'score_display',
        'created_at_formatted'
    )
    list_filter = ('created_at', 'property__status', 'user__user_type')
    search_fields = ('user__username', 'property__title')
    ordering = ('-score', '-created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Recommendation Details', {
            'fields': ('user', 'property', 'score')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def property_price(self, obj):
        if obj.property and obj.property.price:
            return f"Rs. {obj.property.price:,.2f}"
        return "N/A"
    property_price.short_description = "Price"
    property_price.admin_order_field = 'property__price'
    
    def score_display(self, obj):
        if obj.score is not None:
            score_color = 'green' if obj.score >= 8 else 'orange' if obj.score >= 5 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}/10</span>',
                score_color,
                float(obj.score)
            )
        return "No score"
    score_display.short_description = "Score"
    score_display.admin_order_field = 'score'
    
    def created_at_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d %H:%M")
        return "Unknown"
    created_at_formatted.short_description = "Recommended"
    created_at_formatted.admin_order_field = 'created_at'
