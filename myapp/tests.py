from django.test import TestCase
from .models import Group


class GroupTest(TestCase):
    def set_up(self):
        self.client_1 = self.client
        self.client_2 = self.client
        self.client_3 = self.client
        self.client_4 = self.client


        self.group_1 = Group.objects.create()