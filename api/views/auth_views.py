import base64
import bcrypt

from django.db import IntegrityError

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
    return Response({'success': True, 'message': '登出成功'})


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
            return Response({'success': True, 'message': '登入成功', 'sessionid': request.session.session_key})
        else:
            # 密码不匹配，返回登录页面并显示错误消息
            return Response({'success': False, 'message': '帳號或密碼錯誤'}, status=status.HTTP_404_NOT_FOUND)

    except User.DoesNotExist:
        return Response({'success': False, 'message': '登入失敗，帳號或密碼錯誤'}, status=status.HTTP_404_NOT_FOUND)


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
                            gender=data['gender'], live=data['live'],
                            # photo=data['photo'],
                            # photo=photo_string,
                            phone=data['phone'], permission=data['permission'])

        return Response({'success': True, 'message': '註冊成功'})


    except IntegrityError:
        return Response({'success': False, 'message': '此帳號已被註冊'}, status=status.HTTP_409_CONFLICT)

    except:
        return Response({'success': False, 'message': '輸入格式錯誤，請確認電話及其他欄位的填寫格式'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 忘記密碼
@api_view()
def forget(request, pk):
    # # 注意：因使用POST，data
    # data = request.data
    #
    # user_id = data.get('user_id')
    # # get 後面加東西，可能部會成功，故fileter 方便
    #
    # user = User.objects.filter(pk=user_id)
    #
    # if not user.exists():
    #     return Response({'success': False, 'message': '沒有此帳號'}, status=status.HTTP_404_NOT_FOUND)
    #
    # return Response({'success': True, 'message': '成功找到此帳號'})

    try:
        user = User.objects.get(pk=pk)
    except:
        return Response({'success': False, 'message': '查無資料'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'message': '即將發送郵件重設密碼',
        'data':
            {
                'id': user.pk
            }
    })

