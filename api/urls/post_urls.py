from django.urls import path

from api.views.post_views import *

app_name = 'post'

urlpatterns = [
    path('addpost/', addpost, name='addpost'),
    path('addmessage/', addmessage, name='addmessage'),
    path('post/', get_all_post_test, name='get_all_post_test'),
    # path('forget/<pk>/', forget),
]
