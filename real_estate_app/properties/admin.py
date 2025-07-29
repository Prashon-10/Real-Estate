from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from .models import Property, PropertyImage, PropertyMessage, Favorite, PropertyBooking, BookingFee

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 80px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'address_short',
        'price_formatted',
        'bedrooms',
        'bathrooms',
        'status_colored',
        'agent',
        'created_at_formatted',
        'has_images'
    )
    list_filter = (
        'status',
        'bedrooms',
        'bathrooms',
        'agent',
        'created_at'
    )
    search_fields = ('title', 'address', 'description', 'agent__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Property Information', {
            'fields': ('title', 'address', 'price', 'description')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_footage')
        }),
        ('Status & Agent', {
            'fields': ('status', 'agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline]
    
    def address_short(self, obj):
        if obj.address:
            return obj.address[:50] + "..." if len(obj.address) > 50 else obj.address
        return "No address"
    address_short.short_description = "Address"
    
    def price_formatted(self, obj):
        if obj.price is not None:
            return f"${obj.price:,.2f}"
        return "No price"
    price_formatted.short_description = "Price"
    price_formatted.admin_order_field = 'price'
    
    def status_colored(self, obj):
        colors = {
            'available': 'green',
            'sold': 'red',
            'pending': 'orange'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = "Status"
    status_colored.admin_order_field = 'status'
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_formatted.short_description = "Created"
    created_at_formatted.admin_order_field = 'created_at'
    
    def has_images(self, obj):
        count = obj.images.count()
        if count > 0:
            return format_html(
                '<span style="color: green;">✓ {} images</span>',
                count
            )
        return format_html('<span style="color: red;">No images</span>')
    has_images.short_description = "Images"

class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image_preview', 'order')
    list_filter = ('property__status',)
    search_fields = ('property__title',)
    ordering = ('property', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 80px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

class PropertyMessageAdmin(admin.ModelAdmin):
    list_display = (
        'property',
        'sender',
        'message_preview',
        'timestamp_formatted',
        'read_status'
    )
    list_filter = ('timestamp', 'read', 'sender__user_type')
    search_fields = ('property__title', 'sender__username', 'content')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('property', 'sender', 'content', 'read')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('timestamp',)
    
    def message_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    message_preview.short_description = "Message"
    
    def timestamp_formatted(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M")
    timestamp_formatted.short_description = "Sent"
    timestamp_formatted.admin_order_field = 'timestamp'
    
    def read_status(self, obj):
        if obj.read:
            return format_html('<span style="color: green;">✓ Read</span>')
        else:
            return format_html('<span style="color: orange;">Unread</span>')
    read_status.short_description = "Status"

class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'property',
        'property_price',
        'property_status',
        'added_at_formatted'
    )
    list_filter = ('added_at', 'property__status', 'user__user_type')
    search_fields = ('user__username', 'property__title')
    ordering = ('-added_at',)
    date_hierarchy = 'added_at'
    
    def property_price(self, obj):
        return f"${obj.property.price:,.2f}"
    property_price.short_description = "Price"
    property_price.admin_order_field = 'property__price'
    
    def property_status(self, obj):
        colors = {
            'available': 'green',
            'sold': 'red',
            'pending': 'orange'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.property.status, 'black'),
            obj.property.get_status_display()
        )
    property_status.short_description = "Status"
    
    def added_at_formatted(self, obj):
        return obj.added_at.strftime("%Y-%m-%d %H:%M")
    added_at_formatted.short_description = "Added"
    added_at_formatted.admin_order_field = 'added_at'


class PropertyBookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name',
        'property_title',
        'booking_type_display',
        'payment_method_display',
        'payment_amount_formatted',
        'status_colored',
        'created_at_formatted'
    )
    list_filter = ('status', 'booking_type', 'payment_method', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'property_ref__title', 'transaction_id')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Booking Details', {
            'fields': ('property_ref', 'booking_type', 'preferred_date', 'message')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'transaction_id', 'payment_amount', 'payment_status', 'payment_data')
        }),
        ('Status & Verification', {
            'fields': ('status', 'admin_notes', 'verified_by', 'verified_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    
    def property_title(self, obj):
        return obj.property_ref.title
    property_title.short_description = "Property"
    
    def booking_type_display(self, obj):
        return obj.get_booking_type_display()
    booking_type_display.short_description = "Type"
    
    def payment_method_display(self, obj):
        return obj.get_payment_method_display()
    payment_method_display.short_description = "Payment Method"
    
    def payment_amount_formatted(self, obj):
        return f"NPR {obj.payment_amount:,.2f}"
    payment_amount_formatted.short_description = "Amount"
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'rejected': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = "Status"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_formatted.short_description = "Created"
    created_at_formatted.admin_order_field = 'created_at'


class BookingFeeAdmin(admin.ModelAdmin):
    list_display = (
        'booking_fee_formatted',
        'visit_fee_formatted',
        'is_active',
        'created_at_formatted'
    )
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)
    
    def booking_fee_formatted(self, obj):
        return f"NPR {obj.booking_fee:,.2f}"
    booking_fee_formatted.short_description = "Booking Fee"
    
    def visit_fee_formatted(self, obj):
        return f"NPR {obj.visit_fee:,.2f}"
    visit_fee_formatted.short_description = "Visit Fee"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_formatted.short_description = "Created"
    created_at_formatted.admin_order_field = 'created_at'


# Register models
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyMessage, PropertyMessageAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(PropertyBooking, PropertyBookingAdmin)
admin.site.register(BookingFee, BookingFeeAdmin)