from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from myapp.models import MyUser


class MyUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = MyUser.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                return None
        except user.DoesNotExist:
            return None