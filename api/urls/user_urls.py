from django.urls import path

from api.views.user_views import *

# 將被auth_urls取代
app_name = 'user'

urlpatterns = [
    # path('all/', get_all_reviews),

    # 下面test/ 供成就相關表格進行測試
    # path('test/', get_user_detail_test),
    path('detail/', get_user_detail),
    path('detail/edit/', user_detail_edit),
    path('pass/edit/', user_pass_edit)

    # 學姊的範例測試
    # path('get/<int:pk>/', get_review),
    # path('get_critic_reviews/', get_critic_reviews),
]
