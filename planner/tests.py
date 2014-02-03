# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

class EventFormTestCase(TestCase):
    fixtures = ['initial_data.json']
    
    def setUp(self):
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client = Client(enforce_csrf_checks=True)
        
        self.client.login(username='temporary', password='temporary')
        self.client.get('/planner/event/Gudstjänst/form/')
        self.csrf_token = self.client.cookies['csrftoken'].value
        

    def test_get(self):
        
        resp = self.client.get('/planner/event/Gudstjänst/form/')
        self.assertEqual(resp.status_code, 200)

        
    def test_post(self):
        resp = self.client.post('/planner/event/Gudstjänst/form/', {'csrfmiddlewaretoken': self.csrf_token, 'title': 'test', 'start_date': "2014-01-30", "start_time": "11:00"})
        self.assertEqual(resp.status_code, 200)