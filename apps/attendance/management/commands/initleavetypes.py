from django.core.management.base import BaseCommand
from ... import models

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        leave_types = ['事假', '病假', '工伤假', '婚假', '丧假', '产假', '探亲假', '公假', '年休假']
        for leave_type in leave_types:
            models.LeaveType.objects.create(name=leave_type)
        self.stdout.write('请假类型数据初始化成功！')