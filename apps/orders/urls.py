from django.conf.urls import url
from .views import PlaceOrderView, HandleOrderView
from utils.login import login_required
app_name = 'orders'
urlpatterns = [
    url(r'^place_orders$', login_required(PlaceOrderView.as_view()), name='place_orders'),
    url(r'^commit$', login_required(HandleOrderView.as_view()), name='commit'),
]
