from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from userManagement.models import MyUser


class Group(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, blank=False)
    users = models.ManyToManyField(MyUser, related_name="users_of_chat", default=None, blank=True)
    admins = models.ManyToManyField(MyUser, related_name="admins_of_chat", default=None, blank=True)
    owner = models.ForeignKey(MyUser, related_name="owner_of_chat", on_delete=models.CASCADE, default=None)
    group_img = models.ImageField(upload_to = 'group-pics/', default = '/defaults/no-img-group.jpeg')
    name = models.CharField(default="Chat", max_length=25)
    id_chat = models.CharField(blank=True, null=True, max_length=20)  # This cannot be unique. So you say default to None and in views you check it yourself manually.

    def join_chat(self, user):
        self.users.add(user)
        user.chat_list.add(self)
        self.save()

    def __str__(self):
        return str(self.pk)

    class Meta:
        ordering = ('id',)


class Message(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, blank=False)
    group_id      = models.ForeignKey(Group, related_name="id_of_chat", on_delete=models.CASCADE, blank=False, null=False, max_length=20)
    creator       = models.ForeignKey(MyUser, related_name="sender_user", on_delete=models.CASCADE, blank=False)
    replying_to   = models.ForeignKey(MyUser, related_name="replied_user", on_delete=models.CASCADE, default=None, blank=True, null=True)
    file_url      = models.TextField(default="", null=True, blank=True)
    content       = models.TextField(default="", max_length=3300)
    created_at    = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class FileMessage(models.Model):
    file_file = models.FileField(upload_to='chat/', default=None, null=True, blank=True)


class Date(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True, blank=False)
    users = models.ManyToManyField(MyUser, default=None)
    creator = models.ForeignKey(MyUser, related_name='creator_date', on_delete=models.CASCADE, default=None)
    male_user = models.ForeignKey(MyUser, related_name='male_user_date', on_delete=models.CASCADE, default=None)
    female_user = models.ForeignKey(MyUser, related_name='female_user_date', on_delete=models.CASCADE, default=None)
    request_or_hidden = models.BooleanField(default=False)  # True means request. False means hidden and crush
    male = models.BooleanField(default=False)
    female = models.BooleanField(default=False)

    def __str__(self):
        return self.pk

    class Meta:
        ordering = ('id',)


## Use <MyField>_set.get() --> Many to One