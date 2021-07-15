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
site_link_media = "127.0.0.1:8000"

swear_words = ['4r5e', '5h1t', '5hit', 'a55', 'anal', 'anus', 'ar5e', 'arrse', 'arse', 'ass', 'ass-fucker', 'asses', 'assfucker', 'assfukka', 'asshole', 'assholes', 'asswhole', 'a_s_s', 'b!tch', 'b00bs', 'b17ch', 'b1tch', 'ballbag', 'balls', 'ballsack', 'bastard', 'beastial', 'beastiality', 'bellend', 'bestial', 'bestiality', 'bi+ch', 'biatch', 'bitch', 'bitcher', 'bitchers', 'bitches', 'bitchin', 'bitching', 'bloody', 'blow job', 'blowjob', 'blowjobs', 'boiolas', 'bollock', 'bollok', 'boner', 'boob', 'boobs', 'booobs', 'boooobs', 'booooobs', 'booooooobs', 'breasts', 'buceta', 'bugger', 'bum', 'bunny fucker', 'butt', 'butthole', 'buttmunch', 'buttplug', 'c0ck', 'c0cksucker', 'carpet muncher', 'cawk', 'chink', 'cipa', 'cl1t', 'clit', 'clitoris', 'clits', 'cnut', 'cock', 'cock-sucker', 'cockface', 'cockhead', 'cockmunch', 'cockmuncher', 'cocks', 'cocksuck', 'cocksucked', 'cocksucker', 'cocksucking', 'cocksucks', 'cocksuka', 'cocksukka', 'cok', 'cokmuncher', 'coksucka', 'coon', 'cox', 'crap', 'cum', 'cummer', 'cumming', 'cums', 'cumshot', 'cunilingus', 'cunillingus', 'cunnilingus', 'cunt', 'cuntlick', 'cuntlicker', 'cuntlicking', 'cunts', 'cyalis', 'cyberfuc', 'cyberfuck', 'cyberfucked', 'cyberfucker', 'cyberfuckers', 'cyberfucking', 'd1ck', 'damn', 'dick', 'dickhead', 'dildo', 'dildos', 'dink', 'dinks', 'dirsa', 'dlck', 'dog-fucker', 'doggin', 'dogging', 'donkeyribber', 'doosh', 'duche', 'dyke', 'ejaculate', 'ejaculated', 'ejaculates', 'ejaculating', 'ejaculatings', 'ejaculation', 'ejakulate', 'f u c k', 'f u c k e r', 'f4nny', 'fag', 'fagging', 'faggitt', 'faggot', 'faggs', 'fagot', 'fagots', 'fags', 'fanny', 'fannyflaps', 'fannyfucker', 'fanyy', 'fatass', 'fcuk', 'fcuker', 'fcuking', 'feck', 'fecker', 'felching', 'fellate', 'fellatio', 'fingerfuck', 'fingerfucked', 'fingerfucker', 'fingerfuckers', 'fingerfucking', 'fingerfucks', 'fistfuck', 'fistfucked', 'fistfucker', 'fistfuckers', 'fistfucking', 'fistfuckings', 'fistfucks', 'flange', 'fook', 'fooker', 'fuck', 'fucka', 'fucked', 'fucker', 'fuckers', 'fuckhead', 'fuckheads', 'fuckin', 'fucking', 'fuckings', 'fuckingshitmotherfucker', 'fuckme', 'fucks', 'fuckwhit', 'fuckwit', 'fudge packer', 'fudgepacker', 'fuk', 'fuker', 'fukker', 'fukkin', 'fuks', 'fukwhit', 'fukwit', 'fux', 'fux0r', 'f_u_c_k', 'gangbang', 'gangbanged', 'gangbangs', 'gaylord', 'gaysex', 'goatse', 'God', 'god-dam', 'god-damned', 'goddamn', 'goddamned', 'hardcoresex', 'hell', 'heshe', 'hoar', 'hoare', 'hoer', 'homo', 'hore', 'horniest', 'horny', 'hotsex', 'jack-off', 'jackoff', 'jap', 'jerk-off', 'jism', 'jiz', 'jizm', 'jizz', 'kawk', 'knob', 'knobead', 'knobed', 'knobend', 'knobhead', 'knobjocky', 'knobjokey', 'kock', 'kondum', 'kondums', 'kum', 'kummer', 'kumming', 'kums', 'kunilingus', 'l3i+ch', 'l3itch', 'labia', 'lmfao', 'lust', 'lusting', 'm0f0', 'm0fo', 'm45terbate', 'ma5terb8', 'ma5terbate', 'masochist', 'master-bate', 'masterb8', 'masterbat*', 'masterbat3', 'masterbate', 'masterbation', 'masterbations', 'masturbate', 'mo-fo', 'mof0', 'mofo', 'mothafuck', 'mothafucka', 'mothafuckas', 'mothafuckaz', 'mothafucked', 'mothafucker', 'mothafuckers', 'mothafuckin', 'mothafucking', 'mothafuckings', 'mothafucks', 'mother fucker', 'motherfuck', 'motherfucked', 'motherfucker', 'motherfuckers', 'motherfuckin', 'motherfucking', 'motherfuckings', 'motherfuckka', 'motherfucks', 'muff', 'mutha', 'muthafecker', 'muthafuckker', 'muther', 'mutherfucker', 'n1gga', 'n1gger', 'nazi', 'nigg3r', 'nigg4h', 'nigga', 'niggah', 'niggas', 'niggaz', 'nigger', 'niggers', 'nob', 'nob jokey', 'nobhead', 'nobjocky', 'nobjokey', 'numbnuts', 'nutsack', 'orgasim', 'orgasims', 'orgasm', 'orgasms', 'p0rn', 'pawn', 'pecker', 'penis', 'penisfucker', 'phonesex', 'phuck', 'phuk', 'phuked', 'phuking', 'phukked', 'phukking', 'phuks', 'phuq', 'pigfucker', 'pimpis', 'piss', 'pissed', 'pisser', 'pissers', 'pisses', 'pissflaps', 'pissin', 'pissing', 'pissoff', 'poop', 'porn', 'porno', 'pornography', 'pornos', 'prick', 'pricks', 'pron', 'pube', 'pusse', 'pussi', 'pussies', 'pussy', 'pussys', 'rectum', 'retard', 'rimjaw', 'rimming', 's hit', 's.o.b.', 'sadist', 'schlong', 'screwing', 'scroat', 'scrote', 'scrotum', 'semen', 'sex', 'sh!+', 'sh!t', 'sh1t', 'shag', 'shagger', 'shaggin', 'shagging', 'shemale', 'shi+', 'shit', 'shitdick', 'shite', 'shited', 'shitey', 'shitfuck', 'shitfull', 'shithead', 'shiting', 'shitings', 'shits', 'shitted', 'shitter', 'shitters', 'shitting', 'shittings', 'shitty', 'skank', 'slut', 'sluts', 'smegma', 'smut', 'snatch', 'son-of-a-bitch', 'spac', 'spunk', 's_h_i_t', 't1tt1e5', 't1tties', 'teets', 'teez', 'testical', 'testicle', 'tit', 'titfuck', 'tits', 'titt', 'tittie5', 'tittiefucker', 'titties', 'tittyfuck', 'tittywank', 'titwank', 'tosser', 'turd', 'tw4t', 'twat', 'twathead', 'twatty', 'twunt', 'twunter', 'v14gra', 'v1gra', 'vagina', 'viagra', 'vulva', 'w00se', 'wang', 'wank', 'wanker', 'wanky', 'whoar', 'whore', 'willies', 'willy', 'xrated', 'xxx']

def get_download_link_from_file(file):
    try:
        # download_link = f"{site_link}/{file.path}"
        return f"{site_link_media}{file.url}"
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


def check_age(age):
    try:
        if age >= 18:
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
        if (not check_age(me.get_age()) and check_age(randomed.get_age())) or (check_age(me.get_age()) and not check_age(randomed.get_age())):
            continue
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
        if (not check_age(me.get_age()) and check_age(randomed.get_age())) or (check_age(me.get_age()) and not check_age(randomed.get_age())):
            continue
        if not randomed == me and randomed not in me.friends.all() and me not in randomed.block_list.all() and randomed is not me.dating_with:
            if abs(randomed.get_age() - me.get_age()) <= age_range:
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
            if (not check_age(me.get_age()) and check_age(randomed.get_age())) or (check_age(me.get_age()) and not check_age(randomed.get_age())):
                continue
            if not randomed == me and randomed not in me.friends.all() and me not in randomed.block_list.all() and randomed is not me.dating_with:
                if abs(randomed.get_age() - me.get_age()) <= age_range:
                    if with_interests:
                        if interest in str_to_list(randomed.interests):
                            me.users_searched_day += 1
                            me.save()
                            return randomed
                    else:
                        me.users_searched_day += 1
                        me.save()
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
    VerifyLink.objects.create(token=tok, user=user, verify_type="register")
    ## EMAIL THE LINK
    #try:
        #email_link(user.email, mLink)
    #except:
        #print('Less Secure Apps Gmail')


def generateLinkConfirm(user, newEmail):
    tok = str(uuid.uuid4())
    mLink = site_link + 'activate/' + tok
    try:
        p = VerifyLink.objects.get(user=user)
        p.delete()
    except VerifyLink.DoesNotExist:
        pass
    VerifyLink.objects.create(token=tok, user=user, verify_type="email", extra_data=newEmail)
    ## EMAIL THE LINK
    #try:
        #email_link(user.email, mLink)
    #except:
        #print('Less Secure Apps Gmail')
