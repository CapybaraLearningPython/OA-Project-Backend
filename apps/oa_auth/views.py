from rest_framework.views import APIView
from . import serializers
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from .authentications import generate_jwt
from rest_framework.permissions import AllowAny


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token = generate_jwt(user)
            user_info = serializers.UserInfoSerializer(instance=user).data
            return Response({'message':'登录成功！', 'token':token, 'user':user_info})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({'detail':detail}, status=status.HTTP_403_FORBIDDEN)
        
class ChangePasswordView(APIView):
    def post(self, request):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data, 
            context={'request':request}
        )
        user = request.user
        if serializer.is_valid():
            new_pwd = serializer.validated_data.get('new_pwd1')
            user.set_password(new_pwd)
            user.save()
            return Response({'message':'密码修改成功！'})
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({'detail':detail}, status=status.HTTP_400_BAD_REQUEST)