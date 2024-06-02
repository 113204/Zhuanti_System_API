from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from urllib.parse import unquote

from api.models import User

from utils.decorators import user_login_required


# 將被auth_views取代
# 每一個測試的api_view,一次只能取消註解一個

# 使用者列表測試
@api_view()
@user_login_required
def get_user_detail_test(request):
    users = User.objects.all()
    # get(pk=pk) all()

    return Response({
        'success': True,
        'data': [
            {
                'email': user.pk,
                'name': user.name,
                'gender': user.gender,
                'live': user.live,
                'phone': user.phone,
            }
            for user in users
        ]
    })


# 個人資料顯示頁面
@api_view()
@user_login_required
def get_user_detail(request):
    data = request.query_params
    email = data.get('email')

    # 查询用户信息
    try:
        user = User.objects.get(pk=email)
        return Response({
            'success': True,
            'data': {
                'name': user.name,
                'email': user.pk,
                'gender': user.gender,
                'live': user.live,
                'phone': user.phone,
                'about': user.about,
            }
        })
    except User.DoesNotExist:
        return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)



# 個人資料編輯
@api_view(['POST'])
@user_login_required
def user_detail_edit(request):
    data = request.data
    # data = request.query_params
    email = data.get('email')

    user = User.objects.filter(pk=email)

    if not user.exists():
        return Response({'success': False, 'message': '沒有此帳號'}, status=status.HTTP_404_NOT_FOUND)

    try:
        user.update(name=data['name'], gender=data['gender'], live=data['live'], phone=data['phone'], about=data['about'])
        return Response({'success': True, 'message': '編輯成功'})
    except:
        return Response({'success': False, 'message': '編輯失敗'}, status=status.HTTP_400_BAD_REQUEST)
