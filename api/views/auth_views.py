import base64
import bcrypt
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from django.db import IntegrityError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import User

from utils.decorators import user_login_required


# 除了取得資料其他都用post
# 登出
@api_view(['POST'])
@user_login_required
def logout(request):
    data = request.data
    request.session.flush()
    return Response({'success': True})


# 登入
@api_view(['POST'])
def login(request):
    data = request.data

    if 'email' in request.session:
        return Response({'success': False, 'message': '已登入過'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(pk=data['email'])
        hashed_password_from_db = user.password

        # 使用 bcrypt 的 checkpw 函数验证密码
        if bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password_from_db.encode('utf-8')):
            # 密码匹配，进行登录操作
            request.session['email'] = user.email
            request.session.save()
            return Response({'success': True, 'sessionid': request.session.session_key})
        else:
            # 密码不匹配，返回登录页面并显示错误消息
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


# 註冊
@api_view(['POST'])
def register(request):
    data = request.data

    # # 圖片轉base64字串
    # photo = request.FILES['photo']
    # photo_string = str(base64.b64encode(photo.read()))[2:-1]

    # 新增使用者資料
    try:
        User.objects.create(email=data['email'], name=data['name'], password=data['password'],
                            gender=data['gender'],
                            # photo=data['photo'],
                            # photo=photo_string,
                            phone=data['phone'], permission=data['permission'])

        return Response({'success': True})


    except IntegrityError:
        return Response({'success': False}, status=status.HTTP_409_CONFLICT)

    except:
        return Response({'success': False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 忘記密碼
@api_view(['POST'])
def forget(request):
    data = request.data
    email = data.get('email', '').strip()

    if not email:
        return Response({'success': False, 'message': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)

        # 生成重設密碼的令牌和 UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"

        # 發送重設密碼郵件
        send_mail(
            'Password Reset Request',
            f"點擊連結以重新設定密碼: {reset_url}",
            'no-reply@yourdomain.com',
            [user.email],
            fail_silently=False,
        )

        return Response({'success': True, 'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def reset_password(request):
    """
    根據用戶的 UID 和 Token 驗證身份，並更新密碼。
    """
    data = request.data
    uid = data.get('uid')
    token = data.get('token')
    new_password = data.get('password')

    if not uid or not token or not new_password:
        return Response({'success': False, 'message': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 解碼 UID 並查找用戶
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)

        # 驗證 token 是否有效
        if default_token_generator.check_token(user, token):
            # 如果您已經在前端進行了密碼哈希，則直接保存
            user.password = new_password  # 這裡是直接設置哈希後的密碼
            user.save()
            return Response({'success': True, 'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'success': False, 'message': 'Invalid user.'}, status=status.HTTP_400_BAD_REQUEST)