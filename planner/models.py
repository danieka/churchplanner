# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from open_facebook.api import OpenFacebook
from django.contrib.auth.models import User
import datetime
from django.core.signing import Signer
from django.core.mail import send_mail
from jquery_fields.fields import ModelMultipleChoiceTokenInputField
from south.modelsinspector import add_introspection_rules  

from django.core.files import File  
import pdb
from django.db.models.signals import post_save
from django.dispatch import receiver

try:
    #from wand.image import Image
    wand_imported = False
except:
    wand_imported = False

# Create your models here.
page_id = 185831898118166 #Rossenspage id
sender = "daniel.karlsson@roseniuskyrkan.se"
signature = u"""
Med Vänliga Hälsningar
Daniel Karlsson

PS. Detta mailet skickades ut automatiskt med ett nytt system som vi håller på att pröva. 
Det går jättebra att svara som vanligt och ditt mail kommer då till min vanliga adress. DS."""

message = u"""
Hej Vänner,

Här kommer en påminnelse om att du har en uppgift på %s enligt följande:
    
"""
login = u"""
Hej %s,

Här kommer inloggningsuppgifter till Roseniuskyrkans planeringsverktyg.
Vi använder planeringsverktyget för att planera in gudstjänster och andra evenemang och 
vilka som ska medverka vid dessa evenemang. Genom att logga in så kan du se vilka evenemang
som du är inplanerad på.

För skapa inloggningsuppgifter så kan du klicka på länken nedan eller kopiera adressen till
din webbläsares adressfönster. När du klickat kommer du få välja hur du vill logga in.

Om du inte vet varför du detta mail så kan du svara direkt på detta mailet så reder vi ut det.

Länken till planeringsverktyget:
%s
"""

def generate_user_hash(pk):
    user = User.objects.get(pk=pk)
    signer = Signer()
    value = signer.sign(user.username)
    return value.split(":")[1]

class Occurrence(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null = True)
    
    def __unicode__(self):
        return unicode(self.start_time.strftime("%d %b %H:%M"), "utf-8")

class Role(models.Model):
    name = models.CharField(max_length = 30, unique = True)
    
    def __unicode__(self):
        return self.name
        
class EventType(models.Model):
    name = models.CharField(max_length=50, unique = True)
    roles = models.ManyToManyField(Role)
    initial_description = models.TextField(max_length = 4000)
    image = models.ImageField(upload_to="images", null=True, blank = True)
    
    def __unicode__(self):
        return self.name
   
class Document(models.Model):
    name = models.CharField(max_length=50, blank = True, null = True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL)
    file_field = models.FileField(upload_to="files", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="files", null=True, blank=True)
    
    def __unicode__(self):
        return self.file_field.name
    

@receiver(post_save, sender=Document)
def generate_thumbnail(sender, **kwargs):
    if not wand_imported:
        return
    """This is called everytime a Document is saved and if the document doesn't have a thumbnail one is created."""
    instance = kwargs['instance']
    if instance.thumbnail == None:
            with Image(filename = instance.file_field.path +"[0]") as img:
                img.alpha_channel=False
                with img.convert('jpeg') as converted:                    
                    converted.resize(170, 150)
                    converted.save(filename="tmp.jpg")
                    instance.thumbnail.save(settings.MEDIA_URL + "files/thumbnails/" + instance.file_field.name.split(".")[-2] + ".jpg", File(open("tmp.jpg")))
    
       
   
class Event(models.Model):
    event = models.ForeignKey(Occurrence, null = True, verbose_name="Tidpunkt", on_delete=models.SET_NULL)
    title = models.CharField(max_length=100, verbose_name="Titel")
    description = models.CharField(blank = True, null = True, max_length=4000, verbose_name="Beskrivning")
    facebook_publish = models.BooleanField(default = False, verbose_name="Facebook")
    publish_date = models.DateField(blank = True, null = True, verbose_name="Publiceringsdatum")
    internal_notes = models.CharField(blank = True, null = True, max_length=4000, verbose_name="Anteckningar")
    published = models.BooleanField(default = False)
    email_sent = models.BooleanField(default = False)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through = "Participation")
    event_type = models.ForeignKey(EventType)
    documents = models.ManyToManyField(Document, blank = True, null= True)
        
    def __unicode__(self):
        return self.title
    
    def publish(self):
        if not settings.DEBUG:
            token = Token.objects.all()[:1].get().token
            fb = OpenFacebook(token)
            print fb.set(str(page_id) + "/events", no_feed_story = "true", name=self.title, description = self.description, start_time = self.event.start_time.isoformat(), location_id=page_id, picture = "584610018240350")
            self.published = True    
            
    def delete(self, *args, **kwargs):
        self.event.delete()
        super(Event, self).delete(*args, **kwargs)
       
    def send_mail(self):
        rlist = [sender]
        roles = {}
        msg = message % (self.event_type.name)
        
        for participant in self.participants.all():
            rlist.append(participant.email)
            for participation in Participation.objects.filter(user= participant, event = self):
                try:
                    roles[participation.role.name] += participant.first_name + " " +participant.last_name +", "
                except KeyError:
                    roles[participation.role.name] = participant.first_name + " " +participant.last_name +", "
           
        for k in roles.keys():
            msg += k +": " + roles[k][:-2] + "\n"
            
        
        msg += signature
        if settings.SEND_REMINDER == True and self.email_sent == False:
            try:         
                send_mail(
                    subject = self.event_type.name + " " + self.event.start_time.date().strftime("%Y-%m-%d"),
                    from_email = sender,
                    recipient_list = set(rlist),
                    message = msg,
                    )
                self.email_sent = True
                
            except:
                self.email_sent = False
                
            self.save()
    
class Token(models.Model):
    token = models.CharField(max_length = 250)
    creation_date = models.DateField(auto_now_add=True)

class Participation(models.Model):
    """This is the relationsship model between Users and Events.
    
    We have this because we need to store the RSVP status of the user and what role the user should have."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    event = models.ForeignKey(Event)
    attending = models.CharField(max_length=10, default="null")
    role = models.ForeignKey(Role)
    email_sent = models.BooleanField(default = False)
    last_email_sent = models.DateField(blank = True, null = True)

    def status_as_icon(self):
        if self.attending == "null":
            src = "/static/images/yellow_circle.png"
        if self.attending == "true":
            src = "/static/images/tick.png"                    
        if self.attending == "false":
            src = "/static/images/cross.png"
        return "<img style='float:right;height:9px; margin-right:15px' src='%s'>" % src


def send_login(self):
    send_mail(
        subject = "inloggningsuppgifter till Roseniuskyrkans planeringsverktyg",
        from_email = sender,
        recipient_list = (self.email, ),
        message = login % (self.first_name, settings.SITE_ROOT + "/account/initialize/?user=" + str(self.pk) + "&hash=" + self.generate_hash() + "\n" + signature)
        )

def generate_hash(self):
    signer = Signer()
    value = signer.sign(self.username)
    return value.split(":")[1]

User.add_to_class('send_login', send_login)
User.add_to_class('generate_hash', generate_hash)