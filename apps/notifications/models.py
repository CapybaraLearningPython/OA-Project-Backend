from django.db import models
from apps.oa_auth.models import OAUser, Department

class Notification(models.Model):
    #title, content, created_at, is_public, created_by, departments
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    is_public = models.BooleanField()
    created_by = models.ForeignKey(
        OAUser, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='my_notifications'
    )
    departments = models.ManyToManyField(Department, related_name='notifications')
    
    class Meta:
        ordering = ('-created_at',)
        
class NotificationStatus(models.Model):
    recipient = models.ForeignKey(
        OAUser, 
        on_delete=models.CASCADE, 
        related_name='collection_by_reader'
    )
    notification = models.ForeignKey(
        Notification, 
        on_delete=models.CASCADE, 
        related_name='collection_by_notification'
    )
    read_at = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recipient', 'notification']