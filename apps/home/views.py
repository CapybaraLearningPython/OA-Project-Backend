from rest_framework.views import APIView
from apps.attendance import serializers as attendance_serializers
from apps.attendance import models as attendance_models
from rest_framework.response import Response
from apps.notifications import serializers as notification_serializers
from apps.notifications import models as notification_models
from django.db.models import Q, Prefetch, Count
from apps.oa_auth import models as auth_models
from django.core.cache import cache


def get_cached(cache_key, user):
    cache_key = f'{cache_key}_{user.uid}'
    cached = cache.get(cache_key)
    return cached
    
def set_cached(cache_key, user, data, timeout):
    cache_key = f'{cache_key}_{user.uid}'
    cache.set(cache_key, data, timeout)

class LatestLeaveRequestsView(APIView):
    def get(self, request):
        cache_key = 'latest_leave_requests'
        cached = get_cached(cache_key, request.user)
        if cached:
            return Response(cached)

        queryset = attendance_models.Attendance.objects.filter(
                approver_id=request.user.uid
            ).order_by('-applied_at')
        
        queryset = queryset[:10]
        serializer = attendance_serializers.AttendanceSerializer(
            instance=queryset,
            many=True
        )

        set_cached(cache_key, request.user, serializer.data, 60*15)

        return Response(serializer.data)
    
class LatestNotificationsView(APIView):
    def get(self, request):
        cache_key = 'latest_notifications'
        cached = get_cached(cache_key, request.user)
        if cached:
            return Response(cached)
        
        user = request.user
        queryset = notification_models.Notification.objects.prefetch_related(
            Prefetch(
                'collection_by_notification', 
                queryset=notification_models.NotificationStatus.objects.filter(
                    recipient_id=self.request.user.uid
                )
            ), 'departments').filter(
            Q(is_public=True)| 
            Q(departments=user.department)| 
            Q(created_by=user)
        ).distinct().order_by('-created_at')
        queryset = queryset[:10]
        serializer = notification_serializers.NotificationSerializer(
            instance=queryset,
            many=True
        )

        set_cached(cache_key, request.user, serializer.data, 60*15)

        return Response(serializer.data)
    
class StaffCountView(APIView):
    def get(self, request):
        cache_key = 'latest_staff_count'
        cached = get_cached(cache_key, request.user)
        if cached:
            return Response(cached)
        
        data = auth_models.Department.objects.annotate(
            staff_count=Count('crew')
        ).values('name', 'staff_count')

        set_cached(cache_key, request.user, list(data), 60*15)

        return Response(data)