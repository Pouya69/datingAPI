# chat/views.py
import threading
import random
import uuid
import json
import os
from datetime import timedelta
from time import sleep as sleep_time

from django.utils import timezone
from rest_framework.authtoken.models import Token
from myapp.models import Message,Group, Date                                         # Our Message model
from userManagement.models import MyUser, VerifyLink, Story
from myapp.serializers import MessageSerializer, DateSerializer, GroupSerializerAdmins, GroupSerializerGET # Our Serializer Classes
from userManagement.serializers import PictureSerializer, InterestsSerializer, FeelingsSerializer, UserSerializer, \
    VerifySerializer, VerifyUserSerializer, UserGetSerializer
import smtplib
import base64

# headers = {'Authorization': 'Token 9054f7aa9305e012b3c2300408c3dfdf390fcddf'}

site_link = "127.0.0.1:8000/"


def get_download_link_from_file(file):
    try:
        # download_link = f"{site_link}/{file.path}"
        return file.url
    except:
        return ""


def init_tasks():
    while True:
        VerifyLink.objects.all().delete()
        # print("Deleting Verify Links Complete!")
        sleep_time(3600)


def init_tasks2():
    while True:
        MyUser.objects.all().update(users_requested_date_day=0, users_searched_day=0)
        # print("Resetting date requests and search requests!")
        sleep_time(86400)


def init_tasks3():
    while True:
        for story in Story.objects.all():
            if story.timestamp + timedelta(days=1) < timezone.now():
                story.delete()
        sleep_time(300)


def encrypt(data):
    message_bytes = data.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def decrypt(data):

    base64_bytes = data.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message


def get_message_info(message):
    mDic = {"message": {
        "content": message.content,
        "file": message.file.name,
        "creator": message.creator.username,
        "timestamp": str(message.timestamp)
    }}
    return mDic


def check_age_date(me, other):
    accepted_results = [1, 2, 0, -1, -2]
    my_age = me.age
    other_age = other.age
    resultt = my_age - other_age
    resultt2 = other_age - my_age
    if resultt in accepted_results and resultt2 in accepted_results:
        return True
    else:
        return False


def check_age(age):
    try:
        if age >= 16:
            return True
        return False
    except:
        return False


def str_to_list(stringr):
    mylist : list
    mylist = json.loads(stringr)
    return mylist


def str_to_dict(stringr):
    mylist : dict
    mylist = json.loads(stringr)
    return mylist


def list_to_str(mlist):
    mString : str
    mString = json.dumps(mlist)
    return mString


def email_link(email_user,link):
    gmail_user = 'djangorobotpouya@gmail.com'
    gmail_password = 'pooyasalehi69'

    sent_from = gmail_user
    to = [gmail_user, email_user]
    subject = 'Account Verification'
    body = """\
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        h1{ color: blue; }
    </style>
</head>
    <body>
        <h1>You are almost there!</h1><br>
        <h2>Please click <a href="{{""" + link + """ }}">here</a> to confirm your account</h2>
    </body>
</html>
"""

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
    except:
        print('Something went wrong EMAIL...')


def get_user_by_token(req_meta):
    try:
        auth_token = str(req_meta["HTTP_AUTHORIZATION"]).replace("token ", "")
        return Token.objects.get(key=auth_token).user
    except:
        return None


def get_user_random(me):
    tries = 0
    while True:
        tries += 1
        if tries >= 10:
            raise MyUser.DoesNotExist
        randomed = random.choice(MyUser.objects.all())
        if not randomed == me and randomed not in me.friends.all() and me not in randomed.block_list.all() and randomed is not me.dating_with:
            me.users_searched_day += 1
            me.save()
            return randomed


def get_user_by_interests(age_range, genderR, me):
    tries = 0
    while True:
        tries += 1
        if tries >= 10:
            raise MyUser.DoesNotExist
        randomed = random.choice(MyUser.objects.filter(gender=genderR, status=False))
        if not randomed == me and randomed not in me.friends.all() and me not in randomed.block_list.all() and randomed is not me.dating_with:
            if abs(randomed.age - me.age) <= age_range:
                me.users_searched_day += 1
                me.save()
                return randomed


def get_user_by_interests_PREMIUM(interests, age_range, genderR, me, with_interests):
    tries = 0
    while True:
        tries += 1
        if tries >= 10:
            raise MyUser.DoesNotExist
        for interest in interests:
            randomed = random.choice(MyUser.objects.filter(gender=genderR, status=False))
            if not randomed == me and randomed not in me.friends.all() and me not in randomed.block_list.all() and randomed is not me.dating_with:
                if abs(randomed.age - me.age) <= age_range:
                    if with_interests:
                        if interest in str_to_list(randomed.interests):
                            me.users_searched_day += 1
                            me.save()
                            return randomed
                    else:
                        return randomed


def date_notification(data):
    female = data['female']
    male = data['male']
    pass


def msg_notification(data):
    pass


notification_types = {
    'date': date_notification,
    'message': msg_notification
}


def notification(data):
    notification_types[data['type']](data)


def send_notification(content):
    pass


def self_delete_verifyLink(verify_obj):
    print("added link to delete")
    sleep_time(600)
    # FOR TEST : sleep_time(100)
    verify_obj.delete()
    print('VERIFY OBJ DELETED')


def generateLink(user):
    tok = str(uuid.uuid4())
    mLink = site_link + 'activate/' + tok
    try:
        p = VerifyLink.objects.get(user=user)
        p.delete()
    except VerifyLink.DoesNotExist:
        pass
    VerifyLink.objects.create(token=tok, user=user)
    ## EMAIL THE LINK
    #try:
        #email_link(user.email, mLink)
    #except:
        #print('Less Secure Apps Gmail')
