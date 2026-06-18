from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity_list, name='activity'),
    path('api/', views.activity_api, name='activity_api'),
]
