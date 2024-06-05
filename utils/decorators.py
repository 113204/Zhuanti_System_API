from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def user_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('email'):
            # 如果用户未登录，添加消息并重定向到登录页面
            return Response({'success': False, 'message': '還未登入，請登入'}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

