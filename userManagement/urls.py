# chat/urls.py
from django.urls import path
import threading
from . import views

from datingAPI import appProcessing, settings
import os
from django.conf.urls.static import static
urlpatterns = [
    path('login', views.LoginView.as_view(), name='login'),  # For POST login a user
    path('logout', views.LogoutView.as_view(), name='logout'),  # For POST logout a user
    path('register', views.RegisterView.as_view(), name='register'),  # For POST register a user
    path('google', views.GoogleView.as_view(), name='google'),  # add path for google authentication

    path('refreshToken', views.RefreshTokenn.as_view(), name='refreshToken'),
    path('verifyAgain', views.sendVerifyLinkAgain, name='verifyAgain'),

    path('friends', views.FriendsListView.as_view(), name='friendss'),
    path('friends/<str:request_type>', views.FriendsListView.as_view(), name='friendsGET'),
    path('friends/<str:user_id>', views.FriendsListView.as_view(), name='friends'),

    path('premium', views.PremiumBuyView.as_view(), name='premiumbuy'),

    path('block', views.BlockUser.as_view(), name='BlockUserview'),

    path('findUser/<str:username>', views.UsersListView.as_view(), name='userGET'),  # For GET one User
    path('findUser', views.UsersListView.as_view(), name='user'),  # For GET Users and POST

    path('story', views.StoryView.as_view(), name='putStory'),
    path('story/<str:story_id>', views.StoryView.as_view(), name='deleteStory'),
    path('story/<str:username>', views.StoryView.as_view(), name='getStory'),

    path('profile', views.ProfileMeView.as_view(), name='meProfile'),  # For POST and PUT and GET user details and also delete user

    path('interests', views.InterestsView.as_view(), name='interestsUSER'),
    path('interests/<str:username>', views.InterestsView.as_view(), name='interestsUSEROTHER'),

    path('feeling', views.FeelingsView.as_view(), name='feelingsUSER'),
    path('date/<str:date_id>', views.DateView.as_view(), name='dateGET'),  # For Date GET
    path('date', views.DateView.as_view(), name='datePUTPOST'),  # For Date POST and PUT
    path('profilePic', views.ProfilePictureView.as_view(), name='profilepicPOST'),  # For PUT
    path('profilePic/<str:username>', views.ProfilePictureView.as_view(), name='profilepic'),  # For GET
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## After Runserver
dir = 'media/stories'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

init_thread = threading.Thread(target=appProcessing.init_tasks, name="initer")
init_thread.start()

init_thread3 = threading.Thread(target=appProcessing.init_tasks3, name="initer")
init_thread3.start()

init_thread2 = threading.Thread(target=appProcessing.init_tasks2, name="initer2")
init_thread2.start()
