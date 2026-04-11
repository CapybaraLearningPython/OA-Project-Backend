from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from . import models
from . import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

class AttendanceViewset(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   GenericViewSet):
    
    queryset = models.Attendance.objects.all()
    serializer_class = serializers.AttendanceSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        applicant = request.query_params.get('applicant')
        if applicant and applicant == 'sub':
            queryset = queryset.filter(approver=request.user)
        else:
            queryset = queryset.filter(applicant=request.user)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
class LeaveTypeView(APIView):
    def get(self, request):
        queryset = models.LeaveType.objects.all()
        serializer = serializers.LeaveTypeSerializer(instance=queryset, many=True)
        return Response(serializer.data)