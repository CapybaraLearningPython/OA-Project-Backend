from django.core.management.base import BaseCommand
from apps.oa_auth.models import Department


class Command(BaseCommand):
    # 初始化部门数据
    def handle(self, *args, **options):
        board = Department.objects.create(name='董事会')
        dev = Department.objects.create(name='产品开发部')
        operation = Department.objects.create(name='运营部')
        sales = Department.objects.create(name='销售部')
        hr = Department.objects.create(name='人事部')
        finance = Department.objects.create(name='财务部')
        self.stdout.write('部门数据初始化成功！')