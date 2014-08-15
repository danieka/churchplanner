# -*- coding: utf-8 -*-
from django.utils.html import mark_safe
from django.forms import ModelForm, SelectMultiple, ValidationError, DateInput, Textarea, DateField, TimeField, Form
from models import Occurrence, Event, EventType, Participation, Role, Document
from django.core.urlresolvers import reverse_lazy
import pytz

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Column, Submit, Button
from django.contrib.auth.models import User

from django.core.files import File

import json
import datetime
from jquery_fields.fields import ModelMultipleChoiceTokenInputField
from widgets import ParticipationTokenInputWidget

class EventForm(ModelForm):
    """This is the form for all events."""
    start_date = DateField(label="Startdatum")
    start_time = TimeField(label="Starttid")
    end_time = TimeField(label="Sluttid", required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.event_type = EventType.objects.get(name = kwargs.pop('event_type', None))
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = Textarea()
        self.fields['internal_notes'].widget = Textarea()
        
        self.helper = FormHelper()
        self.helper.form_id = "event_form"              
        self.helper.layout = Layout(
            Column("title", "start_date", "start_time", "end_time", css_id="left_div"),
            Column("description", "internal_notes", css_id="right_div"),
            Div(
                Submit('submit', 'Spara', css_id="submit"), 
                Button('delete', 'Ta bort evenemang', css_id="delete"),
                css_id="submit_div"),
        )
            
        self.construct_fields()
                  
        if not self.is_bound and self.instance.pk: #This mean we are modifying a existing event
            self.bind_fields()
            
        if not self.instance.pk:
            self.fields['description'].initial = self.event_type.initial_description
            
    def save(self, commit=True):
        instance = super(EventForm, self).save(commit=False)
        print self.instance.participants.all()
        if not hasattr(self.instance, "event_type"):
            self.instance.event_type = self.event_type
        start_time= datetime.datetime.combine(self.cleaned_data['start_date'], self.cleaned_data['start_time'])
        tz = pytz.timezone("Europe/Stockholm")
        end_time = None
     
        if self.cleaned_data['end_time'] != None:
            end_time = tz.localize(datetime.datetime.combine(self.cleaned_data['start_date'], self.cleaned_data['end_time']))
        

        if instance.event:
            instance.event.delete()
        instance.event =  Occurrence.objects.create(start_time = tz.localize(start_time), end_time=end_time)

        print "iii", self.instance.participants.all()
        if commit:

            instance.save()
            
            for role in self.event_type.roles.all():
                checked_pk = []

                for user in self.cleaned_data[role.name.encode('ascii', 'ignore')]:
                    if len(user.participation_set.filter(event = self.instance, role = role)) == 0:
                        Participation.objects.create(user = user, event = self.instance, attending = "null", role = role)
                    
        return instance
    
    def construct_fields(self):
        """Create form fields for the corresponding model fields."""
        for role in self.event_type.roles.all():
            field = ModelMultipleChoiceTokenInputField(queryset=User.objects.all(), widget=ParticipationTokenInputWidget, required = False, json_source="/planner/users/", label=role.name, 
                    configuration = {}
                    , initial = {}, event = self.instance)
            self.fields[role.name.encode('ascii', 'ignore')] = field
            self.helper.layout.fields[0].append(role.name.encode('ascii', 'ignore'))
            
    def bind_fields(self):
        """Here we initialize the form from a existing event."""
         #This part initializes the date and time.
        start_time = self.instance.event.start_time.astimezone(pytz.timezone("Europe/Stockholm"))
        self.fields['start_date'].initial = start_time.date().strftime("%Y-%m-%d")
        self.fields['start_time'].initial = start_time.time().strftime("%X")
        if self.instance.event.end_time:
            self.fields['end_time'].initial = self.instance.event.end_time.time().strftime("%X")
            
        for participant in self.instance.participants.all():
            #iterate through all existing participants to initialize the form
            relations = participant.participation_set.filter(event = self.instance) #Get the M2M-object
            for relation in relations:
                self.fields[relation.role.name.encode('ascii', 'ignore')].initial[participant] = None
        
        
    class Meta:
        model = Event
        exclude = ['email_sent', 'published', 'event', 'participants', 'event_type']
        
class DocumentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.parent_pk = kwargs.pop('pk', None)
        super(DocumentForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super(DocumentForm, self).save(commit=False)
        instance.uploader = self.user
 
        if commit:
            instance.save()
            Event.objects.get(pk = self.parent_pk).documents.add(instance)
            
        return instance
    
    class Meta:
        model = Document     
        fields = ["file_field", "name"]
        
        
class SendInvitationsForm(Form):
    users = ModelMultipleChoiceTokenInputField(queryset=User.objects.all(), 
        required = False, 
        json_source="/planner/users/", 
        label="Användare som skall få inloggningsuppgifter", 
        configuration = {}, 
        initial = {})



