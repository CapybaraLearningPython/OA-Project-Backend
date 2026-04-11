from rest_framework.views import APIView
from apps.oa_auth.serializers import DepartmentSerializer
from apps.oa_auth.models import Department
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from apps.oa_auth import serializers as auth_serializers
from apps.oa_auth import models as auth_models
from . import pagination
from rest_framework import status
from .tasks import send_email, generate_activation_jwt
from django.urls import reverse
from urllib import parse
from django.views import View
from django.shortcuts import render
import jwt
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from . import serializers
import pandas as pd
from django.db import transaction

def send_activation_email(request, user):
    print(f'uid: {user.uid}')
    token = generate_activation_jwt(user.uid)
    print(f'token: {token}')
    activation_path = reverse('staff:activation') + '?' + parse.urlencode(
        {'token':token}
    )
    print(f'path: {activation_path}')
    activation_url = request.build_absolute_uri(activation_path)
    print(f'url: {activation_url}')
    send_email.delay(user.email, activation_url)
    print('delay called')

class DepartmentView(APIView):
    def get(self, request):
        queryset = Department.objects.all()
        serializer = DepartmentSerializer(queryset, many=True)
        return Response(serializer.data)
    
class StaffViewSet(ListModelMixin, 
                    CreateModelMixin, 
                    UpdateModelMixin, 
                    GenericViewSet):
    serializer_class = auth_serializers.UserInfoSerializer
    queryset = auth_models.OAUser.objects.all()
    pagination_class = pagination.StaffListPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        # 默认按部门进行基础筛选
        if user.department.name == '董事会':
            queryset = queryset
        else:
            department_id = user.department.id
            queryset = queryset.filter(department_id=department_id)
        
        # 按筛选条件进行进一步手动筛选
        conditions = self.request.query_params
        key_words = conditions.get('key_words')
        department_ids_str = conditions.getlist('department_ids')
        department_ids = list(map(lambda value: int(value), department_ids_str))
        date_joined = conditions.getlist('date_joined')
        if key_words:
            queryset = queryset.filter(name__icontains=key_words)
        if department_ids:
            queryset = queryset.filter(department_id__in=department_ids)
        if date_joined:
            queryset = queryset.filter(
                date_joined__gte=date_joined[0],
                date_joined__lte=date_joined[1]
            )
        
        return queryset

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        user = request.user
        target = self.get_object()
        president = auth_models.Department.objects.get(name='董事会').leader
        if user.department.name != '董事会' and user.uid != user.department.leader.uid:
            return Response(
                {'detail':'没有修改的权限！'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.uid == target.uid and user.uid != president.uid:
            return Response(
                {'detail': '不能修改自己的账号状态！'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.department.name != '董事会' and user.uid != user.department.leader.uid:
            return Response(
                {'detail':'没有新增员工的权限！'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 在创建完成后附加邮件发送操作
        user = serializer.save()
        send_activation_email(self.request, user)

class EmployeeActivationView(View):
    def get(self, request):
        # 从url中获取token并解码拿到用户uid
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            uid = payload['userid']
            employee = auth_models.OAUser.objects.get(uid=uid)
            employee.status = auth_models.UserStatusChoices.ACTIVATED
            employee.save()
        except jwt.ExpiredSignatureError:
            return JsonResponse({'detail': '链接已过期!'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({'detail': '无效链接!'}, status=400)
        except auth_models.OAUser.DoesNotExist:
            return JsonResponse({'detail': '用户不存在!'}, status=400)
        
        return render(request, 'activation_successful.html')
    
class StaffUploadView(APIView):
    def post(self, request):
        serializer = serializers.StaffUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data.get('file')
            user = request.user

            # 基础权限判断
            if user.uid != user.department.leader.uid and user.department.name != '董事会':
                return Response(
                    {'detail':'没有上传文件的权限！'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            staff_df = pd.read_excel(file)
            employees = []

            for index, row in staff_df.iterrows():
                # 为表格中每个员工绑定部门
                # 非董事会成员只能添加本部门员工
                if user.department.name != '董事会':
                    department = user.department
                else:
                    try:
                        department = auth_models.Department.objects.get(name=row['所属部门'])
                    # 捕获查找不到对应部门的错误
                    except auth_models.Department.DoesNotExist:
                        return Response(
                            {'detail':f"{row['所属部门']}不存在！"},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    # 捕获表格中没提供部门列的错误
                    except KeyError:
                        return Response(
                            {'detail':'部门列不存在！'},
                            status=status.HTTP_404_NOT_FOUND
                        )

                    # 绑定姓名、邮箱、密码
                try:
                    email = row['员工邮箱']
                    name = row['员工姓名']
                    password = 'abc123'
                    # 创建单个员工实例
                    employee = auth_models.OAUser(
                        name=name,
                        email=email,
                        department=department
                    )
                    employee.set_password(password)
                    employees.append(employee)
                except Exception as e:
                    print(e)
                    return Response(
                        {'detail':'请检查表格中姓名和邮箱是否正确填写！'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            try:
                with transaction.atomic():
                    auth_models.OAUser.objects.bulk_create(employees)
                
            except Exception as e:
                print(e)
                return Response(
                    {'detail':'员工数据添加失败，请稍后再试！'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            for employee in employees:
                try:
                    send_activation_email(request, employee)
                except Exception as e:
                    detail = f'员工数据已添加，发送激活邮件失败：{employee.email}，{e}'
                    print(detail)
                
            return Response()
        
        else:
            detail = list(serializer.errors.values())[0][0]
            return Response({'detail':detail}, status=status.HTTP_400_BAD_REQUEST)
        
class StaffDownloadView(APIView):
    def get(self, request):
        try:
            employee_ids = request.query_params.getlist('employee_ids')
            queryset = auth_models.OAUser.objects.filter(uid__in=employee_ids)

        except AttributeError:
            return Response(
                {'detail':'无法获取员工uid列表！'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # filter不会抛出错误，手动捕获
        if not queryset.exists():
            return Response(
                {'detail': '找不到对应的员工！'},
                status=status.HTTP_404_NOT_FOUND
             )

        user = request.user
        if user.department.name != '董事会' and user.uid != user.department.leader.uid:
            return Response(
                {'detail':'没有下载的权限！'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = queryset.values(
            'name', 'email', 'department__name', 'date_joined', 'status'
        )

        try:
            staff_df = pd.DataFrame(list(result))
            staff_df = staff_df.rename(
                columns={
                    'name': '员工姓名',
                    'email': '员工邮箱',
                    'department__name': '所属部门',
                    'date_joined': '入职时间',
                    'status':'员工状态'
                }
            )

            status_map = {1: '已激活', 2:'未激活', 3:'已锁定'}
            staff_df['员工状态'] = staff_df['员工状态'].map(status_map)
            
            res = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            filename = parse.quote('员工信息.xlsx')
            res['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'

            with pd.ExcelWriter(res) as writer:
                staff_df.to_excel(writer, sheet_name='员工信息')
            return res
        
        except Exception as e:
            print(e)
            return Response(
                {'detail':'文件创建失败！'},
                status=status.HTTP_400_BAD_REQUEST
            )