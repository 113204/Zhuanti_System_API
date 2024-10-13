from django.urls import path

from api.views.record_views import *

# 將被auth_urls取代
app_name = 'record'

urlpatterns = [
    path('record/', addrecord),
    path('getrecord/', get_user_records),
]
