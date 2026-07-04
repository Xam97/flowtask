# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('unread-count/', views.unread_count, name='notification_unread_count'),
    path('mark-all-read/', views.mark_all_read, name='notification_mark_all_read'),
    path('delete-read/', views.delete_all_read, name='notification_delete_all_read'),
    path('<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('<int:notification_id>/read/', views.mark_read, name='notification_mark_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='notification_delete'),
]
