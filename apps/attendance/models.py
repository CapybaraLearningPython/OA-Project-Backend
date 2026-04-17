from django.db import models
from apps.oa_auth.models import OAUser

class LeaveType(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateField(auto_now_add=True)
    
class RequestStatus(models.IntegerChoices):
    APPROVED = 1
    REJECTED = 2
    UNDER_REVIEW = 3

class Attendance(models.Model):
    applicant = models.ForeignKey(
        OAUser, 
        on_delete=models.CASCADE, 
        related_name='my_requests'
    )
    detail = models.TextField()
    leave_type = models.ForeignKey(
        LeaveType, 
        on_delete=models.SET_NULL, 
        null=True
    )
    approver = models.ForeignKey(
        OAUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sub_requests'
    )
    status = models.IntegerField(
        choices=RequestStatus.choices, 
        default=RequestStatus.UNDER_REVIEW
    )
    leave_start = models.DateField()
    leave_end = models.DateField()
    applied_at = models.DateField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-applied_at']