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
    
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)
    square_footage = models.PositiveIntegerField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return self.title

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