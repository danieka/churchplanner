# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User
from django.test import Client
import datetime
from planner.models import *
from planner.tasks import *
import pytz

tz = pytz.timezone("Europe/Stockholm")

def event(date):
    e = Event.objects.create(title="TestEvent", event_type=EventType.objects.get(name="Gudstjänst"))
    e.event =  Occurrence.objects.create(start_time = tz.localize(date))
    Participation.objects.create(user = User.objects.get(pk=2), event = e, attending = "true", role = Role.objects.get(name = "Mötesledare"))
    Participation.objects.create(user = User.objects.get(pk=3), event = e, attending = "null", role = Role.objects.get(name = "Textläsare"))
    e.save()

class TestCreateEvent(TestCase):
    fixtures = ["fixture1.json"]
    def setUp(self):
        event(datetime.datetime.now())

    def testEvent(self):
        e = Event.objects.get(title="TestEvent") 
        self.assertIsNotNone(e)
        self.assertEqual(e.event_type.name, "Gudstjänst")
        self.assertIsNotNone(e.event)

    def testParticipation(self):
        e = Event.objects.get(title="TestEvent")
        self.assertEqual(len(e.participants.all()), 2)
        self.assertEqual(e.participants.all()[0], User.objects.get(username = "Test.1"))

class TestReminderEmail(TestCase):
    fixtures = ["fixture1.json"]
    def setUp(self):
        event(datetime.datetime.now() + datetime.timedelta(days=2))

    def testSend(self):
        e = Event.objects.get(title="TestEvent")
        send_email_task()

        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(len(m.to), 2)
        self.assertTrue(User.objects.get(username = "Test.1").email in m.to)
        self.assertTrue(User.objects.get(pk = 1).email in m.to)
        self.assertEqual(m.subject, e.event_type.name + " " + e.event.start_time.strftime("%Y-%m-%d"))

    def testDuplicate(self):
        send_email_task()
        send_email_task()

        self.assertEqual(len(mail.outbox), 1)

class TestParticipationEmail(TestCase):
    fixtures = ["fixture1.json"]

    def setUp(self):
        event(datetime.datetime.now() + datetime.timedelta(days=2))

    def testSend(self):
        e = Event.objects.get(title="TestEvent")
        send_email_participation()

        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(len(m.to), 1)
        self.assertTrue(User.objects.get(username = "Test.2").email in m.to)
        self.assertEqual(m.subject, "Kan du hjälpa till?")

    def testDuplicate(self):
        send_email_participation()
        send_email_participation()

        self.assertEqual(len(mail.outbox), 1)