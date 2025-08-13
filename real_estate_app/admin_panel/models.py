from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache


class SystemSettings(models.Model):
    """Model to store system-wide settings"""
    
    # Site Information
    site_name = models.CharField(max_length=100, default="Real Estate Platform")
    contact_email = models.EmailField(default="admin@realestate.com")
    phone_number = models.CharField(max_length=20, default="+1 (555) 123-4567")
    business_address = models.TextField(default="123 Business St, City")
    site_description = models.TextField(
        default="Your trusted real estate platform for buying, selling, and renting properties."
    )
    
    # Platform Limits
    max_properties_per_agent = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    max_images_per_property = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    booking_expiry_days = models.PositiveIntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    
    # Feature Toggles
    allow_registration = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    auto_approve_listings = models.BooleanField(default=True)
    require_email_verification = models.BooleanField(default=True)
    
    # Email Settings
    smtp_host = models.CharField(max_length=255, default="smtp.gmail.com")
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True)
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)
    from_email = models.EmailField(default="noreply@realestate.com")
    from_name = models.CharField(max_length=100, default="RealEstate Platform")
    
    # Security Settings
    session_timeout_minutes = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(1440)]
    )
    max_login_attempts = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    
    # System Info
    last_backup = models.DateTimeField(null=True, blank=True)
    storage_used_gb = models.DecimalField(max_digits=10, decimal_places=2, default=2.4)
    uptime_days = models.PositiveIntegerField(default=15)
    uptime_hours = models.PositiveIntegerField(default=7)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def __str__(self):
        return f"System Settings - {self.site_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'Real Estate Platform',
                'contact_email': 'admin@realestate.com',
            }
        )
        return settings
    
    def save(self, *args, **kwargs):
        # Clear cache when settings are updated
        cache.delete('system_settings')
        super().save(*args, **kwargs)
    
    @classmethod
    def cached_settings(cls):
        """Get cached settings"""
        settings = cache.get('system_settings')
        if not settings:
            settings = cls.get_settings()
            cache.set('system_settings', settings, 3600)  # Cache for 1 hour
        return settings
