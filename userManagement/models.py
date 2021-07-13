from datetime import date

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import os


class Story(models.Model):
    clip = models.FileField(upload_to='stories/', null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    # expire_date = timezone.now() + datetime.timedelta(days=1)


class MyUserManager(BaseUserManager):
    
    def create_user(self, email, date_of_birth, full_name, username, gender, premium, password):

        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            full_name=full_name,
            gender=gender,
            premium=premium,
            username=username,
            status=False,
            dating_with = "nobody"
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, date_of_birth, gender, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            gender=gender,
            premium=True,
            username=username,
            full_name=full_name,
            date_of_birth=date_of_birth,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True, unique=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=False,
        blank=False
    )
    full_name = models.CharField(blank=False, null=False, default="", max_length=20)
    date_of_birth = models.DateField(blank=False, null=False, default=date.fromisoformat("2000-01-01"))
    profile_pic = models.ImageField(upload_to = 'pics/', blank=True, null=True, default=None)
    gender = models.BooleanField(default=True)
    premium_days_left = models.IntegerField(default=0)
    username = models.CharField(blank=False, unique=True, max_length=15)
    friends = models.ManyToManyField('MyUser', default=None)
    subscription_id_stripe = models.TextField(default="")
    account_type = models.CharField(default="", max_length=10)
    customer_id_stripe = models.TextField(default="")
    dating_with = models.ForeignKey('MyUser', related_name="dating_with_user", on_delete=models.CASCADE, blank=True, null=True)
    users_searched_day = models.IntegerField(default=0)
    users_requested_date_day = models.IntegerField(default=0)
    feeling = models.CharField(default="nothing", max_length=15)
    about = models.CharField(max_length=40, default="A new user")
    create_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    interests = models.CharField(default="[]", max_length=50)
    chat_list = models.ManyToManyField('myapp.Group', related_name='users_chat_list', default=None)
    block_list = models.ManyToManyField('MyUser', related_name='blocked_users_list', default=None)
    private = models.BooleanField(default=False)
    stories = models.ManyToManyField(Story, related_name='story_list', default=None)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['date_of_birth', 'gender', 'email', 'full_name']

    def remove_old_profile_pic(self):
        if self.profile_pic:
            s = self.profile_pic.path
            print(f"L: {self.profile_pic.path}")
            self.profile_pic.delete()
            self.profile_pic = None

    def get_age(self):
        return int((date.today() - self.date_of_birth).days / 365)

    def add_story(self, story):
        self.stories.add(story)
        self.save()

    def __str__(self):
        return str(self.username) or ""

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class VerifyLink(models.Model):
    token = models.TextField(blank=False, primary_key=True)
    user = models.ForeignKey(MyUser, related_name='register_user', on_delete=models.CASCADE)
    verify_type = models.CharField(max_length=10, default="")
    extra_data = models.TextField(default="")

    def __str__(self):
        return self.token

    class Meta:
        ordering = ('token',)
