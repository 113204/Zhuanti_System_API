import base64
import traceback

import pytz

from django.db import IntegrityError
from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from datetime import datetime

from api.models import Post, Message, User

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
                'date': post.date,
            }
            for post in posts
        ]
    })

# 抓取特定使用者文章
@api_view(['GET'])
def get_user_post(request):

    data = request.query_params
    useremail = data.get('email')

    # 獲取當前登入用戶文章
    posts = Post.objects.filter(usermail__email=useremail)

    return Response({
        'success': True,
        'data': [
            {
                'no': post.pk,
                'usermail': post.usermail.name,
                'title': post.title,
                'text': post.text,
                'date': post.date,
            }
            for post in posts
        ]
    })

# 文章內容
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
                'date': post.date,
            }
        })
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Article not found'}, status=404)

# 留言內容
@api_view(['GET'])
def get_post_message(request, nopost):
    try:
        # 確保 nopost 為有效整數
        try:
            nopost = int(nopost)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid `nopost` parameter'}, status=400)

        # 確保nopost為有效的Post欄位
        try:
            post = Post.objects.get(no=nopost)
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)

        # 獲取nopost有關所有資訊
        messages = Message.objects.filter(nopost=post)

        # 新增留言
        message_list = [
            {
                'no': message.pk,
                'nopost': message.nopost.no,  # 確保是Post的PK
                'usermail': message.usermail.name if message.usermail else 'Anonymous',
                'text': message.text,
                'date': message.date.isoformat(),  # 確保日期時間為 ISO 8601 格式
            }
            for message in messages
        ]

        return JsonResponse({
            'success': True,
            'data': message_list
        })

    except Exception as e:
        print(f'Error in get_post_message: {e}')
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Error fetching messages: {str(e)}'}, status=500)

# 新增文章
@api_view(['POST'])
def addpost(request):
    data = request.data
    print("Received data:", data)

    usermail_str = data.get('usermail')
    title = data.get('title')
    text = data.get('text')
    date_str = data.get('date')  # 獲取日期時間

    if not usermail_str or not title or not text:
        print("Missing required fields")
        return Response({'success': False, 'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=usermail_str)
    except User.DoesNotExist:
        print("User not found:", usermail_str)  # 使用者未找到
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 解析 ISO 8601 格式的日期時間並設置為台灣台北時間
        if date_str:
            date = datetime.fromisoformat(date_str)
            # 設置為台灣台北時間
            taipei_tz = pytz.timezone('Asia/Taipei')
            date = date.astimezone(taipei_tz)
        else:
            date = None

        Post.objects.create(usermail=user, title=title, text=text, date=date)
        return Response({'success': True})
    except IntegrityError as e:
        print(f'IntegrityError: {e}')
        return Response({'success': False, 'message': 'Integrity error'}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        import traceback
        print(f'Error in addpost: {e}')
        traceback.print_exc()
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 新增留言
@api_view(['POST'])
def addmessage(request):
    data = request.data
    print("Received data:", data)  # 打印接收到的数据

    nopost_id = data.get('nopost')  # 文章編號
    usermail_str = data.get('usermail')  # 當前登入帳號
    text = data.get('text')  # 评留言內容
    date_str = data.get('date')  # 留言時間

    if not nopost_id or not usermail_str or not text:
        print("Missing required fields")  # 打印缺少欄位
        return Response({'success': False, 'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=usermail_str)
    except User.DoesNotExist:
        print("User not found:", usermail_str)  # 使用者帳號未找到
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 查找文章
        try:
            post = Post.objects.get(no=nopost_id)
        except Post.DoesNotExist:
            print("Post not found:", nopost_id)  # 文章未找到
            return Response({'success': False, 'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        # 解析 ISO 8601 格式的日期時間並設置為台灣台北時間
        if date_str:
            date = datetime.fromisoformat(date_str)
            # 設置為台灣台北時區
            taipei_tz = pytz.timezone('Asia/Taipei')
            date = date.astimezone(taipei_tz)
        else:
            date = None

        # 新增留言
        Message.objects.create(nopost=post, usermail=user, text=text, date=date)
        return Response({'success': True})
    except IntegrityError as e:
        print(f'IntegrityError: {e}')
        return Response({'success': False, 'message': 'Integrity error'}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        import traceback
        print(f'Error in addmessage: {e}')
        traceback.print_exc()
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 編輯文章
@api_view(['POST'])
def editpost(request):
    data = request.data
    print("Received data:", data)

    no = data.get('no')  # 獲取要編輯的文章的no
    usermail_str = data.get('usermail')
    title = data.get('title')
    text = data.get('text')
    date = data.get('date')  # 獲取發文日期

    if not no or not usermail_str or not title or not text:
        print("Missing required fields")
        return Response({'success': False, 'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = Post.objects.get(no=no)
    except Post.DoesNotExist:
        print("Post not found:", no)  # 文章未找到
        return Response({'success': False, 'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 確認使用者是否存在
        user = User.objects.get(email=usermail_str)

        # 解析 ISO 8601 格式的日期時間並設置為台灣台北時間
        if date:
            date = datetime.fromisoformat(date)
            # 設置為台灣台北時間
            taipei_tz = pytz.timezone('Asia/Taipei')
            date = date.astimezone(taipei_tz)
        else:
            date = None

        # 更新文章
        post.usermail = user
        post.title = title
        post.text = text
        post.date = date
        post.save()

        return Response({'success': True})
    except IntegrityError as e:
        print(f'IntegrityError: {e}')
        return Response({'success': False, 'message': 'Integrity error'}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        import traceback
        print(f'Error in editpost: {e}')
        traceback.print_exc()
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#刪除文章
@api_view(['POST'])
def deletepost(request, no):
    try:
        post = Post.objects.get(pk=no)
        post.delete()
        return JsonResponse({'success': True, 'message': 'Post successfully deleted'})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)
