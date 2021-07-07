import re
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from stripe import Customer, Subscription, PaymentMethod
from datingAPI.appProcessing import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication
from django.contrib.auth import authenticate
from PIL import Image
from rest_framework.parsers import FileUploadParser, MultiPartParser
from .models import MyUser, VerifyLink                                         # Our Message model
from .serializers import LoginUserSerializer, UpdateUserSerializer, FriendsListSerializer, PictureSerializer, \
    InterestsSerializer, FeelingsSerializer, UserSerializer, UserGetSerializer, VerifySerializer, VerifyUserSerializer, \
    BlockListSerializer  # Our Serializer Classes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PremiumBuyView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
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
            return JsonResponse({'status': 'SORRY'}, status=404)
# TESTED SUCCESS


class RegisterView(APIView):
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            if data['gender'] == 'male':
                data['gender'] = True
            else:
                data['gender'] = False
            try:
                data['age'] = int(data['age'])
            except:
                return JsonResponse({"status": "AGE ERROR"}, status=406)
            if not check_age(data['age']):
                return JsonResponse({'status': "AGE NOT ALLOWED"}, status=405)
            try:
                if not re.match("^[a-z0-9_]*$", data['username']):
                    return JsonResponse({"status": "Invalid characters in username"}, status=402)
                regexx = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.match(regexx, data['email']):
                    return JsonResponse({"status": "Invalid characters in email"}, status=402)
            except:
                return JsonResponse({"status": "ERROR"}, status=500)
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                user = MyUser.objects.get(username=data['username'], email=data['email'])
                user.set_password(str(data['password']))
                user.save()
                # do some stuff
                generateLink(user)
                # continue doing stuff
                return JsonResponse({'status': 'REGISTER OK VERIFY'}, status=200)
            else:
                return JsonResponse(serializer.errors, status=400)

        except:
            return JsonResponse({"status": "SORRY"})


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


# TESTED
class VerifyView(APIView):
    def get(self, request, token):
        if token:
            # print(token)
            try:
                p = VerifyLink.objects.get(token=token)
                token_user = p.user
                userp = MyUser.objects.get(username=token_user.username, email=token_user.email, age=token_user.age)
                userp.is_verified = True
                userp.save()
                p.delete()
                # Remeber to make response in HTML because they are using the browser!
                return JsonResponse({'status': 'VERIFED'}, status=200)
            except VerifyLink.DoesNotExist:
                return JsonResponse({'status': 'BAD-TOKEN'}, status=404)
        else:
            return JsonResponse({'status': 'BAD TOKEN'}, status=404)
# TESTED


class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
        try:
            p = Token.objects.get(user=me)
            p.delete()
            return JsonResponse({'status': 'LOGGED OUT'}, status=200)
        except MyUser.DoesNotExist:
            return JsonResponse({'status': 'INVALID CREDENTIALS'}, status=404)


class InterestsView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
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
            return JsonResponse({'status': 'Invalid token'}, status=404)
        if username:
            try:
                userr = MyUser.objects.get(username=username)
                if me in userr.block_list.all():
                    return JsonResponse({'status': 'You are blocked'}, status=410)
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


class FeelingsView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None):
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
        if username:
            try:
                usr = MyUser.objects.get(username=username)
                if me in usr.block_list.all():
                    return JsonResponse({'status': 'You are blocked'}, status=410)
                serializer = FeelingsSerializer(usr, many=False, context={'request': request})
                return JsonResponse(serializer.data, status=200)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'username not exists'}, status=400)
        serializer = FeelingsSerializer(me, many=False, context={'request': request})
        return JsonResponse(serializer.data, status=200)

    def put(self, request):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
        serializer = FeelingsSerializer(me, data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=404)
# TESTED


class ProfilePictureView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, )

    def put(self, request):
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
        try:
            f = request.FILES["file"]
        except:
            return JsonResponse({"status": "ERROR FILE"}, status=500)
        if f.size > (6 * (1024 * 1024)):
            return JsonResponse({'status': 'File Size more than 6 MB'}, status=405)
        try:
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
            return JsonResponse({"status": "Invalid Token"}, status=404)
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
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
        if username:
            try:
                user = MyUser.objects.get(username=username)
            except MyUser.DoesNotExist:
                return JsonResponse({'status': 'USER NOT EXISTS'}, status=404)
            final_data = UserGetSerializer(user, many=False, context={'request': request}).data
            # changes in interests and etc.
            final_data['interests'] = str_to_list(final_data['interests'])
            return JsonResponse(final_data, status=200)
        try:
            reqGen = data['reqGender']
            reqGen = True if reqGen == "true" else False
        except KeyError:
            reqGen = True if me.gender is False else False
        minterests = str_to_list(me.interests)
        if not minterests:
            return JsonResponse({'status': 'YOUR INTERESTS EMPTY'}, status=405)
        try:
            age_range = int(data['age_range'])
        except KeyError:
            age_range = 100
        if me.premium_days_left > 0:
            try:
                with_interests = True if data['with_interests'] == "true" else False
            except KeyError:
                with_interests = False
            try:
                final_data = UserGetSerializer(get_user_by_interests_PREMIUM(minterests, age_range, reqGen, me, with_interests), many=False, context={'request': request}).data
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
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def put(self, request):  # We will send the notifications in the client side
        data = JSONParser().parse(request)
        me_user = get_user_by_token(request.META)
        if me_user is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
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
        if userModel in me_user.friends.all() and userModel is me_user:
            return JsonResponse({'status': 'ALREADY EXISTS'}, status=400)
        me_user.friends.add(userModel)
        me_user.save()
        return JsonResponse({'status': 'ADDED'}, status=200)

    def get(self, request):
        me_user = get_user_by_token(request.META)
        if me_user is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
        serializer = FriendsListSerializer(me_user)
        return JsonResponse(serializer.data, safe=False, status=200)

    def delete(self, request):
        data = JSONParser().parse(request)
        me_user = get_user_by_token(request.META)
        if me_user is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
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
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            me = get_user_by_token(request.META)
            if me is None:
                return JsonResponse({"status": "Invalid Token"}, status=404)
            serializer = LoginUserSerializer(me, many=False, context={'request': request})
            serializer.data['interests'] = str_to_list(serializer.data['interests'])
            return JsonResponse(serializer.data, status=200)
        except MyUser.DoesNotExist:
            return JsonResponse({"status": "Not Found"}, status=404)
        except:
            return JsonResponse({"status": "BAD"}, status=400)

    def post(self, request):  # Change Password
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'invalid Token'}, status=403)
        try:
            previous_password = data['prev_password']
            new_password = data['new_password']
        except KeyError:
            return JsonResponse({"status": "No Passwords Given"}, status=404)
        if not me.check_password(previous_password):
            return JsonResponse({'status': 'INVALID CREDENTIALS'}, status=405)
        me.set_password(new_password)
        me.save()
        return JsonResponse({'status': 'Password Changed'}, status=200)

    def put(self, request):  # Change User Details
        try:
            data = JSONParser().parse(request)
            me = get_user_by_token(request.META)
            if me is None:
                return JsonResponse({"status": "Invalid Token"}, status=403)
            try:
                regexx = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.match("^[a-z0-9_]*$", data['username']):
                    return JsonResponse({"status": "Invalid characters in username"}, status=402)
                if not re.match(regexx, data['email']):
                    return JsonResponse({"status": "Invalid characters in email"}, status=402)
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
    # TEST THIS ONE HERE


class RefreshToken(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
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
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
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
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
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
            return JsonResponse({"status": "Invalid Token"}, status=403)
        serializer = BlockListSerializer(me)
        return JsonResponse(serializer.data, safe=False, status=200)


class DateView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, date_id=None):
        me = get_user_by_token(request)
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
        data = JSONParser().parse(request)
        try:
            me = get_user_by_token(request.META)
        except KeyError:
            return JsonResponse({'status': 'Invalid token'}, status=404)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
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
        if with_who.gender is True:
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
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
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
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
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
