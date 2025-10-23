# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room, name='chat_room'),
    path('users/', views.chat_users, name='chat_users'),
    path('history/<int:user_id>/', views.chat_history, name='chat_history'),
]