# chat/urls.py
from django.urls import path
from . import views
urlpatterns = [
    # path('mongo1/', views.test_mongo_db, name='testmongo'), # MONGO TEST
    # path('mongo2/', views.test_mongo_db_2, name='testmongo'), # MONGO TEST

    path('roomPick', views.index, name='index'),
    path('room/<str:chat_id>', views.room, name='room'),
    

    path('chat/<str:chat_id>', views.GroupListView.as_view(), name='chatGET'), # For GET one group
    path('chat/join/<str:chat_id>', views.join_chat, name='chatGET'), # For GET one group
    path('chat', views.GroupListView.as_view(), name='chat'), # For GET groups and POST

    path('chatPic', views.GroupPictureView.as_view(), name='chat'), # For PUT
    path('chatPic/<str:group_id>', views.GroupPictureView.as_view(), name='chat'), # For GET


    #path('date/', views.date, name='dateGET'), # For Date POST, DELETE, PUT

    #path('chat/<str:group_id>/messages', views.date, name='dateGET'), # For Message GET and POST
    #path('chat/<str:group_id>/<str:message_id>', views.date, name='dateGET'), # For Message GET
    #The TEST FOR SSH CONNECTING TO THE LINUX  WAS SUCCESSFUL.
]
