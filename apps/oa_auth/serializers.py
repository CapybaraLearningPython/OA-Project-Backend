from rest_framework import serializers
from . import models
from django.contrib.auth.hashers import check_password

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': '请输入邮箱！',
            'blank': '请输入邮箱！', 
            'invalid': '邮箱格式错误！'
    }
    )
    password = serializers.CharField(
        min_length=6, 
        max_length=20, 
        error_messages={
            'required': '请输入密码！', 
            'blank': '请输入密码！',
            'min_length': '密码太短！', 
            'max_length': '密码太长！'
        }
    )
    
    def validate(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = models.OAUser.objects.filter(email=email).first()
        if not email:
            raise serializers.ValidationError('请输入邮箱！')
        if not password:
            raise serializers.ValidationError('请输入密码！')
        if not user:
            raise serializers.ValidationError('用户不存在！')
        if not user.check_password(password):
            raise serializers.ValidationError('密码不正确！')
        if user.status == models.UserStatusChoices.UNACTIVATED:
            raise serializers.ValidationError('该账户未激活！')
        if user.status == models.UserStatusChoices.LOCKED:
            raise serializers.ValidationError('该账户已锁定！')
        
        validated_data['user'] = user
        
        return validated_data
    
class SimpleUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OAUser
        fields = ['name', 'uid']

class DepartmentSerializer(serializers.ModelSerializer):
    leader = SimpleUserInfoSerializer()

    class Meta:
        model = models.Department
        fields = '__all__'

class UserInfoSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    password = serializers.CharField(min_length=6, max_length=20, write_only=True)

    class Meta:
        model = models.OAUser
        exclude = ['groups', 'user_permissions', 'is_staff']

    def create(self, validated_data):
        # 部门由于嵌套了序列化器，前端不便传递整个对象
        department_id = validated_data.pop('department_id')
        try:
            department = models.Department.objects.get(id=department_id)
        except:
            raise serializers.ValidationError('部门不存在！') 
        validated_data['department'] = department

        employee = models.OAUser.objects.create_user(**validated_data)

        return employee

class ChangePasswordSerializer(serializers.Serializer):
    old_pwd = serializers.CharField(
        min_length=6, 
        max_length=20, 
        error_messages={
            'required': '请输入旧密码！', 
            'blank': '请输入旧密码！',
            'min_length': '密码太短！', 
            'max_length': '密码太长！'
        }
    )
    new_pwd1 = serializers.CharField(
        min_length=6, 
        max_length=20, 
        error_messages={
            'required': '请输入新密码！', 
            'blank': '请输入新密码！',
            'min_length': '密码太短！', 
            'max_length': '密码太长！'
        }
    )
    new_pwd2 = serializers.CharField(
        min_length=6, 
        max_length=20, 
        error_messages={
            'required': '请再次输入密码！', 
            'blank': '请再次输入密码！',
            'min_length': '密码太短！', 
            'max_length': '密码太长！'
        }
    )
    
    def validate(self, validated_data):
        request = self.context.get('request')
        user = request.user
        old_pwd = validated_data.get('old_pwd')
        new_pwd1 = validated_data.get('new_pwd1')
        new_pwd2 = validated_data.get('new_pwd2')
        if not old_pwd:
            raise serializers.ValidationError("请输入旧密码！")
        if not new_pwd1:
            raise serializers.ValidationError("请输入新密码！")
        if not new_pwd2:
            raise serializers.ValidationError("请再输入一次新密码！")
        if not user.check_password(old_pwd):
            raise serializers.ValidationError("旧密码不正确！")
        if new_pwd1 != new_pwd2:
            raise serializers.ValidationError("两次新密码输入不一致！")
        return validated_data