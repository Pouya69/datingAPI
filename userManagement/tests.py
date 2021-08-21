import json

from rest_framework.test import APITestCase

from myapp.models import Date
from .models import MyUser, VerifyLink


class User1Test(APITestCase):
    def setUp(self):  # Register and Login before each test
        self.url = 'http://127.0.0.1:8000'

        data = {
            "email": "pooyasalehi69@gmail.com",
            "username": "fuckyou",
            "password": "Pooya1274406641@",
            "date_of_birth": "2000-01-05",
            'full_name': "Meow Meow2",
            "gender": "male"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 410)

        data = {
            "email": "pooyasalehi69@gmail.com",
            "username": "good_cat2",
            "password": "Pooya1274406641@",
            "date_of_birth": "2000-01-05",
            'full_name': "Fuck",
            "gender": "male"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 410)

        data = {
            "email": "pooyasalehi69@gmail.com",
            "username": "pouyad_ai",
            "password": "Pooya1274406641@",
            "date_of_birth": "2000-01-05",
            'full_name': "Meow Meow2",
            "gender": "male"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            "email": "test@gmail.com",
            "username": "pouyad_ai2",
            "password": "Pooya1274406641@",
            "date_of_birth": "1993-01-05",
            'full_name': "Meow Meow",
            "gender": "male"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            "username": "catfish_2",
            "email": "pouya.psalehi@gmail.com",
            "password": "Pooya1274406641@",
            "date_of_birth": "1996-01-05",
            "gender": "female",
            'full_name': "Pouya Salehi"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            "username": "catfish_22",
            "email": "pouya.psalehi2@gmail.com",
            "password": "Pooya1274406641@",
            "date_of_birth": "2006-01-05",
            "gender": "female",
            'full_name': "Pouya Salehi"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'username': "pouyacat34",
            "date_of_birth": "2001-01-05",
            "gender": "female",
            'full_name': "Pouya Salehi2",
            # Each time get a token from google auth api https://developers.google.com/oauthplayground/  with value : https://www.googleapis.com/auth/userinfo.email
            'token': "ya29.a0ARrdaM_2hbEL6bznRbsJkBFyzcsu6xRniUazz8iHm0eBgdksGng6OgdooVd-VHL3sCwk9t4Q0n5rF4sFczuB_7C1M1Xh5dCHlFclRRJ3popNpTdyYEEIMb3ycfdvlaL1kbsGSVTctzk-6FyJXACA178L_ScK"
        }
        response = self.client.post(path=f"{self.url}/api/google", data=data, format='json')
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.token_4 = json_response['access_token']
        # Bearer <Token>

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="pouyad_ai")).token
        response = self.client.get(path=link, format='json')
        self.assertEqual(response.status_code, 200)

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="catfish_22")).token
        response = self.client.get(path=link, format='json')
        self.assertEqual(response.status_code, 200)

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="catfish_2")).token
        response = self.client.get(path=link, format='json')
        self.assertEqual(response.status_code, 200)

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="pouyad_ai2")).token
        response = self.client.get(path=link, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            "username": "pouyad_ai",
            "password": "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        token = json_response['token']
        print(json_response['user'])
        self.assertNotEqual(token, "")
        self.token_1 = token

        data = {
            "email": "pouya.psalehi@gmail.com",
            "password": "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        token = json_response['token']
        self.assertNotEqual(token, "")
        self.token_2 = token

        data = {
            "email": "test@gmail.com",
            "password": "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        token = json_response['token']
        self.assertNotEqual(token, "")
        self.token_3 = token

        data = {
            "username": "catfish_22",
            "password": "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        token = json_response['token']
        self.assertNotEqual(token, "")
        self.token_5 = token

        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")

        # self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_4}")  # For google is Bearer

    def test_forgot_password(self):
        response = self.client.get(path=f"{self.url}/api/forgotPassword", format='json')
        self.assertEqual(response.status_code, 200)

        verify_token = VerifyLink.objects.get(user=MyUser.objects.get(username="pouyad_ai"), verify_type="passwordForgot").token
        data = {
            "verify_token": verify_token,
            "new_password": "Pooya12345"
        }
        response = self.client.get(path=f"{self.url}/activate/{verify_token}", format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(path=f"{self.url}/api/forgotPassword", data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_feeling(self):
        response = self.client.get(path=f"{self.url}/api/feeling", format='json')
        json_response = response.json()
        print(json_response)
        self.assertEqual("nothing", json_response['feeling'])
        data = {
            'feeling': 'happy'
        }
        response = self.client.put(path=f"{self.url}/api/feeling", data=data, format='json')
        json_response = response.json()
        self.assertEqual("happy", json_response['feeling'])

        response = self.client.get(path=f"{self.url}/api/feeling", format='json')
        json_response = response.json()
        self.assertEqual("happy", json_response['feeling'])

    def test_profile_me_data(self):
        response = self.client.get(path=f"{self.url}/api/profile", format='json')
        json_response = response.json()
        print(f"profile me: {json_response}")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual({}, json_response)

    def test_change_profile_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_2}")
        data = {
            'username': "pouyad_ai8",
            'email': "pouya.psalehi@gmail.com",
            "country": "Canada",
            'about': "I just changed my bio",
            'private': 'true',
            'date_of_birth': "2007-01-01",
            'full_name': "Gta Meow"
        }
        response = self.client.put(path=f"{self.url}/api/profile", data=data, format='json')
        json_response = response.json()
        print(f"profile me: {json_response}")
        self.assertEqual(response.status_code, 200)

        data = {
            'username': "pouyad_ai8",
            'email': "pouya.psalehi@gmail.com",
            'about': "I just changed my bio",
            "country": "Canada",
            'private': 'true',
            'date_of_birth': "2001-01-01",
            'full_name': "Gta Cat"
        }
        response = self.client.put(path=f"{self.url}/api/profile", data=data, format='json')
        json_response = response.json()
        self.assertEqual(response.status_code, 200)

        data = {
            'username': "pouyad_ai8",
            'email': "pouya.psalehi@gmail.com",
            'about': "I just changed my bio",
            "country": "Canada",
            'private': 'true',
            'date_of_birth': "2003-01-01",
            'full_name': "Pouya Salehi"
        }
        response = self.client.put(path=f"{self.url}/api/profile", data=data, format='json')
        json_response = response.json()
        print(f"Profile Update Good: {json_response}")
        self.assertEqual(response.status_code, 200)

    def test_block_user(self):
        data = {
            'user_username': "catfish_2"
        }

        response = self.client.post(path=f"{self.url}/api/block", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        response = self.client.get(path=f"{self.url}/api/block", format='json')
        json_response = response.json()
        self.assertEqual(json_response['block_list'], [{'username': "catfish_2"}])

        response = self.client.delete(path=f"{self.url}/api/block", data=data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_interests(self):
        data = {
            'interests': ["piano", "gta", "cat"]
        }
        response = self.client.get(path=f"{self.url}/api/interests", format='json')
        json_response = response.json()
        self.assertEqual({'interests': []}, json_response)

        response = self.client.put(path=f"{self.url}/api/interests", data=data, format='json')
        json_response = response.json()
        self.assertEqual(data, json_response)

        response = self.client.put(path=f"{self.url}/api/interests", data={}, format='json')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f"{self.url}/api/interests", format='json')
        json_response = response.json()
        self.assertEqual({'interests': ["piano", "gta", "cat"]}, json_response)

    def test_profile_picture(self):
        response = self.client.get(path=f"{self.url}/api/profilePic")
        json_response = response.json()
        self.assertNotEqual(json_response['profile_pic'], "")
        with open('userManagement/image_test.jpg', 'rb') as image:
            response = self.client.put(path=f"{self.url}/api/profilePic", data={'file': image})
            self.assertEqual(response.status_code, 200)
        with open('userManagement/image_test.jpg', 'rb') as image:
            response = self.client.put(path=f"{self.url}/api/profilePic", data={'file': image})
            self.assertEqual(response.status_code, 200)
        with open('userManagement/image_test.jpg', 'rb') as image:
            response = self.client.put(path=f"{self.url}/api/profilePic", data={'file': image})
            self.assertEqual(response.status_code, 200)
        response = self.client.get(path=f"{self.url}/api/profilePic")
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertNotEqual(json_response['profile_pic'], "http://testserver/media/defaults/no-img.jpeg")
        print(f"profile pic : {json_response['profile_pic']}")  # Print the image download link

    def test_change_password(self):
        data = {
            'prev_password': "Pooya1274406641@",
            'new_password': "Catfish111"
        }
        response = self.client.post(path=f"{self.url}/api/profile", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(path=f"{self.url}/api/logout", format='json')
        self.assertEqual(response.status_code, 200)
        self.client.credentials()

        data = {
            "username": "pouyad_ai",
            "password": "Catfish111"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        token = json_response['token']
        self.assertNotEqual(token, "")
        self.token_1 = token
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")

        data = {
            'prev_password': "Catfish111",
            'new_password': "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/profile", data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_friends(self):
        response = self.client.get(path=f"{self.url}/api/friends/get_friends", format='json')
        json_response = response.json()
        print(f"friends get: {json_response}")
        self.assertEqual(response.status_code, 200)

        data = {
            'user_username': "pouyacat34"
        }
        response = self.client.put(path=f"{self.url}/api/friends", data=data, format='json')
        json_response = response.json()
        self.assertEqual(response.status_code, 200)  # Then send notification to add friend back

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_4}")  # Go to other user
        response = self.client.get(path=f"{self.url}/api/friends/friend_requests", format='json')
        json_response = response.json()
        print(f"friends get 2: {json_response}")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json_response, {})

        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")  # Go to other user

        # Delete without dating
        response = self.client.delete(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        # Delete with dating  TODO
        response = self.client.put(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 200)  # Then send notification to add friend back
        data = {
            'with': "pouyacat34",
            'type': "hidden"  # Crush
        }
        response = self.client.post(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'with': "pouyad_ai",
            'decision': "OK"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_4}")  # Go to other user
        response = self.client.put(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'user_username': 'pouyacat34',
            'delete_date': 'OK'  # If user wants to delete the date while removing friend else nothing
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")  # Go to other user
        response = self.client.delete(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="pouyacat34")
        self.assertEqual(Date.objects.all().count(), 0)
        self.assertEqual(user_1.dating_with, None)
        self.assertEqual(user_2.dating_with, None)





        response = self.client.put(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 200)  # Then send notification to add friend back
        data = {
            'with': "pouyacat34",
            'type': "hidden"  # Crush
        }
        response = self.client.post(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'with': "pouyad_ai",
            'decision': "OK"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_4}")  # Go to other user
        response = self.client.put(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'user_username': 'pouyacat34',
            'delete_date': ""  # If user wants to delete the date while removing friend else nothing
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")  # Go to other user
        response = self.client.delete(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="pouyacat34")
        self.assertNotEqual(Date.objects.all().count(), 0)
        self.assertNotEqual(user_1.dating_with, None)
        self.assertNotEqual(user_2.dating_with, None)
        self.assertEqual(Date.objects.filter(users__in=[user_1]).get(users__in=[user_1]).female, True)
        self.assertEqual(Date.objects.filter(users__in=[user_1]).get(users__in=[user_1]).male, True)

        data = {
            'with': "pouyacat34",
        }
        response = self.client.delete(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Date.objects.all().count(), 0)
        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="pouyacat34")
        self.assertEqual(user_1.dating_with, None)
        self.assertEqual(user_2.dating_with, None)

    def test_refresh_token(self):
        data = {
            'password': "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/refreshToken", data=data, format='json')
        self.assertEqual(response.status_code, 201)
        json_response = response.json()
        self.assertNotEqual(json_response['token'], self.token_1)
        self.token_1 = json_response['token']

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_4}")  # Go to other user
        response = self.client.post(path=f"{self.url}/api/refreshToken", format='json')
        json_response = response.json()
        print(json_response)
        self.assertEqual(response.status_code, 201)

        self.assertNotEqual(json_response['access_token'], self.token_4)
        self.token_4 = json_response['access_token']

    def test_dating(self):
        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="pouyacat34")
        self.assertEqual(user_1.dating_with, None)
        self.assertEqual(user_2.dating_with, None)

        data = {
            'with': "catfish_2",
            'type': "hidden"  # Crush
        }
        response = self.client.post(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Date.objects.all().count(), 1)

        data = {
            'with': "pouyad_ai",
            'decision': "OK"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_2}")  # Go to other user
        response = self.client.put(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_1.dating_with, user_2.dating_with)
        self.assertEqual(Date.objects.filter(users__in=[user_1]).get(users__in=[user_1]).female, True)
        self.assertEqual(Date.objects.filter(users__in=[user_1]).get(users__in=[user_1]).male, True)

        response = self.client.delete(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(user_1.dating_with, None)
        self.assertEqual(user_2.dating_with, None)
        self.assertEqual(Date.objects.all().count(), 0)

    def test_find_users(self):  # TODO
        data = {
            'interests': ["piano", "gta", "cat"]
        }
        response = self.client.put(path=f"{self.url}/api/interests", data=data, format='json')
        json_response = response.json()
        self.assertEqual(data, json_response)
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_2}")  # Go to other user
        data = {
            'interests': ["piano", "dog", "another"]  # One interests is same
        }
        response = self.client.put(path=f"{self.url}/api/interests", data=data, format='json')
        json_response = response.json()
        self.assertEqual(data, json_response)

    def test_stories(self):  # TODO
        response = self.client.get(path=f"{self.url}/api/story")
        json_response = response.json()
        self.assertEqual(json_response, {'stories': {}})

        with open('userManagement/image_test.jpg', 'rb') as image:
            dd = json.dumps({
                'story_type': "image"
            })
            data = {
                'file': image,
                'data': dd
            }
            response = self.client.post(path=f"{self.url}/api/story", data=data)
            json_response = response.json()
            self.assertEqual(response.status_code, 200)

        with open('userManagement/testvideo.mp4', 'rb') as video:
            dd = json.dumps({
                'story_type': "video"
            })
            data = {
                'file': video,
                'data': dd
            }
            response = self.client.post(path=f"{self.url}/api/story", data=data)
            json_response = response.json()
            self.assertEqual(response.status_code, 200)
        with open('userManagement/test2.mp4', 'rb') as video2:  # TODO
            dd = json.dumps({
                'story_type': "video"
            })
            data = {
                'file': video2,
                'data': dd
            }
            response = self.client.post(path=f"{self.url}/api/story", data=data)
            json_response = response.json()
            self.assertEqual(response.status_code, 408)
        response = self.client.get(path=f"{self.url}/api/story")
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        print(f"Stories new : {json_response}")  # Print the image download link
