from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

class Property(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
    )
    
    LISTING_TYPE_CHOICES = (
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    )
    
    PROPERTY_TYPE_CHOICES = (
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('villa', 'Villa'),
    )
    
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, help_text="Longitude coordinate")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)
    square_footage = models.PositiveIntegerField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='sale')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='house')
    is_featured = models.BooleanField(default=False)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return self.title
    
    def get_thumbnail(self):
        """Get the first image as thumbnail"""
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return None
    
    def get_display_price(self):
        """Get formatted price for display"""
        return f"Rs. {self.price:,.0f}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images')
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.property.title} - {self.id}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.property.title}"

@receiver(post_save, sender=Property)
def remove_from_favorites_if_sold(sender, instance, **kwargs):
    if instance.status == 'sold':
        Favorite.objects.filter(property=instance).delete()

@receiver(pre_delete, sender=Property)
def remove_from_favorites_if_deleted(sender, instance, **kwargs):
    Favorite.objects.filter(property=instance).delete()



#Testing
from django.contrib.auth import get_user_model

User = get_user_model()


class PropertyMessage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} on {self.property.title}"


class PropertyBooking(models.Model):
    """Model to store property booking information with payment details"""
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe (International)'),
        ('esewa', 'eSewa (Nepal)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    BOOKING_TYPE_CHOICES = [
        ('booking', 'Property Booking'),
        ('visit', 'Property Visit Request'),
    ]
    
    # Basic Information
    property_ref = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default='booking')
    
    # Customer Details
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Visit Details (for visit requests)
    preferred_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True, help_text="Additional message or requirements")
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='completed')
    payment_data = models.JSONField(blank=True, null=True, help_text="Store payment gateway response")
    
    # Booking Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Admin verification notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_bookings'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property Booking'
        verbose_name_plural = 'Property Bookings'
    
    def __str__(self):
        return f"{self.customer_name} - {self.property_ref.title} ({self.get_booking_type_display()})"
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.status in ['confirmed', 'rejected'] and not self.verified_at:
            self.verified_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_visit_request(self):
        return self.booking_type == 'visit'
    
    @property
    def can_be_verified(self):
        return self.status == 'pending'


class BookingFee(models.Model):
    """Model to store booking fee configuration"""
    
    booking_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=500.00,
        help_text="Booking fee amount in NPR"
    )
    visit_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=200.00,
        help_text="Visit request fee amount in NPR"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking Fee Configuration'
        verbose_name_plural = 'Booking Fee Configurations'
    
    def __str__(self):
        return f"Booking: NPR {self.booking_fee} | Visit: NPR {self.visit_fee}"
    
    @classmethod
    def get_current_fees(cls):
        """Get the current active booking fees"""
        fee_config = cls.objects.filter(is_active=True).first()
        if fee_config:
            return {
                'booking_fee': fee_config.booking_fee,
                'visit_fee': fee_config.visit_fee
            }
        return {
            'booking_fee': 500.00,  # Default values
            'visit_fee': 200.00
        }