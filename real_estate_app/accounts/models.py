import random
import string
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def generate_unique_key():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(9))

def generate_verification_token():
    return str(uuid.uuid4())

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    unique_key = models.CharField(max_length=9, unique=True, default=generate_unique_key)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    
    def is_agent(self):
        return self.user_type == 'agent'
    
    def is_customer(self):
        return self.user_type == 'customer'
    
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)