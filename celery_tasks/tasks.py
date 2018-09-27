from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

import time

# 在celery端加入，这里就是本机
import django
import os
# cited from daily_fresh.wsgi
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daily_fresh.settings')
django.setup()

# 实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_email(to_who, username, token):
    '''异步发送激活邮件'''

    # 发送激活邮件
    subject = '每日生鲜欢迎信息'
    message = ''
    html_message = '<h1>{},欢迎您注册成为天天生鲜会员<h1>请点击下面链接以激活账户</br>\
    <a href="http://127.0.0.1:8000/users/active/{}">\
    http://127.0.0.1:8000/users/active/{}</a>'.format(username, token, token)
    sender = settings.EMAIL_FROM
    receiver_list = [to_who]

    send_mail(subject, message, sender, receiver_list, html_message=html_message)
    time.sleep(5)