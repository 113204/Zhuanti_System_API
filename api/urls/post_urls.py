from django.urls import path

from api.views.post_views import *

app_name = 'post'

urlpatterns = [
    path('addpost/', addpost, name='addpost'),
    path('addmessage/', addmessage, name='addmessage'),
    path('post/', get_all_post, name='get_all_post'),
    path('post/detail/<int:no>/', get_post, name='get_post'),
    path('post/message/<int:nopost>/', get_post_message, name='post_message'),
    path('editpost/', editpost, name='editpost'),
    # path('forget/<pk>/', forget),
]
