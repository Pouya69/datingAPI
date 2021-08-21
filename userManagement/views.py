import re
from datetime import date

import requests
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from stripe import Customer, Subscription, PaymentMethod
from datingAPI.appProcessing import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication
from django.contrib.auth import authenticate
from PIL import Image
from rest_framework.parsers import MultiPartParser
from .models import MyUser, VerifyLink, Story  # Our Message model
from .serializers import LoginUserSerializer, UpdateUserSerializer, FriendsListSerializer, PictureSerializer, \
    FeelingsSerializer, UserSerializer, UserGetSerializer, \
    BlockListSerializer  # Our Serializer Classes
from moviepy.editor import VideoFileClip

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# TODO: Ads for free premium searches
class PremiumBuyView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # data = JSONParser().parse(request)
        # email = data['email']
        # payment_method_id = None
        # payment_method_obj = None
        # try:
        #     card_number = data["card_number"]
        #     card_cvc = data["card_cvc"]
        #     card_exp_year = int(data["card_exp_year"])
        #     card_exp_month = int(data["card_exp_month"])
        # except KeyError:
        #     payment_method_id = data["payment_method_id"]
        # except TypeError:
        #     return JsonResponse({"status": "INVALID VALUES"}, status=400)
        #
        # if payment_method_id:
        #     try:
        #         payment_method_obj = PaymentMethod.retrieve(payment_method_id,)
        #     except:
        #         return JsonResponse({"status": "No Payment found"}, status=404)
        # else:
        #     payment_method_obj = PaymentMethod.create(
        #         type="card",
        #         card={
        #             "number": card_number,
        #             "exp_month": card_exp_month,
        #             "exp_year": card_exp_year,
        #             "cvc": card_cvc,
        #         },
        #     )
        #
        # customer_data = Customer.list(email=email).data
        #
        # extra_msg = ""
        # # if the array is empty it means the email has not been used yet
        # if len(customer_data) == 0:
        #     # creating customer
        #     customer = Customer.create(
        #     email=email, payment_method=payment_method_obj.id, invoice_settings={
        #     'default_payment_method': payment_method_obj.id
        # })
        #
        # else:
        #     customer = customer_data[0]
        #     extra_msg = "Customer already existed."
        #
        # ss = Subscription.create(
        #     customer=customer,
        #     items=[
        #         {
        #             'price': 'price_1IId2OBBdPclVL6EeTfyry3v'  # Premium Plan
        #         }
        #     ]
        # )
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
        me.premium = True
        me.save()
        # return JsonResponse({'status': 'PREMIUM OK', 'customer_id': customer.id, 'subscription_id': ss.id, 'extra_message': extra_msg}, status=200)
        return JsonResponse({'status': 'PREMIUM OK'}, status=200)


class LoginView(APIView):
    def post(self, request):
        try:
            username = ""
            email = ""
            password = ""
            data = JSONParser().parse(request)
            if "username" in data:
                if not data["username"] == "":
                    username = data['username']
            if "email" in data:
                if not data["email"] == "":
                    email = data['email']

            if "password" in data:
                if not data['password'] == "":
                    password = str(data['password'])

            if email == '' and username == '':
                return JsonResponse({'status': 'EMPTY CREDENTIALS'}, status=404)
            elif email == '' and not username == '' and not password == '':
                try:
                    userModel = MyUser.objects.get(username=username)
                except MyUser.DoesNotExist:
                    return JsonResponse({'status': 'No User Found with username'}, status=406)
                if not userModel.check_password(password):
                    return JsonResponse({'status': 'INVALID CREDENTIALS'}, status=403)
                user = authenticate(username=username, password=password)
                if not user:
                    return JsonResponse({'status': 'Invalid Password'}, status=404)
                else:
                    if not user.is_verified:
                        return JsonResponse({'status': 'NOT VERIFIED'}, status=405)
                    token, _ = Token.objects.get_or_create(user=user)
                    serializer = LoginUserSerializer(user, many=False, context={'request': request})
                    final_data = serializer.data
                    final_data["interests"] = str_to_list(final_data["interests"])
                    return JsonResponse({'token': token.key, 'user': final_data}, status=200)

            elif username == '' and not email == '' and not password == '':
                try:
                    userModel = MyUser.objects.get(email=email)
                except MyUser.DoesNotExist:
                    return JsonResponse({'status': 'No User Found with email'}, status=406)
                if not userModel.check_password(password):
                    return JsonResponse({'status': 'INVALID CREDENTIALS3'}, status=404)
                usernameA = userModel.username
                user = authenticate(username=usernameA, password=password)
                if not user:
                    return JsonResponse({'status': 'Invalid Password'}, status=404)
                if not user.is_verified:
                    return JsonResponse({'status': 'NOT VERIFIED'}, status=405)
                token, _ = Token.objects.get_or_create(user=user)
                serializer = LoginUserSerializer(user, many=False, context={'request': request})
                final_data = serializer.data
                final_data["interests"] = str_to_list(final_data["interests"])
                return JsonResponse({'token': token.key, 'user': final_data}, status=200)

            else:
                return JsonResponse({'status': 'EMPTY FIELDS'}, status=404)
        except:
            return JsonResponse({'status': 'SORRY'}, status=500)
# TESTED SUCCESS


class UserNameCheckView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        username = data['username']
        if not re.match("^[a-z0-9_]*$", data['username']) or not data['username'][0].isalpha():
            return JsonResponse({"status": "Invalid characters in username"}, status=402)
        for word in swear_words:
            if word in data['username']:
                return JsonResponse({"status": "username is offensive"}, status=410)
        if len(data['username']) < 5:
            return JsonResponse({"status": "username needs to be at least 5 characters long"}, status=406)
        try:
            _ = MyUser.objects.get(username=username).username
            return JsonResponse({'status': "Username already taken"}, status=404)
        except MyUser.DoesNotExist:
            return JsonResponse({'status': "Username available"}, status=200)
        except KeyError:
            return JsonResponse({'status': "No Username Provided"}, status=405)


class RegisterView(APIView):
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            date_of_birth = date.fromisoformat(data['date_of_birth'])
            if int((date.today() - date_of_birth).days / 365) < 13:
                return JsonResponse({"status": "Should be more than 13"}, status=408)
            data['date_of_birth'] = date_of_birth
            try:
                if len(data['password']) < 8:
                    return JsonResponse({"status": "Password needs to be at least 5 characters long"}, status=411)
                regexx = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.match(regexx, data['email']):
                    return JsonResponse({"status": "Invalid characters in email"}, status=405)
                if not re.match("^[a-z0-9_]*$", data['username']) or not data['username'][0].isalpha():
                    return JsonResponse({"status": "Invalid characters in username"}, status=402)
                if len(data['username']) < 5:
                    return JsonResponse({"status": "username needs to be at least 5 characters long"}, status=406)
                for word in swear_words:
                    if word in data['username'] or word in data['full_name'].lower():
                        return JsonResponse({"status": "username or name is offensive"}, status=410)
            except:
                return JsonResponse({"status": "ERROR"}, status=500)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                user = MyUser.objects.get(username=data['username'], email=data['email'])
                user.set_password(str(data['password']))
                user.account_type = "normal"
                user.save()
                # do some stuff
                generateLink(user)
                # continue doing stuff
                return JsonResponse({'status': 'REGISTER OK VERIFY'}, status=200)
            else:
                return JsonResponse(serializer.errors, status=400)

        except:
            return JsonResponse({"status": "SORRY"}, status=500)


@csrf_exempt
def sendVerifyLinkAgain(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            email = data['email']
        except:
            return JsonResponse({'status': 'EMPTY FIELDS'}, status=404)
        try:
            me = MyUser.objects.get(email=email)
        except MyUser.DoesNotExist:
            me = None
        if me is None:
            return JsonResponse({'status': 'INVALID CREDENTIALS'}, status=404)
        if me.is_verified:
            return JsonResponse({'status': 'ALREADY VERIFIED'}, status=401)
        try:
            l = VerifyLink.objects.get(user=me)
            m_link = site_link + 'activate/' + l.token
            try:
                email_thread = threading.Thread(target=email_link, name="self_user", args=(me.email, m_link))
                email_thread.start()
                return JsonResponse({'status': 'EMAILED PREVIOUS'}, status=200)
            except:
                print('EMAIL AGAIN FAILED')
                return JsonResponse({'status': 'EMAIL AGAIN FAILED'}, status=400)
        except VerifyLink.DoesNotExist:
            generateLink(me)
            return JsonResponse({'status': 'ANOTHER LINK'}, status=200)


# No apple because it costs money
class GoogleView(APIView):
    def post(self, request):
        dataa = JSONParser().parse(request)
        try:
            payload = {'access_token': dataa['token']}  # validate the token
        except KeyError:
            return JsonResponse({'status': 'ERROR'}, status=500)
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)

        if 'error' in data:
            content = {'message': 'wrong google token / this google token is already expired.'}
            return JsonResponse(content, status=404)

        # create user if not exist
        try:
            user = MyUser.objects.get(email=data['email'])
            if not user.account_type == "google":
                return JsonResponse({"status": "Access Denied"}, status=406)
        except KeyError:
            return JsonResponse({"status": "Error"}, status=500)
        except MyUser.DoesNotExist:
            try:
                if dataa['gender'] == 'male':
                    pass
                else:
                    pass
                date_of_birth = date.fromisoformat(dataa['date_of_birth'])
                if int((date.today() - date_of_birth).days / 365) < 13:
                    return JsonResponse({"status": "Should be more than 13"}, status=408)
                user = MyUser()
                user.email = data['email']
                if not re.match("^[a-z0-9_]*$", dataa['username']) or not dataa['username'][0].isalpha():
                    return JsonResponse({"status": "Invalid characters in username"}, status=402)
                if len(dataa['username']) < 5:
                    return JsonResponse({"status": "username needs to be at least 5 characters long"}, status=402)
                for word in swear_words:
                    if word in dataa['username'] or word in dataa['full_name'].lower():
                        return JsonResponse({"status": "username or name is offensive"}, status=410)
                user.username = dataa['username']
                user.full_name = dataa['full_name']
                user.date_of_birth = date_of_birth
                user.gender = dataa['gender']
                user.account_type = "google"
                # provider random default password
                user.is_verified = True  # No verification for Google users
                user.set_password(make_password(BaseUserManager().make_random_password()))
                user.save()
            except:
                return JsonResponse({"status": "Error"}, status=500)

        token = RefreshToken.for_user(user)  # generate token without username & password
        response = {}
        serializer = LoginUserSerializer(user, many=False, context={'request': request})
        final_data = serializer.data
        final_data["interests"] = str_to_list(final_data["interests"])
        response['user'] = final_data
        response['access_token'] = str(token.access_token)
        response['refresh_token'] = str(token)
        return JsonResponse(response, status=200)


class ForgotPasswordView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if not me.account_type == "normal":
            return JsonResponse({'status': 'You cannot change a third party account password'}, status=406)
        generateLinkPassword(me)
        return JsonResponse({"status": "Sent"}, status=200)
        ###################

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            new_password = data['new_password']
            verify_token = data['verify_token']
        except KeyError:
            return JsonResponse({"status": "Error"}, status=500)
        if not me.account_type == "normal":
            return JsonResponse({'status': 'You cannot change a third party account password'}, status=406)
        try:
            v = VerifyLink.objects.get(token=verify_token)
        except VerifyLink.DoesNotExist:
            return JsonResponse({"status": "Verify Token Invalid"}, status=404)
        if not v.user == me:
            return JsonResponse({"status": "Not your account"}, status=408)
        if v.extra_data == "OK":
            me.set_password(new_password)
            me.save()
            v.delete()
            return JsonResponse({"status": "Password Changed"}, status=200)
        return JsonResponse({"status": "Not verified"}, status=405)


# TESTED
class VerifyView(APIView):
    def get(self, request, token=None):
        if token:
            try:
                p = VerifyLink.objects.get(token=token)
            except VerifyLink.DoesNotExist:
                return JsonResponse({'status': 'BAD-TOKEN'}, status=404)
            token_user = p.user
            userp = MyUser.objects.get(email=token_user.email)
            if p.verify_type == "register":
                userp.is_verified = True
                userp.save()
                p.delete()
            elif p.verify_type == "email":  # Change email
                userp.email = p.extra_data
                userp.save()
                p.delete()
            else:  # Forgot Password
                p.extra_data = "OK"
                p.save()
                return JsonResponse({'verify_token': p.token}, status=200)

            # Remeber to make response in HTML because they are using the browser!
            return JsonResponse({'status': 'VERIFED'}, status=200)
        else:
            return JsonResponse({'status': 'BAD TOKEN'}, status=404)
# TESTED


class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        try:
            if me.account_type == "normal":
                p = Token.objects.get(user=me)
                p.delete()
                return JsonResponse({'status': 'LOGGED OUT'}, status=200)
            else:
                RefreshToken.for_user(user=me)
        except MyUser.DoesNotExist:
            return JsonResponse({'status': 'INVALID CREDENTIALS'}, status=404)


class InterestsView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            interests = list_to_str([str(i) for i in data['interests']])
        except:
            return JsonResponse({'status': 'interests error'}, status=404)
        me.interests = interests
        me.save()
        mydic = {'interests': str_to_list(me.interests)}
        return JsonResponse(mydic, status=200)

    def get(self, request, username=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if username:
            try:
                userr = MyUser.objects.get(username=username)
                if me in userr.block_list.all():
                    return JsonResponse({'status': 'You are blocked'}, status=410)
                if userr.private is True:
                    if me not in userr.friends.all():
                        return JsonResponse({'status': 'You are not in their friend list. private account'}, status=406)
                mList = str_to_list(userr.interests)
                mydic = {}
                mydic['interests'] = mList
                return JsonResponse(mydic, status=200)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'USER NOT FOUND'}, status=404)
        mList = str_to_list(me.interests)
        mydic = {'interests': mList}
        return JsonResponse(mydic, status=200)
# TESTED


class StoryView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if username:
            try:
                usr = MyUser.objects.get(username=username)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'username not exists'}, status=404)
            my_age = me.get_age()
            user_age = usr.get_age()
            if (not check_age(my_age) and check_age(user_age)) or (check_age(my_age) and not check_age(user_age)):
                return JsonResponse({'status': 'Cannot friend or date with ages above 18 if you are under 18 and so on'}, status=409)
            if me in usr.block_list.all():
                return JsonResponse({'status': 'You are blocked'}, status=410)
            if usr.private is True:
                if me not in usr.friends.all():
                    return JsonResponse({'status': 'You are not in their friend list. private account'}, status=406)
            final_data = {'stories': {}}
            for story in usr.stories.all():
                final_data['stories'][story.id] = get_download_link_from_file(story.clip)
            return JsonResponse(final_data, status=200)
        else:
            final_data = {'stories': {}}
            for story in me.stories.all():
                final_data['stories'][story.id] = get_download_link_from_file(story.clip)
            return JsonResponse(final_data, status=200)

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        try:
            data = json.loads(request.POST['data'])
        except:
            return JsonResponse({'status': 'Bad Request'}, status=400)
        try:
            f = request.FILES["file"]
        except:
            return JsonResponse({"status": "ERROR FILE"}, status=500)
        if f.size > (8 * (1024 * 1024)):
            return JsonResponse({'status': 'File Size more than 6 MB'}, status=405)
        try:
            story_type = data['story_type']
        except KeyError:
            return JsonResponse({'status': 'No Story Type'}, status=404)
        if story_type == "video":
            story = Story()
            try:
                story.clip.save(f.name, f, save=True)
                story.save()
                video = VideoFileClip(story.clip.path)
                seconds = int(video.duration)
                if seconds > 10:
                    video.close()
                    story.clip.delete()
                    story.delete()
                    return JsonResponse({'status': 'Video more than 10 seconds'}, status=408)

                me.add_story(story)
                return JsonResponse({'status': 'SUCCESS UPLOAD'}, status=200)
            except:
                try:
                    story.clip.delete()
                    story.delete()
                except:
                     pass
                return JsonResponse({'status': 'Video Error'}, status=406)
        try:
            img = Image.open(f)
            img.verify()
            story = Story()
            story.clip.save(f.name, f, save=True)
            story.save()
            me.add_story(story)
            return JsonResponse({'status': 'SUCCESS UPLOAD'}, status=200)
        except:
            return JsonResponse({"status": "Unsupported image type"}, status=401)

    def delete(self, request, story_id=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if story_id:
            story = Story.objects.get(id=int(story_id))
            story.clip.delete()
            story.delete()
            me.save()
            return JsonResponse({'status': 'Story deleted'}, status=201)


class FeelingsView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if username:
            try:
                usr = MyUser.objects.get(username=username)
                if me in usr.block_list.all():
                    return JsonResponse({'status': 'You are blocked'}, status=410)
                my_age = me.get_age()
                user_age = usr.get_age()
                if (not check_age(my_age) and check_age(user_age)) or (check_age(my_age) and not check_age(user_age)):
                    return JsonResponse({'status': 'Cannot friend or date with ages above 18 if you are under 18 and so on'}, status=409)
                if usr.private is True:
                    if me not in usr.friends.all():
                        return JsonResponse({'status': 'You are not in their friend list. private account'}, status=406)
                serializer = FeelingsSerializer(usr, many=False, context={'request': request})
                return JsonResponse(serializer.data, status=200)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'username not exists'}, status=404)
        serializer = FeelingsSerializer(me, many=False, context={'request': request})
        return JsonResponse(serializer.data, status=200)

    def put(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        serializer = FeelingsSerializer(me, data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=404)
# TESTED


class ProfilePictureView(APIView):  # TODO: In client side. Make a limitation (too fast)
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, )

    def put(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        try:
            f = request.FILES["file"]
        except:
            return JsonResponse({"status": "ERROR FILE"}, status=500)
        if f.size > (6 * (1024 * 1024)):
            return JsonResponse({'status': 'File Size more than 6 MB'}, status=405)
        try:
            me.remove_old_profile_pic()
            img = Image.open(f)
            img.verify()
            me.profile_pic.save(f.name, f, save=True)
            me.save()  # Here if error
            return JsonResponse({'status': 'SUCCESS UPLOAD'}, status=200)
        except:
            return JsonResponse({"status": "Unsupported image type"}, status=401)

    def get(self, request, username=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if username:
            try:
                user = MyUser.objects.get(username=username)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'USER NOT EXISTS'}, status=404)
            serializer = PictureSerializer(user, many=False, context={'request': request})
            serializer.data['profile_pic'] = get_download_link_from_file(serializer.data['profile_pic'])
            return JsonResponse(serializer.data, safe=False, status = 200)

        else:
            serializer = PictureSerializer(me, many=False, context={'request': request})
            serializer.data['profile_pic'] = get_download_link_from_file(serializer.data['profile_pic'])
            return JsonResponse(serializer.data, status=200)


class UsersListView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        if username:
            try:
                user = MyUser.objects.get(username=username)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'USER NOT EXISTS'}, status=404)
            if me in user.block_list.all():
                return JsonResponse({'status': 'You are blocked'}, status=410)
            my_age = me.get_age()
            user_age = user.get_age()
            if (not check_age(my_age) and check_age(user_age)) or (check_age(my_age) and not check_age(user_age)):
                return JsonResponse({'status': 'Cannot friend or date with ages above 18 if you are under 18 and so on'}, status=409)
            if user.private is True:
                if me not in user.friends.all():
                    return JsonResponse({'status': 'You are not in their friend list. private account'}, status=406)
            final_data = UserGetSerializer(user, many=False, context={'request': request}).data
            # changes in interests and etc.
            final_data['interests'] = str_to_list(final_data['interests'])
            return JsonResponse(final_data, status=200)
        try:
            reqGen = data['reqGender']
        except KeyError:
            reqGen = "male" if me.gender == "female" else "female"
        minterests = str_to_list(me.interests)
        if not minterests:
            return JsonResponse({'status': 'YOUR INTERESTS EMPTY'}, status=405)
        try:
            age_range = int(data['age_range'])
            country = data['country']
        except KeyError:
            age_range = 100
        except ValueError:
            return JsonResponse({'status': 'ERROR'}, status=500)
        if not check_age(me.get_age()):
            if age_range > 5:
                age_range = 5
        if me.premium_days_left > 0:
            try:
                with_interests = True if data['with_interests'] == "true" else False
            except KeyError:
                with_interests = False
            try:
                final_data = UserGetSerializer(get_user_by_interests_PREMIUM(minterests, age_range, reqGen, me, with_interests, country=country), many=False, context={'request': request}).data
                # changes in interests and etc.
                final_data['interests'] = str_to_list(final_data['interests'])
                return JsonResponse(final_data, status=200)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'No User Found'}, status=500)
        if not me.users_searched_day <= 5:
            try:
                final_data = UserGetSerializer(get_user_by_interests(age_range, reqGen, me), many=False, context={'request': request}).data
                # changes in interests and etc.
                final_data['interests'] = str_to_list(final_data['interests'])
                return JsonResponse(final_data, status=200)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'No User Found'}, status=500)
        try:
            final_data = UserGetSerializer(get_user_random(me), many=False, context={'request': request}).data
            # changes in interests and etc.
            final_data['interests'] = str_to_list(final_data['interests'])
            return JsonResponse(final_data, status=200)
        except MyUser.DoesNotExist:
            return JsonResponse({'status': 'No User Found'}, status=500)


class FriendsListView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def put(self, request):  # We will send the notifications in the client side
        me_user = get_user_by_token(request.META)
        if me_user is None:
            me_user = request.user
            if me_user is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            username = data['user_username']
        except:
            return JsonResponse({'status': 'Username Error'}, status=500)
        try:
            userModel = MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return JsonResponse({'status': 'User does not exists'}, status=404)
        if me_user in userModel.block_list.all():
            return JsonResponse({'status': 'You are blocked'}, status=410)
        if userModel in me_user.friends.all() or userModel is me_user:
            return JsonResponse({'status': 'ALREADY EXISTS'}, status=400)
        my_age = me_user.get_age()
        user_age = userModel.get_age()
        if (not check_age(my_age) and check_age(user_age)) or (check_age(my_age) and not check_age(user_age)):
            return JsonResponse({'status': 'Cannot friend or date with ages above 18 if you are under 18 and so on'},status=409)
        me_user.friends.add(userModel)
        me_user.save()
        return JsonResponse({'status': 'ADDED'}, status=200)

    def get(self, request, request_type=None):
        if not request_type:
            return JsonResponse({'status': 'No types'}, status=404)
        me_user = get_user_by_token(request.META)
        if me_user is None:
            me_user = request.user
            if me_user is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if request_type == "get_friends":
            serializer = FriendsListSerializer(me_user)
            return JsonResponse(serializer.data, safe=False, status=200)
        elif request_type == "friend_requests":
            final_data = {}
            users = MyUser.objects.filter(friends__in=[me_user])
            for user in users:
                if user not in me_user.friends.all():
                    final_data['friend_requests'] = user.username
            return JsonResponse(final_data, status=200)

    def delete(self, request):
        me_user = get_user_by_token(request.META)
        if me_user is None:
            me_user = request.user
            if me_user is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            friend_username = data['user_username']
        except KeyError:
            return JsonResponse({'status': 'Username Error'}, status=500)
        try:
            delete_date = data['delete_date'] if 'delete_date' in data else ""
        except KeyError:
            delete_date = ""
        try:
            friend_user = MyUser.objects.get(username=friend_username)
        except MyUser.DoesNotExist:
            return JsonResponse({"status": "USER NOT EXISTS"}, status=404)
        if friend_user not in me_user.friends.all():
            return JsonResponse({"status": "USER NOT IN FRIENDS"}, status=405)
        me_user.friends.remove(friend_user)
        if not delete_date == "":  # means OK. Delete date also
            if me_user.dating_with is not None:
                if friend_user.username == me_user.dating_with.username:
                    me_user.dating_with = None
                    friend_user.dating_with = None
                    me_user.save()
                    friend_user.save()
                    Date.objects.filter(users__in=[me_user]).get(users__in=[friend_user]).delete()
        return JsonResponse({'status': 'Friend Removed'}, status=201)


class ProfileMeView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            me = get_user_by_token(request.META)
            if me is None:
                me = request.user
                if me is None:
                    return JsonResponse({'status': 'Invalid token'}, status=403)
            serializer = LoginUserSerializer(me, many=False, context={'request': request})
            serializer.data['interests'] = str_to_list(serializer.data['interests'])
            return JsonResponse(serializer.data, status=200)
        except MyUser.DoesNotExist:
            return JsonResponse({"status": "Not Found"}, status=404)
        except:
            return JsonResponse({"status": "BAD"}, status=400)

    def post(self, request):  # Change Password
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        if not me.account_type == "normal":
            return JsonResponse({'status': 'Google accounts cannot change password. Change your password from Google'}, status=407)
        try:
            previous_password = data['prev_password']
            new_password = data['new_password']
        except KeyError:
            return JsonResponse({"status": "No Passwords Given"}, status=404)
        if not me.check_password(previous_password):
            return JsonResponse({'status': 'INVALID CREDENTIALS'}, status=405)
        if len(data['new_password']) < 8:
            return JsonResponse({"status": "Password needs to be at least 5 characters long"}, status=411)
        me.set_password(new_password)
        me.save()
        return JsonResponse({'status': 'Password Changed'}, status=200)

    def put(self, request):  # Change User Details
        try:
            me = get_user_by_token(request.META)
            if me is None:
                me = request.user
                if me is None:
                    return JsonResponse({'status': 'Invalid token'}, status=403)
            data = JSONParser().parse(request)
            try:
                regexx = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if len(data['username']) < 5:
                    return JsonResponse({"status": "username needs to be at least 5 characters long"}, status=402)
                if not re.match("^[a-z0-9_]*$", data['username']) or not data['username'][0].isalpha():
                    return JsonResponse({"status": "Invalid characters in username"}, status=402)
                for word in swear_words:
                    if word in data['username'] or word in data['full_name'].lower():
                        return JsonResponse({"status": "username or name is offensive"}, status=410)
                if not re.match(regexx, data['email']):
                    return JsonResponse({"status": "Invalid characters in email"}, status=402)
                if not data['email'] == me.email:
                    try:
                        _ = MyUser.objects.get(email=data['email'])
                        return JsonResponse({"status": "Email already exists"}, status=400)
                    except MyUser.DoesNotExist:
                        generateLinkConfirm(me, data['email'])  # We change on confirm of the previous email
            except KeyError:
                return JsonResponse({"status": "ERROR"}, status=500)
            serializer = UpdateUserSerializer(me, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except MyUser.DoesNotExist:
            return JsonResponse({"status": "Not Found"}, status=404)
        except:
            return JsonResponse({"status": "BAD"}, status=500)

    def delete(self, request):  # Delete the whole profile
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            username = data['username']
            password = data['password']
            user = MyUser.objects.get(username=username)
            if not user == me:
                return JsonResponse({"status": "User from token is not the same with user in credentials"}, status=405)
            if not user.check_password(password):
                return JsonResponse({'status': "Invalid credentials"}, status=404)
            user.delete()
        except:
            return JsonResponse({'status': "Invalid credentials"}, status=404)


class RefreshTokenn(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if not me.account_type == "google":
            token = RefreshToken.for_user(me)  # generate token without username & password
            return JsonResponse({'access_token': str(token.access_token), 'refresh_token': str(token)}, status=201)
        data = JSONParser().parse(request)
        try:
            password = data["password"]
        except KeyError:
            return JsonResponse({'status': 'Keys Not Found'}, status=404)
        if password == "":
            return JsonResponse({'status': 'Invalid Credentials'}, status=404)
        if me.check_password(password):
            if me.is_verified:
                Token.objects.get(user=me).delete()
                token, _ = Token.objects.get_or_create(user=me)
                return JsonResponse({'token': token.key}, status=201)
            else:
                return JsonResponse({'status': 'NOT VERIFIED'}, status=405)
        else:
            return JsonResponse({'status': 'INVALID CREDENTIALS3'}, status=404)


class BlockUser(APIView):  # Check this with views always. Messages, groups, date, friend add etc.
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            user = MyUser.objects.get(username=data['user_username'])
        except:
            return JsonResponse({'status': 'User Not Found'}, status=404)
        if user in me.friends.all():
            me.friends.remove(user)
            user.friends.remove(me)
        if me.dating_with == user:
            me.dating_with = None
            user.dating_with = None
            try:
                Date.objects.filter(users__in=[me]).get(users__in=[user]).delete()
            except:
                pass
        me.block_list.add(user)
        me.save()
        user.save()
        return JsonResponse({'status': 'Blocked'}, status=201)

    def delete(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            user = MyUser.objects.get(username=data['user_username'])
        except:
            return JsonResponse({'status': 'User Not Found'}, status=404)
        if user in me.block_list.all():
            me.block_list.remove(user)
        me.save()
        return JsonResponse({'status': 'Unblocked'}, status=201)

    def get(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
        serializer = BlockListSerializer(me)
        return JsonResponse(serializer.data, safe=False, status=200)


class DateView(APIView):
    authentication_classes = [authentication.TokenAuthentication, JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, date_id=None):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        if date_id:
            try:
                date = Date.objects.get(date_id=date_id)
            except Date.DoesNotExist:
                return JsonResponse({'status': 'Date not found'}, status=404)
            if me in date.users.all():
                serializer = DateSerializer(date, many=False, context={'request': request})
                return JsonResponse(serializer.data, safe=False)
            return JsonResponse({'status': 'ACCESS DENIED'}, safe=False, status=405)
        # date = Date.objects.filter(users__in=[me], allowed=True)
        dates = Date.objects.filter(creator=me)  # Only the ones that I have sent requests to. others are secret :D
        serializer = DateSerializer(dates, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        if me.premium_days_left <= 0:
            if me.users_requested_date_day > 1:
                return JsonResponse({'status': 'More than limit 1'}, status=406)
        try:
            with_who = MyUser.objects.get(username=data["with"])
        except:
            return JsonResponse({'status': 'User not found'}, status=404)
        if with_who is me:
            return JsonResponse({'status': 'Error'}, status=500)
        if me in with_who.block_list.all():
            return JsonResponse({'status': 'You are blocked'}, status=410)
        if me.dating_with or with_who.dating_with:
            return JsonResponse({'status': 'Already dating'}, status=402)
        my_age = me.get_age()
        with_who_age = with_who.get_age()
        if (not check_age(my_age) and check_age(with_who_age)) or (check_age(my_age) and not check_age(with_who_age)):
            return JsonResponse({'status': 'Cannot friend or date with ages above 18 if you are under 18 and so on'}, status=409)
        if not check_age(me.get_age()):
            if abs(with_who.get_age() - me.get_age()) > 2:
                return JsonResponse({'Age difference is too much'}, status=411)
        try:
            if Date.objects.filter(users__in=[me]).get(users__in=[with_who]).exists():
                return JsonResponse({'status': 'Already a date request'}, status=403)
        except Date.DoesNotExist:
            pass
        try:
            my_choice = False if data["type"] == "hidden" else True
        except KeyError:
            return JsonResponse({'status': 'type Key Error'}, status=404)
        if my_choice:  # If a normal date request: send notifications to both
            pass
        if with_who.gender == "female":
            date = Date(male_user=with_who, female_user=me, creator=me, request_or_hidden=my_choice, female=True)
        else:
            date = Date(male_user=me, female_user=with_who, creator=me, request_or_hidden=my_choice, male=True)

        date.save()
        date.users.add(me)
        date.users.add(with_who)
        date.save()
        me.users_requested_date_day += 1
        me.save()
        return JsonResponse({'status': 'Done'}, status=200)

    def put(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            with_who = MyUser.objects.get(username=data["with"])
        except MyUser.DoesNotExist:
            return JsonResponse({'status': 'User not found'}, status=404)
        try:
            date = Date.objects.filter(users__in=[me]).get(users__in=[with_who])
        except Date.DoesNotExist:
            return JsonResponse({'status': 'Date Does Not Exist'}, status=404)
        if me.dating_with or with_who.dating_with:
            return JsonResponse({'status': 'Already dating'}, status=402)
        # if date.male is True and date.female is True:
        if date.male_user.dating_with is date.female_user or date.female_user.dating_with is date.male_user:
            return JsonResponse({'status': 'Already dating currently'}, status=400)
        if date.creator is me:
            return JsonResponse({'status': 'You are the creator'}, status=407)
        try:
            decision = data["decision"]
        except KeyError:
            return JsonResponse({'status': 'Key Error'}, status=400)
        if decision == "OK":
            if date.male_user == me:
                date.male = True
            elif date.female_user == me:
                date.female = True
            date.save()
            if date.male is True and date.female is True:
                me.dating_with = with_who
                with_who.dating_with = me
                me.save()
                with_who.save()
                ####### Date confirmed.. SEND TO BOTH
                return JsonResponse({'status': 'Date created'}, status=200)
            return JsonResponse({'status': 'Unknown Error Occurred'}, status=500)
        else:
            date.delete()
            return JsonResponse({'status': 'Date deleted'}, status=201)
            # CUT the relationship

    def delete(self, request):  # Don't want the request eben the other one does like him/her or break up
        me = get_user_by_token(request.META)
        if me is None:
            me = request.user
            if me is None:
                return JsonResponse({'status': 'Invalid token'}, status=403)
        data = JSONParser().parse(request)
        try:
            with_who = MyUser.objects.get(username=data["with"])
        except:
            return JsonResponse({'status': 'User not found'}, status=404)
        if with_who is me:
            return JsonResponse({'status': 'Error'}, status=500)
        try:
            Date.objects.filter(users__in=[me]).get(users__in=[with_who]).delete()
            with_who.dating_with = None
            me.dating_with = None
            with_who.save()
            me.save()
        except Date.DoesNotExist:
            return JsonResponse({"status": "Date Not found"}, status=404)
        return JsonResponse({'status': 'Deleted'}, status=201)
