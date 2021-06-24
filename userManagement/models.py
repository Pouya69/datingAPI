from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    
    def create_user(self, email, age, username, gender, premium, password):

        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            age=age,
            gender=gender,
            premium=premium,
            username=username,
            status=False,
            dating_with = "nobody"
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, age, gender, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            gender=gender,
            premium=True,
            username=username,
            age=age,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True, unique=True)
    email = models.EmailField(
        max_length=255
    )
    age = models.IntegerField(blank=False)
    profile_pic = models.ImageField(upload_to = 'pics/', default='/defaults/no-img.jpeg')
    gender = models.BooleanField(default=True)
    premium_days_left = models.IntegerField(default=0)
    username = models.CharField(blank=False, unique=True, max_length=15)
    friends = models.ManyToManyField('self', default=None)
    subscription_id_stripe = models.TextField(default="")
    customer_id_stripe = models.TextField(default="")
    followers = models.ManyToManyField('self', default=None)
    following = models.ManyToManyField('self', default=None)
    dating_with = models.ForeignKey('self', related_name="dating_with_user", on_delete=models.CASCADE, blank=True, null=True)
    users_searched_day = models.IntegerField(default=0)
    users_requested_date_day = models.IntegerField(default=0)
    feeling = models.CharField(default="nothing", max_length=15)
    about = models.CharField(max_length=30, default="A new user")
    create_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    interests = models.CharField(default="[]", max_length=50)
    chat_list = models.ManyToManyField('myapp.Group', related_name='users_chat_list', default=None)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['age', 'gender', 'email']

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

    def __str__(self):
        return self.token

    class Meta:
        ordering = ('token',)
