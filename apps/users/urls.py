from django.conf.urls import url
from . import views
from .views import RegisterView, ActiveView, LoginView

app_name = 'users'
urlpatterns = [

    url(r'^register$', RegisterView.as_view(), name='register'),
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url(r'^login$', LoginView.as_view(), name='login')
]
