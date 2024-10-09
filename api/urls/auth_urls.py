from django.urls import path

from api.views.auth_views import *

app_name = 'auth'

urlpatterns = [
    path('register/', register, name='register'),  # 註冊
    path('login/', login, name='login'),  # 登入
    path('logout/', logout, name='logout'),  # 登出
    path('forget/', forget, name='forget'),  # 忘記密碼
    path('reset-password/', reset_password, name='reset_password'),  # 重設密碼
]
