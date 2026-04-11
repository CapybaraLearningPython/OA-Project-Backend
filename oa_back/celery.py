import os
from celery import Celery
from celery.signals import after_setup_logger
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oa_back.settings')

app = Celery('oa_back')

@after_setup_logger.connect
def logger_setting(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('logs.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')