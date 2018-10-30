# encoding: utf-8
from django.shortcuts import render, redirect
from django.views.generic import View

from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django_redis import get_redis_connection
from celery_tasks.tasks import send_active_email
from hashlib import md5 # 加密密码
import json # 解决cookie中文乱码问题
import re

from .models import User, Address
from goods.models import GoodsSKU
from orders.models import OrderInfo, OrderGoods

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
        user.password = md5(password.encode('utf-8')).hexdigest() # 存储密码的MD5值
        user.email = email
        user.is_active = 0  # 默认未激活
        user.save()

        # 发送激活邮件，设置激活链接(标识用户唯一性)： /users/active/1/
        # 加密用户身份信息
        serializer = Serializer(settings.SECRET_KEY, 3600) # 使用django提供的token， 1小时过期
        info = {'confirm': user.id}
        
        token = serializer.dumps(info).decode() 

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

        if 'username' in request.COOKIES:
            username = json.loads(request.COOKIES.get('username'))
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')

        if not all([username, pwd]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 检查用户名是否匹配
        try:
            user = User.objects.get(username=username) # 查不到抛异常

            hashed_pwd = md5(pwd.encode('utf-8')).hexdigest() # md5之前要进行编码
            if user.password == hashed_pwd:

                if user.is_active:

                    remember = request.POST.get('remember')

                    response = redirect(reverse('goods:index'))

                    if remember == 'on':
                        # 记住用户名
                        response.set_cookie('username', json.dumps(username), max_age=3*24*3600)
                    else:
                        response.delete_cookie('username')

                             # 记住登录状态
                    request.session['islogin'] = True
                    request.session['user'] = user

                    return response

                else:
                    return render(request, 'login.html', {'errmsg': '用户未激活'})

            else:
                    return render(request, 'login.html', {'errmsg': '用户名或密码不正确'})

        except Exception as e:
            print(e)
            return render(request, 'login.html', {'errmsg': '用户不存在'})

class LogOutView(View):
    def get(self, request):
        # 清楚session
        request.session.flush()
        return redirect(reverse('goods:index'))


#装饰器不能用于视图类
class UserInfoView(View):
    def get(self, request):

        # 获取默认地址信息
        current_user = request.session.get('user')
        address = Address.objects.get_default_address(current_user)

        # 获取历史浏览记录
        conn = get_redis_connection('default')

        history_key = 'history_%d'%current_user.id
        sku_list = conn.lrange(history_key, 0, 4)
        goods_list = []

        for sku in sku_list:
            good = GoodsSKU.objects.get(id=sku)
            goods_list.append(good)

        context = {'page': 'user', 'current_user': current_user, 'address': address, 'good_history': goods_list}
        return render(request, 'user_center_info.html', context)


class UserOrderView(View):
    def get(self, request, page_num):
        user = request.session.get('user')

        orders = OrderInfo.objects.filter(user=user)

        for order in orders:
            goods = OrderGoods.objects.filter(order=order).order_by('-create_time')

            for good in goods:
                good.sum = good.count * good.price

            order.goods = goods
            order.status_name = OrderInfo.ORDER_STATUS_MAP[order.order_status]

        paginator = Paginator(orders, 1)

        # 页码非数值
        try:
            page_num = int(page_num)
        except ValueError:
            page_num = 1

        # 超出总页数
        if page_num > paginator.num_pages:
            page_num = 1

        page = paginator.page(page_num)

        context = {
            'orders': orders,
            'page': page,
            'page_num': page_num,
            'page_name': 'order'
        }

        return render(request, 'user_center_order.html', context)


class UserSiteView(View):
    def get(self, request):
        current_user = request.session.get('user')
        addr_set = Address.objects.filter(user=current_user)
        return render(request, 'user_center_site.html', {'page': 'site', 'addr_set': addr_set})

    def post(self, request):
        '''处理编辑后的地址'''
        receiver = request.POST.get('receiver')
        addr = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        contact = request.POST.get('contact')


        if not all([receiver, addr, zip_code, contact]):
            return render(request, 'user_center_site.html', {'errmsg': '信息不完整'})

        address = Address()
        address.receiver = receiver
        address.address = addr
        address.zip_code = zip_code
        address.contact = contact
        address.user = request.session.get('user')

        address.save()
        return render(request, 'user_center_site.html')





