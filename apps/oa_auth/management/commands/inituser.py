from django.core.management.base import BaseCommand
from apps.oa_auth.models import OAUser, Department

class Command(BaseCommand):
    def handle(self, *args, **options):
        board = Department.objects.get(name='董事会')
        dev = Department.objects.get(name='产品开发部')
        operation = Department.objects.get(name='运营部')
        sales = Department.objects.get(name='销售部')
        hr = Department.objects.get(name='人事部')
        finance = Department.objects.get(name='财务部')
    
    # 董事会员工为 superuser，部门领导为普通 user
        dongdong = OAUser.objects.create_superuser(
            email='dongdong@oa.com', 
            name='东东', 
            password='abc123', 
            department=board
        )
        duoduo = OAUser.objects.create_superuser(
            email='duoduo@oa.com', 
            name='多多', 
            password='abc123', 
            department=board
        )
        zhangsan = OAUser.objects.create_user(
            email='zhangsan@oa.com', 
            name='张三', 
            password='abc123', 
            department=dev
        )
        lisi = OAUser.objects.create_user(
            email='lisi@oa.com', 
            name='李四', 
            password='abc123', 
            department=operation
        )
        wangwu = OAUser.objects.create_user(
            email='wangwu@oa.com', 
            name='王五', 
            password='abc123', 
            department=hr
        )
        zhaoliu = OAUser.objects.create_user(
            email='zhaoliu@oa.com', 
            name='赵六', 
            password='abc123', 
            department=finance
        )
        sunqi = OAUser.objects.create_user(
            email='sunqi@oa.com', 
            name='孙七', 
            password='abc123', 
            department=sales
        )
        
        
        board.leader = dongdong
        board.manager = None
        
        dev.leader = zhangsan
        dev.manager = dongdong
        
        operation.leader = lisi
        operation.manager = dongdong
        
        hr.leader = wangwu
        hr.manager = dongdong
        
        finance.leader = zhaoliu
        finance.manager = duoduo
        
        sales.leader = sunqi
        sales.manager = duoduo
        
        departments = [board, dev, operation, hr, finance, sales]
        for department in departments:
            department.save()
            
        self.stdout.write('用户初始化成功')