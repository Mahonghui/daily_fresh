from django.shortcuts import render, redirect
from django.views.generic import View
from .models import User
from django.urls import reverse
from django.http import HttpResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from celery_tasks.tasks import send_active_email

import re
# Create your views here.


# /users/register, 已不使用
def register(request):

    if request.method == 'GET':
        '''显示注册页面'''
        return render(request, 'register.html')

    else:
        '''处理用户注册'''
        # 1.接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 2.检验数据
        # 数据缺失
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 检验邮箱合法性
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '请输入合法邮箱'})

        # 检验密码是否一致
        cpwd = request.POST.get('cpwd')
        if password != cpwd:
            return render(request, 'register.html', {'errmsg': '密码不一致'})

        # 是否同意协议
        is_allow = request.POST.get('allow')
        if is_allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 检查用户名是否存在
        try:
            user = User.objects.get(username=username)
        except:
            # 用户名不存在
            user = None

        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 3.业务处理
        user = User()
        user.username = username
        user.password = hash(password)
        user.email = email
        user.is_active = 0  # 默认未激活
        user.save()


        # 4.返回响应
        return redirect(reverse('goods:index'))


class RegisterView(View):
    '''注册类视图'''

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 1.接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 2.检验数据
        # 数据缺失
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 检验邮箱合法性
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '请输入合法邮箱'})

        # 检验密码是否一致
        cpwd = request.POST.get('cpwd')
        if password != cpwd:
            return render(request, 'register.html', {'errmsg': '密码不一致'})

        # 是否同意协议
        is_allow = request.POST.get('allow')
        if is_allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 检查用户名是否存在
        try:
            user = User.objects.get(username=username)
        except:
            # 用户名不存在
            user = None

        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 3.业务处理
        user = User()
        user.username = username
        user.password = hash(password)
        user.email = email
        user.is_active = 0  # 默认未激活
        user.save()

        # 发送激活邮件，设置激活链接(标识用户唯一性)： /users/active/1/
        # 加密用户身份信息
        serializer = Serializer(settings.SECRET_KEY, 3600) # 使用django提供的token， 1小时过期
        info = {'confirm': user.id}
        token = serializer.dumps(info) # 返回byte流

        token = token.decode() # 解码为str

        # celery发送邮件
        send_active_email.delay(email, username, token)

        # 4.返回响应
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''处理用户激活请求'''

    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600) # 前后token要一致

        try:
            # 解密url中的解密字符串
            info = serializer.loads(token) # 返回被加密数据，类型前后一致
            user_id = info['confirm']

            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            return redirect(reverse('users:login'))

        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')


class LoginView(View):
    '''登录视图'''

    def get(self, request):
        return render(request, 'login.html')