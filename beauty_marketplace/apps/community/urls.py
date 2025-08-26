from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/messages/add/', views.add_message, name='add_message'),
    
    path('messages/', views.private_messages, name='private_messages'),
    path('messages/<int:user_id>/', views.private_message_thread, name='private_message_thread'),
]
