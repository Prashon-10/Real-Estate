from django.db import models
from django.conf import settings
from properties.models import Property

class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_history')
    query = models.TextField()
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Search histories'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.query}"

class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    score = models.FloatField()  # Relevance score
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.property.title} ({self.score})"