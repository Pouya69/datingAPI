from django.test import TestCase

from userManagement.models import MyUser, VerifyLink
from .models import Group


class GroupTest(TestCase):
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
            "email": "test@gmail.com",
            "username": "pouyad_ai2",
            "password": "Pooya1274406641@",
            "age": 25,
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

        link = self.url + '/activate/' + VerifyLink.objects.get(user=MyUser.objects.get(username="pouyad_ai2")).token
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

        data = {
            "username": "pouyad_ai2",
            "password": "Pooya1274406641@"
        }
        response = self.client.post(path=f"{self.url}/api/login", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        token = json_response['token']
        self.assertNotEqual(token, "")
        self.token_1 = token
        self.client.credentials(HTTP_AUTHORIZATION=f"token {self.token_3}")

    def test_join_chat(self):
        pass

