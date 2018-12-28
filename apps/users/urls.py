from django.conf.urls import url
from .views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, UserSiteView, LogOutView
# 使用自定义login_required
from utils.login import login_required
app_name = 'users'
urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'),
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^user_center_info$', login_required(UserInfoView.as_view()), name='user_center_info'),
    url(r'^user_center_order/(?P<page_num>\d+)$', login_required(UserOrderView.as_view()), name='user_center_order'),
    url(r'^user_center_site$', login_required(UserSiteView.as_view()), name='user_center_site'),
    url(r'^logout$', LogOutView.as_view(), name='logout')
]

# 1. login_required 不能用于视图类，需要手动调用
# 2. login_required 默认跳转到account/login?next=， settings.py:LOGIN_URL指定跳转页面