from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def user_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('email'):
            # 如果用户未登录，添加消息并重定向到登录页面
            messages.warning(request, '請先登入')
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

