# chat/views.py
import os
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from datingAPI.appProcessing import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication
from PIL import Image
from rest_framework.parsers import FileUploadParser, MultiPartParser
from .models import Message, Group, Date                                         # Our Message model
from .serializers import GroupPictureSerializer, MessageSerializer, DateSerializer, GroupSerializer # Our Serializer Classes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# headers = {'Authorization': 'Token 9054f7aa9305e012b3c2300408c3dfdf390fcddf'}


# To get data from headers : request.META["HTTP_AUTHORIZATION"]

def index(request):
    return render(request, 'roompick.html')


def room(request, chat_id=None):
    if chat_id:
        try:
            Group.objects.get(id=int(chat_id))
            # Later on we'll use json not html.
            return render(request, 'room.html', {
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
            if file.size > (10 * (1024 * 1024)):
                return JsonResponse({'status': 'File Size more than 10 MB'}, status=403)
            msg = Message.objects.get(id=int(data['message_id']))
            msg.file_url.save(file.name, file, save=True)
            msg.save()  # Here if error
        except:
            return JsonResponse({'status': 'File Error'}, status=500)


def join_chat(request, chat_id=None):
    # We'll make the invite link from the client-side
    if chat_id:
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid Token'}, status=404)
        try:
            group = Group.objects.get(id=int(chat_id))
        except:
            return JsonResponse({'status': 'Invalid Group'}, status=404)
        if group not in me.chat_list.all():
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
            return JsonResponse({'status': 'Invalid token'}, status=404)
        if chat_id:
            try:
                group = Group.objects.get(id_chat=chat_id)
            except Group.DoesNotExist:
                return JsonResponse({'status': 'Invalid chat_id'}, status=404)
            final_data = GroupSerializer(group, many=False, context={'request': request}).data
            # Edit last message etc.
            return JsonResponse(final_data, safe=False)
        groups = me.chat_list.all()
        final_data = GroupSerializer(groups, many=True, context={'request': request}).data
        final_data['last_message'] = str_to_dict(final_data['last_message'])
        # Edit last message etc.
        return JsonResponse(final_data)

    def post(self, request):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
        try:
            data_users = data['users']
            group = Group(owner=me)
            group.save()
            for u_username in data_users:
                try:
                    user = MyUser.objects.get(username=u_username)
                    print(user)
                    group.users.add(user)
                except MyUser.DoesNotExist:
                    group.delete()
                    return JsonResponse({"status": "User not exists GROUP POST"}, status=404)
        except:
            return JsonResponse({"status": "Error in user lists"}, status=500)
        group.save()
        # print(group.owner)
        group.admins.add(me)
        group.users.add(me)
        for u in group.users.all():
            u.chat_list.add(group)
        serializer = GroupSerializer(group, many=False, context={'request': request})
        return JsonResponse(serializer.data, status=200)
        # TESTED

    def put(self, request, chat_id=None):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if not chat_id:
            return JsonResponse({'status': 'Invalid chat_id'}, status=404)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
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
                users_add = data["add_users"]
                for add_username in users_add:
                    try:
                        user_user = MyUser.objects.get(username=add_username)
                        if not user_user not in users:
                            group.users.add(user_user)
                    except MyUser.DoesNotExist:
                        # return JsonResponse({'status': 'Users not valid'}, status=404)
                        pass
            except:
                pass
        elif command == "leave_group":
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
        elif me not in admins:
            return JsonResponse({'status': 'NOT ADMIN'}, status=403)
        if command == "new_chat_id":
            try:
                new_id = data["new_id_chat"]
                if not new_id == "" and new_id is not None:
                    group.id_chat = new_id
            except KeyError:
                pass
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
                pass
        elif command == "new_admins":
            try:
                new_admins = data["new_admins"]
                for admin_username in new_admins:
                    try:
                        user_admin = MyUser.objects.get(username=admin_username)
                        if user_admin not in admins:
                            group.admins.add(user_admin)
                    except MyUser.DoesNotExist:
                        group.save()
                        return JsonResponse({'status': 'Admins not valid'}, status=404)
            except KeyError:
                pass
        group.save()
        return JsonResponse("UPDATED", status=200)

    def delete(self, request, chat_id=None):
        data = JSONParser().parse(request)
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({'status': 'Invalid token'}, status=404)
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
                    return JsonResponse({'status': 'Cannot remove admin'}, status=403)
                group.users.remove(user)
                if user in group.admins:
                    group.admins.remove(user)
                group.save()
            except:
                return JsonResponse({'status': 'Error'}, status=406)


# U should also have a request handler for deleting the admins and users.
class GroupPictureView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def put(self, request):
        data = json.loads(request.data["data"])
        me = get_user_by_token(request.META)
        if me is None:
            return JsonResponse({"status": "Invalid Token"}, status=404)
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
        if group_id:
            try:
                gr = Group.objects.get(id=group_id)
                serializer = GroupPictureSerializer(gr, many=False, context={'request': request})
                return JsonResponse(serializer.data, safe=False, status = 200)
            except Group.DoesNotExist:
                return JsonResponse({'status': 'USER NOT EXISTS'}, status = 404)
        else:
            return JsonResponse({'status': 'NO GROUP SPECIFIED'}, status = 404)

# TESTED