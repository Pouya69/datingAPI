from rest_framework.test import APITestCase

from myapp.models import Date
from .models import MyUser, VerifyLink
from rest_framework.authtoken.models import Token


class User1Test(APITestCase):
    def setUp(self):  # Register and Login before each test
        self.url = 'http://127.0.0.1:8000'

        data = {
            "email": "pooyasalehi69@gmail.com",
            "username": "pouyad_ai",
            "password": "Pooya1274406641@",
            "age": 17,
            "gender": "male"
        }
        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            "username": "catfish_2",
            "email": "pouya.psalehi@gmail.com",
            "password": "Pooya1274406641@",
            "age": 18,
            "gender": "female"
        }

        response = self.client.post(path=f"{self.url}/api/register", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="pouyad_ai")).token
        response = self.client.get(path=link, format='json')
        self.assertEqual(response.status_code, 200)

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="catfish_2")).token
        response = self.client.get(path=link, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            "username": "pouyad_ai",
            "password": "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        # print(json_response)
        token = json_response['token']
        self.assertNotEqual(token, "")
        self.token_1 = token
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")

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

    def test_profile_me_data(self):  # TODO (about, username, email)
        response = self.client.get(path=f"{self.url}/api/profile", format='json')
        json_response = response.json()
        print(f"profile me: {json_response}")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual({}, json_response)

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
        # print(json_response)
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
        response = self.client.get(path=f"{self.url}/api/friends", format='json')
        json_response = response.json()
        print(f"friends get: {json_response}")
        self.assertEqual(response.status_code, 200)

        data = {
            'user_username': 'catfish_2'
        }
        response = self.client.put(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 200)  # Then send notification to add friend back

        response = self.client.get(path=f"{self.url}/api/friends", format='json')
        json_response = response.json()
        print(f"friends get 2: {json_response}")
        self.assertEqual(response.status_code, 200)

        # Delete without dating
        response = self.client.delete(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        # Delete with dating  TODO
        response = self.client.put(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 200)  # Then send notification to add friend back
        data = {
            'with': "catfish_2",
            'type': "hidden"  # Crush
        }
        response = self.client.post(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'with': "pouyad_ai",
            'decision': "OK"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_2}")  # Go to other user
        response = self.client.put(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'user_username': 'catfish_2',
            'delete_date': 'OK'  # If user wants to delete the date while removing friend else nothing
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")  # Go to other user
        response = self.client.delete(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="catfish_2")
        self.assertEqual(Date.objects.all().count(), 0)
        self.assertEqual(user_1.dating_with, None)
        self.assertEqual(user_2.dating_with, None)





        response = self.client.put(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 200)  # Then send notification to add friend back
        data = {
            'with': "catfish_2",
            'type': "hidden"  # Crush
        }
        response = self.client.post(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'with': "pouyad_ai",
            'decision': "OK"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_2}")  # Go to other user
        response = self.client.put(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 200)

        data = {
            'user_username': 'catfish_2',
            'delete_date': ""  # If user wants to delete the date while removing friend else nothing
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_1}")  # Go to other user
        response = self.client.delete(path=f"{self.url}/api/friends", data=data, format='json')
        self.assertEqual(response.status_code, 201)

        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="catfish_2")
        self.assertNotEqual(Date.objects.all().count(), 0)
        self.assertNotEqual(user_1.dating_with, None)
        self.assertNotEqual(user_2.dating_with, None)
        self.assertEqual(Date.objects.filter(users__in=[user_1]).get(users__in=[user_1]).female, True)
        self.assertEqual(Date.objects.filter(users__in=[user_1]).get(users__in=[user_1]).male, True)

        data = {
            'with': "catfish_2",
        }
        response = self.client.delete(path=f"{self.url}/api/date", data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Date.objects.all().count(), 0)
        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="catfish_2")
        self.assertEqual(user_1.dating_with, None)
        self.assertEqual(user_2.dating_with, None)


    def test_dating(self):
        user_1 = MyUser.objects.get(username="pouyad_ai")
        user_2 = MyUser.objects.get(username="catfish_2")
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
        pass
