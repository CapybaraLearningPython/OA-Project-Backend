from rest_framework.viewsets import ModelViewSet
from . import models, serializers
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Prefetch

class NotificationViewSet(ModelViewSet):
    serializer_class = serializers.NotificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        #通知可见条件为：
        # 1. 设为公开；
        # 2. 设为当前用户部门看见；
        # 3. 由当前用户创建。
        queryset = models.Notification.objects.select_related(
            'created_by'
        ).prefetch_related(
            Prefetch(
                'collection_by_notification', 
                queryset=models.NotificationStatus.objects.filter(
                    recipient_id=self.request.user.uid
                )
            ), 'departments'
        ).filter(
            Q(is_public=True)| 
            Q(departments=user.department)| 
            Q(created_by=user)
        ).distinct()
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user != instance.created_by:
            if user.department.name != '董事会' or user.uid != user.department.leader.uid:
                return Response(
                    {'detail':'没有删除的权限！'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        self.perform_destroy(instance)
        
        return Response({'message':'删除成功！'}, status=status.HTTP_204_NO_CONTENT)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.department.name != '董事会' and user.uid != user.department.leader.uid:
            return Response(
                {'detail':'没有发布通知的权限！'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

class NotificationStatusView(APIView):
    def post(self, request):
        serializer = serializers.NotificationStatusSerializer(data=request.data)
        if serializer.is_valid():
            recipient = serializer.validated_data.get('recipient')
            notification = serializer.validated_data.get('notification')
            if models.NotificationStatus.objects.filter(
                notification_id=notification.id, 
                recipient_id=recipient.uid
            ).exists():
                return Response()
            else:
                try:
                    models.NotificationStatus.objects.create(
                        notification_id=notification.id, 
                        recipient_id=recipient.uid
                    )
                    return Response()
                except Exception as e:
                    print(e)
                    return Response(
                        {'detail':str(e)}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response(
                {'detail':detail},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    def get(self, request):
        status = models.NotificationStatus.objects.filter(
            recipient_id = request.user.uid,
            notification_id = request.query_params.get('id')
        )
        
        serializer = serializers.NotificationStatusSerializer(instance=status)
        
        return Response(serializer.data)