# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from open_facebook.api import OpenFacebook
from django.contrib.auth.models import User
import datetime
from django.core.signing import Signer
from django.core.mail import send_mail
from jquery_fields.fields import ModelMultipleChoiceTokenInputField

class ManyToManyField(models.ManyToManyField):

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': ModelMultipleChoiceTokenInputField, "configuration": {}, "queryset": User.objects.all(), "json_source":'http://shell.loopj.com/tokeninput/tvshows.php'}
        defaults.update(kwargs)
        print defaults
        return super(ManyToManyField, self).formfield(**defaults)
    
class ForeignKey(models.ManyToManyField):

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {'form_class': ModelMultipleChoiceTokenInputField, "configuration": {'tokenLimit': 1}, "queryset": User.objects.all(), "json_source":'/planner/users/'}
        defaults.update(kwargs)
        print defaults
        return super(ForeignKey, self).formfield(**defaults)    
    
# Create your models here.
valid_events = ["Vardag", "Service"]
page_id = 185831898118166
sender = "daniel.karlsson@roseniuskyrkan.se"
signature = u"""
Med Vänliga Hälsningar
Daniel Karlsson

PS. Detta mailet skickades ut automatiskt men det går jättebra att svara på det. Ditt mail kommer då till min vanliga adress. DS."""

def generate_login_link(pk):
    user = User.objects.get(pk=pk)
    signer = Signer()
    value = signer.sign(user.username)
    return settings.SITE_ROOT + "/account/initialize/?user=" + str(user.pk) + "&hash=" + value.split(":")[1]

class Occurrence(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null = True)
    
    def __unicode__(self):
        return unicode(self.start_time.strftime("%d %b %H:%M"), "utf-8")
        
    
class Event(models.Model):
    
    event = models.ForeignKey(Occurrence, null = True, verbose_name="Tidpunkt")
    title = models.CharField(max_length=100, verbose_name="Titel")
    description = models.CharField(blank = True, null = True, max_length=1000, verbose_name="Beskrivning")
    facebook_publish = models.BooleanField(default = False, verbose_name="Facebook")
    publish_date = models.DateField(blank = True, null = True, verbose_name="Publiceringsdatum")
    internal_notes = models.CharField(blank = True, null = True, max_length=1000, verbose_name="Anteckningar")
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return self.title
    
    def publish(self):
        #token = Token.objects.all()[:1].get().token
        #fb = OpenFacebook(token)
        #fb.set(str(page_id) + "/events", no_feed_story = "true", name=self.title, description = self.description, start_time = self.event.start_time.isoformat(), location_id=page_id)
        print "publish"
        
    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        if self.facebook_publish and (self.publish_date == None or self.publish_date <= datetime.date.today()):
            self.publish()        
            
    def delete(self, *args, **kwargs):
        self.event.delete()
        super(Event, self).save(*args, **kwargs)

class Vardag(Event):
    organiser = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="organiserVardag")
    speaker = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="speakerVardag")
    food = models.ManyToManyField(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="food")
    
    class Meta:
        verbose_name = "VARDag"
        
class Service(Event):
    organiser = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="organiserService", verbose_name="Ansvarig")
    speaker = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="speakerService", verbose_name = "Talare")
    meeting_leader = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="meeting_leader", verbose_name = u"Mötesledare")
    host = ManyToManyField(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="host", verbose_name = u"Kyrkvärdar")
    music = ManyToManyField(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="music", verbose_name = u"Musiker/Lovsång")
    organ = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="organ", verbose_name = "Organist")
    bible_reader = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="bible_reader", verbose_name = u"Bibelläsare")
    personal_prayer = ManyToManyField(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="personal_prayer", verbose_name = u"Personlig förbön")
    prayer = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="prayer", verbose_name = u"Kyrkans förbön")
    technician = ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, related_name="technician", verbose_name = "Teknik")
    
    class Meta:
        verbose_name = "Gudtjänst"
        
    def send_reminder(self):
        rlist = [self.organiser.email]
        message = u"""
Hej Vänner,

Här kommer en påminnelse om att du har en uppgift på söndagens gudtjänst enligt följande:
    
"""
        for field in ["speaker", "meeting_leader", "organ", "bible_reader", "prayer"]:
            user = eval("self.%s" % field)
            if user:
                rlist.append(user.email)
                message +=  self._meta.get_field(field).verbose_name + ": " + user.first_name + " " + user.last_name + "\n"

        for field in ['host', 'music', 'personal_prayer']:
            users = eval("self.%s.all()" % field)
            
            for user in users:
                rlist.append(user.email)
                message +=  self._meta.get_field(field).verbose_name + ": " + user.first_name + " " + user.last_name + "\n"

        send_mail(
            subject = "Gudtjänst " + self.event.start_time.date().strftime("%Y-%m-%d"),
            from_email = sender,
            recipient_list = set(rlist),
            message = message+signature,
            )
        
    @classmethod
    def search(cls, query):
        return User.objects.all()
    
class Token(models.Model):
    token = models.CharField(max_length = 250)
    creation_date = models.DateField(auto_now_add=True)