from oa_back import celery_app
from django.core.mail import send_mail
from django.conf import settings
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import time

def generate_activation_jwt(uid):
    exp = datetime.now() + timedelta(minutes=30)
    token = jwt.encode({'userid':uid, 'exp':exp}, settings.SECRET_KEY)
    return token

@celery_app.task()
def send_email(email, activation_url):
    time.sleep(2)
    subject = '【企业OA系统激活】'
    message = f'欢迎使用企业OA系统！请点击以下链接激活您的账户：{activation_url}'
    send_mail(
        subject=subject,
        recipient_list=[email],
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL
    )