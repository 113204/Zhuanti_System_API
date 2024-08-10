import base64
import bcrypt

from django.db import IntegrityError
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from api.models import Post, Message

from utils.decorators import user_login_required


# 除了取得資料其他都用post

# 文章抓取
@api_view()
# @user_login_required
def get_all_post(request):
    posts = Post.objects.all()

    return Response({
        'success': True,
        'data': [
            {
                'no': post.pk,
                'usermail': post.usermail.name,
                'title': post.title,
                'text': post.text,
            }
            for post in posts
        ]
    })


@api_view(['GET'])
def get_post(request, no):
    try:
        post = Post.objects.get(pk=no)
        return JsonResponse({
            'success': True,
            'data': {
                'no': post.pk,
                'usermail': post.usermail.name,
                'title': post.title,
                'text': post.text,
            }
        })
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Article not found'}, status=404)

@api_view(['GET'])
def get_post_message(request, nopost):
    try:
        # 确保 `nopost` 是有效的整数
        try:
            nopost = int(nopost)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid `nopost` parameter'}, status=400)

        # 获取与 `nopost` 关联的所有消息
        messages = Message.objects.filter(nopost=nopost)

        # 构建消息列表
        message_list = [
            {
                'no': message.pk,
                'nopost': message.nopost,  # 确保只返回 Post 的主键
                'usermail': message.usermail.name,
                'text': message.text,
            }
            for message in messages
        ]

        return JsonResponse({
            'success': True,
            'data': message_list
        })
    except Exception as e:
        import traceback
        print(f'Error in get_post_message: {e}')
        traceback.print_exc()  # 打印详细的异常信息
        return JsonResponse({'success': False, 'message': f'Error fetching messages: {str(e)}'}, status=500)

# 新增文章
@api_view(['POST'])
def addpost(request):
    data = request.data

    # 新增文章資料
    try:
        Post.objects.create(no=data['no'], usermail=data['usermail'], text=data['text'])

        return Response({'success': True})


    except IntegrityError:
        return Response({'success': False}, status=status.HTTP_409_CONFLICT)

    except:
        return Response({'success': False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 新增文章
@api_view(['POST'])
def addmessage(request):
    data = request.data

    # 新增文章資料
    try:
        Message.objects.create(no=data['no'], nopost=data['nopost'], text=data['text'])

        return Response({'success': True})


    except IntegrityError:
        return Response({'success': False}, status=status.HTTP_409_CONFLICT)

    except:
        return Response({'success': False},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

