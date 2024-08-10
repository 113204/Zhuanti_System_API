import base64
import bcrypt

from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Post, Message

from utils.decorators import user_login_required


# 除了取得資料其他都用post

# 文章抓取
@api_view()
# @user_login_required
def get_all_post_test(request):
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

