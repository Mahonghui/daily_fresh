from django.shortcuts import redirect,  reverse

# 自定义装饰器，
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.has_key('islogin'):
            return view_func(request, *args, **kwargs)
        else:
            return redirect(reverse('users:login'))
    return wrapper