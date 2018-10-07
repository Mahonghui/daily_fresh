from django.conf.urls import url
from .views import AddCartView, CartInfoView, UpdateCartView, DeleteCartView
from utils.login import  login_required
app_name = 'cart'
urlpatterns = [
    url(r'^add$', AddCartView.as_view(), name='add'),
    # 只有登录的用户才有购物车
    url(r'^$', login_required(CartInfoView.as_view()), name='cart'),
    url(r'^update$', login_required(UpdateCartView.as_view()), name='update'),
    url(r'^delete$', login_required(DeleteCartView.as_view()), name='delete')
]
