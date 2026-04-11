from rest_framework import serializers
from . import models
from apps.oa_auth.models import OAUser
from apps.oa_auth.serializers import UserInfoSerializer

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LeaveType
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    approver = UserInfoSerializer(read_only=True)
    applicant = UserInfoSerializer(read_only=True)
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.IntegerField()
    
    class Meta:
        model = models.Attendance
        fields = '__all__'
        
    def create(self, validated_data):
        # applicant, approver, leave_type需要后端进行绑定
        request = self.context.get('request')
        leave_type_id = validated_data.pop('leave_type_id', None)
        # 绑定applicant
        user = request.user
        validated_data['applicant'] = user
        # 绑定approver
        if user.department.name == '董事会':
            if user.department.leader.uid == user.uid:
                validated_data['approver'] = None
                validated_data['status'] = 1
            else:
                validated_data['approver'] = user.department.leader
        elif user.department.leader.uid == user.uid:
            validated_data['approver'] = user.department.manager
        else:
            validated_data['approver'] = user.department.leader
        # 绑定leave_type
        leave_type = models.LeaveType.objects.filter(pk=leave_type_id).first()
        if not leave_type:
            raise serializers.ValidationError('请假类型不存在！')
        validated_data['leave_type'] = leave_type
        #创建新的leave request
        return models.Attendance.objects.create(**validated_data)