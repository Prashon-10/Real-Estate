from django.db import models
from django.conf import settings
from properties.models import Property

class ChatRoom(models.Model):
    """
    Chat room for conversations between customer and agent about a property
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='chatrooms')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_chats')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('property', 'customer', 'agent')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat: {self.customer.username} - {self.agent.username} ({self.property.title})"


class ChatMessage(models.Model):
    """
    Individual messages in a chat room
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
