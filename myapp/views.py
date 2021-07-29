# chat/views.py
import os
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from datingAPI.appProcessing import *
import re
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication
from PIL import Image
from rest_framework.parsers import FileUploadParser, MultiPartParser
from .models import Message, Group, Date, FileMessage  # Our Message model
from .serializers import GroupPictureSerializer, \
    GroupSerializerAdmins, GroupSerializerGET, GroupSerializerIdChat  # Our Serializer Classes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# headers = {'Authorization': 'Token 9054f7aa9305e012b3c2300408c3dfdf390fcddf'}


# To get data from headers : request.META["HTTP_AUTHORIZATION"]

def index(request):
    return render(request, 'chat/index.html')


def room(request, chat_id=None):
    if chat_id:
        try:
            Group.objects.get(id=int(chat_id))
            # Later on we'll use json not html.
            return render(request, 'chat/chat.html', {
                'room_name': chat_id
            })
        except:
            return JsonResponse({'status': 'No Chat found with this id'}, status=404)

    else:
        return JsonResponse({'status': 'No Chat ID found'}, status=404)


class FileUploadMessage(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        data = json.loads(request.data['data'])
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid Token'}, status=404)
        try:
            file = request.FILES["file"]
            if file.size > (15 * (1024 * 1024)):
                return JsonResponse({'status': 'File Size more than 15 MB'}, status=403)
            try:
                if me not in Group.objects.get(id=data['group_id']).users.all():
                    return JsonResponse({'status': 'You cannot access the group'}, status=407)
            except Group.DoesNotExist:
                return JsonResponse({'status': 'Group Access Error'}, status=404)
            file_message_model = FileMessage()
            file_message_model.save()
            file_message_model.file_file.save(file.name, file, save=True)
            file_message_model.save()  # Here if error
            return JsonResponse({'download_url': get_download_link_from_file(file_message_model.file_file)}, status=200)
        except:
            return JsonResponse({'status': 'File Error'}, status=500)


def join_chat(request, chat_id=None):
    # We'll make the invite link from the client-side
    if chat_id:
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid Token'}, status=403)
        try:
            group = Group.objects.get(id=int(chat_id))
        except:
            return JsonResponse({'status': 'Invalid Group'}, status=404)
        if group not in me.chat_list.all() and me not in group.users.all():
            for user in group.users.all():
                if (not check_age(me.get_age()) and check_age(user.get_age())) or (check_age(me.get_age()) and not check_age(user.get_age())):
                    return JsonResponse({'status': 'Cannot be in group with ages above 18 if you are under 18 and so on'}, status=409)
            group.join_chat(me)
            me.chat_list.add(group)
            return JsonResponse({'status': 'Joined Group'}, status=200)
        return JsonResponse({'status': 'Already in the group'}, status=402)
    return JsonResponse({'status': 'Chat ID None'}, status=405)


class GroupListView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def get(self, request, chat_id=None):
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
        if chat_id:
            try:
                group = Group.objects.get(id_chat=chat_id)
            except Group.DoesNotExist:
                return JsonResponse({'status': 'Invalid chat_id'}, status=404)
            if me not in group.users.all():
                return JsonResponse({'status': 'You are not in the group'}, status=405)
            final_data = GroupSerializerGET(group, many=False, context={'request': request}).data
            return JsonResponse(final_data, status=200)
        final_data = GroupSerializerGET(me.chat_list.all(), many=True, context={'request': request}).data
        return JsonResponse(final_data, status=200)

    def post(self, request):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
        try:
            data_users = data['users']
            group = Group(owner=me)
            group.save()
            for u_username in data_users:
                try:
                    user = MyUser.objects.get(username=u_username)
                    if me in user.block_list.all():
                        return JsonResponse({'status': f'You are blocked by {user.username}'}, status=410)
                    for user in group.users.all():
                        if (not check_age(me.get_age()) and check_age(user.get_age())) or (check_age(me.get_age()) and not check_age(user.get_age())):
                            return JsonResponse({'status': 'Cannot be in group with ages above 18 if you are under 18 and so on'}, status=409)
                    group.users.add(user)
                except MyUser.DoesNotExist:
                    group.delete()
                    return JsonResponse({"status": "User not exists GROUP POST"}, status=503)
        except:
            return JsonResponse({"status": "Error in user lists"}, status=500)
        group.save()
        group.admins.add(me)
        group.users.add(me)
        for u in group.users.all():
            u.chat_list.add(group)
            u.save()
        group.save()
        final_data = GroupSerializerGET(group, many=False, context={'request': request}).data
        # final_data['last_message'] = str_to_dict(final_data['last_message'])
        return JsonResponse(final_data, status=200)

    def put(self, request, chat_id=None):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if not chat_id:
            return JsonResponse({'status': 'Invalid chat_id'}, status=404)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
        try:
            group = Group.objects.get(id=chat_id)
        except Group.DoesNotExist:
            return JsonResponse({'status': 'Invalid chat_id'}, status=404)
        users = group.users.all()
        admins = group.admins.all()
        if me not in users:
            return JsonResponse({'status': 'ACCESS DENIED'}, status=405)
        try:
            command = data['command']
        except KeyError:
            return JsonResponse({'status': 'No Commands'}, status=404)
        except TypeError:
            return JsonResponse({'status': 'No Commands'}, status=404)
        if command == "add_users":
            try:
                users_add = data["users"]
                for add_username in users_add:
                    try:
                        user_user = MyUser.objects.get(username=add_username)
                        if user_user == me:
                            return JsonResponse({'status': 'You are the user'}, status=402)
                        if me in user_user.block_list.all():
                            return JsonResponse({'status': 'You are blocked'}, status=410)
                        for user in group.users.all():
                            if (not check_age(me.get_age()) and check_age(user.get_age())) or (check_age(me.get_age()) and not check_age(user.get_age())):
                                return JsonResponse({'status': 'Cannot be in group with ages above 18 if you are under 18 and so on'}, status=409)
                        if me not in user_user.friends.all() or user_user not in me.friends.all():
                            return JsonResponse({'status': 'You are not friends'}, status=407)
                        if not user_user not in users:
                            group.users.add(user_user)
                            group.save()
                            final_data = GroupSerializerAdmins(group, many=False, context={'request': request}).data
                            # final_data['last_message'] = str_to_dict(final_data['last_message'])
                            return JsonResponse(final_data, status=200)
                    except MyUser.DoesNotExist:
                        return JsonResponse({'status': f'User not vaild : {add_username}'}, status=404)
            except:
                return JsonResponse({'status': f'Users not vaild'}, status=404)
        if me not in admins:
            return JsonResponse({'status': 'NOT ADMIN'}, status=403)
        elif command == "new_chat_id":
            try:
                new_id = data["id_chat"]
                if not new_id == "" and new_id is not None:
                    if not re.match("^[a-z0-9_]*$", new_id):
                        return JsonResponse({"status": "Invalid characters in chat id"}, status=408)
                    serializer = GroupSerializerIdChat(group, data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return JsonResponse(serializer.errors, status=406)
            except KeyError:
                return JsonResponse({'status': 'No chat id provided'}, status=404)
        elif command == "new_owner":
            try:
                new_owner_username = data["new_owner"]
                if not new_owner_username == "" or new_owner_username is not None:
                    if group.owner == me:
                        try:
                            group.owner = MyUser.objects.get(username=new_owner_username)
                        except MyUser.DoesNotExist:
                            group.save()
                            return JsonResponse({'status': 'Owner user not valid'}, status=404)
                    else:
                        group.save()
                        return JsonResponse({'status': 'You are not the owner'}, status=403)
            except KeyError:
                return JsonResponse({'status': 'No owner provided'}, status=404)
        elif command == "new_admins":
            try:
                new_admins = data["new_admins"]
                for admin_username in new_admins:
                    try:
                        user_admin = MyUser.objects.get(username=admin_username)
                        if user_admin not in admins and not user_admin == me:
                            group.admins.add(user_admin)
                        else:
                            return JsonResponse({'status': 'Admin add error'}, status=405)
                    except MyUser.DoesNotExist:
                        group.save()
                        return JsonResponse({'status': 'Admins not valid'}, status=404)
            except:
                return JsonResponse({'status': 'No admins provided'}, status=404)
        group.save()
        final_data = GroupSerializerAdmins(group, many=False, context={'request': request}).data
        # final_data['last_message'] = str_to_dict(final_data['last_message'])
        return JsonResponse(final_data, status=200)

    def delete(self, request, chat_id=None):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=403)
        try:
            command = data['command']
            if command == "":
                raise KeyError
        except KeyError:
            return JsonResponse({'status': 'No Commands'}, status=404)
        try:
            group = Group.objects.get(id=chat_id)
        except Group.DoesNotExist:
            return JsonResponse({'status': 'GROUP NOT EXISTS'}, status=404)

        if command == "delete_group":
            if group.owner == me:
                group.delete()
                return JsonResponse({'status': 'DELETED'}, status=200)
            me.chat_list.remove(group)
            group.users.remove(me)
            if me in group.admins:
                group.admins.remove(me)
            me.save()
            group.save()
            return JsonResponse({'status': 'LEFT GROUP'}, status=200)
        elif command == "remove_user":
            try:
                if me not in group.admins.all():
                    return JsonResponse({'status': 'ACCESS DENIED2'}, status=405)
                user = MyUser.objects.get(username=data['user_username'])
                if user == me:
                    return JsonResponse({'status': 'Cannot remove self'}, status=403)
                if user == group.owner:
                    return JsonResponse({'status': 'Cannot remove owner'}, status=403)
                if me == group.owner:
                    if user in group.admins:
                        group.admins.remove(user)
                else:
                    if user in group.admins:
                        return JsonResponse({'status': 'Cannot remove admin'}, status=406)
                group.users.remove(user)
                group.save()
            except:
                return JsonResponse({'status': 'Error'}, status=500)


# U should also have a request handler for deleting the admins and users.
class GroupPictureView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def put(self, request):
        data = json.loads(request.data["data"])
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
        try:
            gr = Group.objects.get(id=data["group_id"])
            if me not in gr.admins:
                return JsonResponse({"status": "ACCESS DENIED"}, status=405)
            try:
                f = request.FILES["file"]
            except:
                return JsonResponse({"status": "ERROR FILE"}, status=500)
            if f.size > (6 * (1024 * 1024)):
                return JsonResponse({'status': 'File Size more than 6 MB'}, status=405)
            try:
                img = Image.open(f)
                img.verify()
                gr.group_img.save(f.name, f, save=True)
                gr.save()  # Here if error
                return JsonResponse({'status': 'SUCCESS UPLOAD'}, status = 200)
            except:
                return JsonResponse({"status": "Unsupported image type"}, status=400)
        except Group.DoesNotExist:
            return JsonResponse({"status": "GROUP NOT EXISTS"}, status=400)

    def get(self, request, group_id=None):
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=403)
        if group_id:
            try:
                gr = Group.objects.get(id=group_id)
                serializer = GroupPictureSerializer(gr, many=False, context={'request': request})
                serializer.data['group_img'] = get_download_link_from_file(serializer.data['group_img'])
                return JsonResponse(serializer.data, status=200)
            except Group.DoesNotExist:
                return JsonResponse({'status': 'USER NOT EXISTS'}, status = 404)
        else:
            return JsonResponse({'status': 'NO GROUP SPECIFIED'}, status = 404)

# TESTED