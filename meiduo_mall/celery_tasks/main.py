import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

from celery import Celery

# 创建Celery对象
celery_app = Celery('celery_tasks')

# 加载配置信息
celery_app.config_from_object('celery_tasks.config')

# 启动worker时自动发现任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
