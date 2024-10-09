import base64
import traceback

import bcrypt
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


@api_view(['GET'])
def get_user_post(request):
    # # 使用当前用户的 email 来过滤文章
    # current_user_email = request.user.email

    data = request.query_params
    useremail = data.get('email')

    # 获取当前用户的文章
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

@api_view(['GET'])
def get_post_message(request, nopost):
    try:
        # 确保 `nopost` 是有效的整数
        try:
            nopost = int(nopost)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid `nopost` parameter'}, status=400)

        # 确保 `nopost` 是一个有效的 `Post` 对象
        try:
            post = Post.objects.get(no=nopost)
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)

        # 获取与 `nopost` 关联的所有消息
        messages = Message.objects.filter(nopost=post)

        # 构建消息列表
        message_list = [
            {
                'no': message.pk,
                'nopost': message.nopost.no,  # 确保返回的是 `Post` 的主键
                'usermail': message.usermail.name if message.usermail else 'Anonymous',
                'text': message.text,
                'date': message.date.isoformat(),  # 确保日期时间为 ISO 8601 格式
            }
            for message in messages
        ]

        return JsonResponse({
            'success': True,
            'data': message_list
        })

    except Exception as e:
        print(f'Error in get_post_message: {e}')
        traceback.print_exc()  # 打印详细的异常信息
        return JsonResponse({'success': False, 'message': f'Error fetching messages: {str(e)}'}, status=500)

# 新增文章
@api_view(['POST'])
def addpost(request):
    data = request.data
    print("Received data:", data)  # 打印接收到的数据

    usermail_str = data.get('usermail')
    title = data.get('title')
    text = data.get('text')
    date_str = data.get('date')  # 获取前端传递的日期时间字符串

    if not usermail_str or not title or not text:
        print("Missing required fields")  # 打印缺少字段的信息
        return Response({'success': False, 'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=usermail_str)
    except User.DoesNotExist:
        print("User not found:", usermail_str)  # 打印用户未找到的信息
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 解析 ISO 8601 格式的日期时间字符串并添加台湾时区
        if date_str:
            date = datetime.fromisoformat(date_str)
            # 设置时区为台湾时间
            taipei_tz = pytz.timezone('Asia/Taipei')
            date = date.astimezone(taipei_tz)
        else:
            date = None

        Post.objects.create(usermail=user, title=title, text=text, date=date)
        return Response({'success': True})
    except IntegrityError as e:
        print(f'IntegrityError: {e}')  # 打印完整性错误信息
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

    nopost_id = data.get('nopost')  # 关联的帖子编号
    usermail_str = data.get('usermail')  # 当前登录用户的邮箱
    text = data.get('text')  # 评论内容
    date_str = data.get('date')  # 评论时间字符串

    if not nopost_id or not usermail_str or not text:
        print("Missing required fields")  # 打印缺少字段的信息
        return Response({'success': False, 'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=usermail_str)
    except User.DoesNotExist:
        print("User not found:", usermail_str)  # 打印用户未找到的信息
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 查找关联的帖子实例
        try:
            post = Post.objects.get(no=nopost_id)
        except Post.DoesNotExist:
            print("Post not found:", nopost_id)  # 打印帖子未找到的信息
            return Response({'success': False, 'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        # 解析 ISO 8601 格式的日期时间字符串并添加台湾时区
        if date_str:
            date = datetime.fromisoformat(date_str)
            # 设置时区为台湾时间
            taipei_tz = pytz.timezone('Asia/Taipei')
            date = date.astimezone(taipei_tz)
        else:
            date = None

        # 创建新的评论
        Message.objects.create(nopost=post, usermail=user, text=text, date=date)
        return Response({'success': True})
    except IntegrityError as e:
        print(f'IntegrityError: {e}')  # 打印完整性错误信息
        return Response({'success': False, 'message': 'Integrity error'}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        import traceback
        print(f'Error in addmessage: {e}')
        traceback.print_exc()
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def editpost(request):
    data = request.data
    print("Received data:", data)  # 打印接收到的数据

    no = data.get('no')  # 获取要编辑的帖子 ID
    usermail_str = data.get('usermail')
    title = data.get('title')
    text = data.get('text')
    date = data.get('date')  # 获取前端传递的日期时间字符串

    if not no or not usermail_str or not title or not text:
        print("Missing required fields")  # 打印缺少字段的信息
        return Response({'success': False, 'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = Post.objects.get(no=no)
    except Post.DoesNotExist:
        print("Post not found:", no)  # 打印帖子未找到的信息
        return Response({'success': False, 'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 确认用户是否存在
        user = User.objects.get(email=usermail_str)

        # 解析 ISO 8601 格式的日期时间字符串并添加台湾时区
        if date:
            date = datetime.fromisoformat(date)
            # 设置时区为台湾时间
            taipei_tz = pytz.timezone('Asia/Taipei')
            date = date.astimezone(taipei_tz)
        else:
            date = None

        # 更新帖子
        post.usermail = user
        post.title = title
        post.text = text
        post.date = date
        post.save()

        return Response({'success': True})
    except IntegrityError as e:
        print(f'IntegrityError: {e}')  # 打印完整性错误信息
        return Response({'success': False, 'message': 'Integrity error'}, status=status.HTTP_409_CONFLICT)
    except Exception as e:
        import traceback
        print(f'Error in editpost: {e}')
        traceback.print_exc()
        return Response({'success': False, 'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def deletepost(request, no):
    try:
        post = Post.objects.get(pk=no)
        post.delete()
        return JsonResponse({'success': True, 'message': 'Post successfully deleted'})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)
