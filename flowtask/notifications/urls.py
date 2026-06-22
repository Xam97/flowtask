# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('api/get/', views.get_notifications, name='get_notifications'),
    path('api/mark/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('api/mark-all/', views.mark_all_as_read, name='mark_all_as_read'),
]
