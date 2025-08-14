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
        """Get the primary image as thumbnail, fallback to first image"""
        # Try to get the primary image first
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        
        # Fallback to the first image if no primary image is set
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return None
    
    def get_primary_image(self):
        """Get the primary image object"""
        return self.images.filter(is_primary=True).first()
    
    def get_display_price(self):
        """Get formatted price for display"""
        return f"Rs. {self.price:,.0f}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images')
    caption = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def save(self, *args, **kwargs):
        # If this image is being set as primary, ensure no other images for this property are primary
        if self.is_primary:
            PropertyImage.objects.filter(property=self.property, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
    
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
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('authorized', 'Payment Authorized (Hold)'),
        ('captured', 'Payment Captured (Charged)'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Payment Refunded'),
        ('cancelled', 'Payment Cancelled'),
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
    additional_properties = models.TextField(
        blank=True, 
        help_text="Comma-separated list of additional property IDs for multi-property visits"
    )
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    payment_intent_id = models.CharField(max_length=255, blank=True, help_text="Stripe Payment Intent ID for authorization/capture")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_data = models.JSONField(blank=True, null=True, help_text="Store payment gateway response")
    
    # Payment timestamps
    payment_authorized_at = models.DateTimeField(null=True, blank=True, help_text="When payment was authorized (money held)")
    payment_captured_at = models.DateTimeField(null=True, blank=True, help_text="When payment was captured (money charged)")
    payment_refunded_at = models.DateTimeField(null=True, blank=True, help_text="When payment was refunded")
    
    # Booking Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Admin verification notes")
    
    # Visit Completion Fields (for visit requests)
    visit_completed = models.BooleanField(default=False, help_text="Whether the visit has been completed")
    visit_completed_at = models.DateTimeField(null=True, blank=True, help_text="When the visit was completed")
    visit_completed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='completed_visits',
        help_text="Agent who marked the visit as completed"
    )
    
    # Dual Confirmation System
    agent_confirmed_completion = models.BooleanField(default=False, help_text="Agent confirmed visit completion")
    agent_confirmation_at = models.DateTimeField(null=True, blank=True, help_text="When agent confirmed completion")
    customer_confirmed_completion = models.BooleanField(default=False, help_text="Customer confirmed visit completion")
    customer_confirmation_at = models.DateTimeField(null=True, blank=True, help_text="When customer confirmed completion")
    
    # Only available after both confirmations
    can_book_after_visit = models.BooleanField(default=True, help_text="Whether customer can book after completing visit")
    booking_deadline = models.DateTimeField(null=True, blank=True, help_text="Deadline for booking after visit completion")

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
    
    @property
    def is_visit_completed(self):
        """Check if this is a completed visit with dual confirmation"""
        try:
            agent_confirmed = getattr(self, 'agent_confirmed_completion', False)
            customer_confirmed = getattr(self, 'customer_confirmed_completion', False)
            return (self.is_visit_request and 
                    agent_confirmed and 
                    customer_confirmed and 
                    self.visit_completed)
        except AttributeError:
            # Fallback for when columns don't exist yet
            return (self.is_visit_request and self.visit_completed)
    
    @property
    def is_pending_customer_confirmation(self):
        """Check if agent confirmed but waiting for customer confirmation"""
        try:
            agent_confirmed = getattr(self, 'agent_confirmed_completion', False)
            customer_confirmed = getattr(self, 'customer_confirmed_completion', False)
            return (self.is_visit_request and 
                    agent_confirmed and 
                    not customer_confirmed)
        except AttributeError:
            return False
    
    @property
    def is_pending_agent_confirmation(self):
        """Check if customer confirmed but waiting for agent confirmation"""
        try:
            agent_confirmed = getattr(self, 'agent_confirmed_completion', False)
            customer_confirmed = getattr(self, 'customer_confirmed_completion', False)
            return (self.is_visit_request and 
                    customer_confirmed and 
                    not agent_confirmed)
        except AttributeError:
            return False
    
    @property
    def booking_deadline_display(self):
        """Human-readable booking deadline"""
        if self.booking_deadline:
            return self.booking_deadline.strftime('%B %d, %Y at %I:%M %p')
        return None
    
    @property
    def can_book_now(self):
        """Check if customer can book after completing visit"""
        if not self.is_visit_completed:
            return False
        if not self.can_book_after_visit:
            return False
        if self.booking_deadline:
            from django.utils import timezone
            return timezone.now() <= self.booking_deadline
        return True

    @property
    def payment_display_status(self):
        """Human-readable payment status"""
        status_mapping = {
            'pending': 'Payment Pending',
            'authorized': 'Payment on Hold (Will be charged on confirmation)',
            'captured': 'Payment Completed',
            'failed': 'Payment Failed',
            'refunded': 'Payment Refunded',
            'cancelled': 'Payment Cancelled'
        }
        return status_mapping.get(self.payment_status, self.payment_status.title())
    
    def authorize_payment(self):
        """Authorize payment (hold money without charging)"""
        from django.utils import timezone
        if self.payment_status == 'pending':
            # In real implementation, this would call Stripe payment authorization
            self.payment_status = 'authorized'
            self.payment_authorized_at = timezone.now()
            self.save()
            return True
        return False
    
    def capture_payment(self):
        """Capture authorized payment (actually charge the money)"""
        from django.utils import timezone
        if self.payment_status == 'authorized':
            # In real implementation, this would call Stripe payment capture
            self.payment_status = 'captured'
            self.payment_captured_at = timezone.now()
            self.save()
            return True
        return False
    
    def refund_payment(self):
        """Refund captured payment"""
        from django.utils import timezone
        if self.payment_status == 'captured':
            # In real implementation, this would call Stripe refund
            self.payment_status = 'refunded'
            self.payment_refunded_at = timezone.now()
            self.save()
            return True
        return False
    
    def cancel_authorization(self):
        """Cancel payment authorization (release held money)"""
        if self.payment_status == 'authorized':
            self.payment_status = 'cancelled'
            self.save()
            return True
        return False
    
    def reauthorize_payment(self):
        """Re-authorize a previously cancelled payment"""
        from django.utils import timezone
        if self.payment_status == 'cancelled':
            # In real implementation, this would create a new payment intent
            self.payment_status = 'authorized'
            self.payment_authorized_at = timezone.now()
            self.save()
            return True
        return False
    
    def complete_visit(self, completed_by_user, booking_deadline_days=7):
        """Mark visit as completed and set booking deadline (DEPRECATED - use confirm_visit_completion)"""
        return self.confirm_visit_completion(completed_by_user, booking_deadline_days)
    
    def confirm_visit_completion(self, confirming_user, booking_deadline_days=7):
        """Agent or customer confirms visit completion"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.is_visit_request or self.status != 'confirmed':
            return False
        
        try:
            # Check if this is agent confirmation
            if confirming_user == self.property_ref.agent:
                agent_confirmed = getattr(self, 'agent_confirmed_completion', False)
                if not agent_confirmed:
                    self.agent_confirmed_completion = True
                    self.agent_confirmation_at = timezone.now()
                    self.visit_completed_by = confirming_user
            
            # Check if this is customer confirmation  
            elif confirming_user == self.customer:
                customer_confirmed = getattr(self, 'customer_confirmed_completion', False)
                if not customer_confirmed:
                    self.customer_confirmed_completion = True
                    self.customer_confirmation_at = timezone.now()
            
            else:
                return False  # User not authorized to confirm
            
            # If both have confirmed, mark visit as fully completed
            agent_confirmed = getattr(self, 'agent_confirmed_completion', False)
            customer_confirmed = getattr(self, 'customer_confirmed_completion', False)
            if agent_confirmed and customer_confirmed:
                if not self.visit_completed:
                    self.visit_completed = True
                    self.visit_completed_at = timezone.now()
                    self.can_book_after_visit = True
                    self.booking_deadline = timezone.now() + timedelta(days=booking_deadline_days)
            
        except AttributeError:
            # Fallback to old behavior if columns don't exist
            if not self.visit_completed:
                self.visit_completed = True
                self.visit_completed_at = timezone.now()
                self.visit_completed_by = confirming_user
                self.can_book_after_visit = True
                self.booking_deadline = timezone.now() + timedelta(days=booking_deadline_days)
        
        self.save()
        return True
    
    def get_confirmation_status(self):
        """Get human-readable confirmation status"""
        if not self.is_visit_request:
            return "Not a visit request"
        
        try:
            agent_confirmed = getattr(self, 'agent_confirmed_completion', False)
            customer_confirmed = getattr(self, 'customer_confirmed_completion', False)
            
            if self.visit_completed:
                return "Visit completed (both parties confirmed)"
            elif agent_confirmed and customer_confirmed:
                return "Both confirmed - processing completion"
            elif agent_confirmed:
                return "Agent confirmed - waiting for customer"
            elif customer_confirmed:
                return "Customer confirmed - waiting for agent"
            else:
                return "Visit pending - no confirmations yet"
        except AttributeError:
            # Fallback if columns don't exist
            if self.visit_completed:
                return "Visit completed"
            else:
                return "Visit pending completion"


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
        default=500.00,
        help_text="Visit request fee amount in NPR (same as booking fee)"
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
            'booking_fee': 500.00,  # Updated default values
            'visit_fee': 500.00
        }