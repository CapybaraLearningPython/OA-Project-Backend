from rest_framework import serializers
from . import models
from apps.oa_auth import serializers as auth_serializers
from apps.oa_auth import models as auth_models

class NotificationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NotificationStatus
        fields = '__all__'
        # serializer校验暂时屏蔽掉unique校验，
        # 否则同时传入recipient和notification两个参数之后
        # is_valid检验不通过会直接报错跳过后续校验逻辑
        # 无法根据设计的错误捕获逻辑运行
        # 因此仅在数据库层面进行unique校验，为高并发兜底
        validators = []
    

class NotificationSerializer(serializers.ModelSerializer):
    #title, content, created_at, is_public, created_by, departments
    created_by = auth_serializers.UserInfoSerializer(read_only=True)
    departments = auth_serializers.DepartmentSerializer(read_only=True, many=True)
    department_ids = serializers.ListField(write_only=True)
    is_public = serializers.BooleanField(read_only=True)
    collection_by_notification = NotificationStatusSerializer(read_only=True, many=True)
    # 模型不包含count字段，该字段为只读额外字段，单独定义序列化逻辑，视图调用retrieve方法时，一并返回该字段
    read_count = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Notification
        fields = '__all__'
        
    #手动绑定created_by、departments、is_public
    def create(self, validated_data):
        request = self.context.get('request')
        
        #绑定created_by
        user = request.user
        validated_data['created_by'] = user
        
        #绑定is_public
        department_ids = validated_data.pop('department_ids')
        department_ids = list(map(lambda value: int(value), department_ids))
        if 0 in department_ids:
           validated_data['is_public'] = True
        else:
            validated_data['is_public'] = False
            
        #创建notification实例
        notification = models.Notification.objects.create(**validated_data)
        
        #绑定departments
        departments = auth_models.Department.objects.filter(id__in=department_ids)
        notification.departments.set(departments)
        
        return notification
        
    def get_read_count(self, instance):
        return models.NotificationStatus.objects.filter(notification=instance).count()