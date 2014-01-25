# -*- coding: utf-8 -*-
from django.forms import ModelForm, SelectMultiple, ValidationError, DateInput, Textarea, DateField, TimeField
from models import Service, Vardag, Occurrence
from django.core.urlresolvers import reverse_lazy
import pytz

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Column, Submit, Button
from django.contrib.auth.models import User

import json
import datetime
from jquery_fields.fields import ModelMultipleChoiceTokenInputField


class ServiceForm(ModelForm):
    start_date = DateField(label="Startdatum")
    start_time = TimeField(label="Starttid")
    end_time = TimeField(label="Sluttid", required=False)
    
    class Meta:
        
        
        datewidgetoptions = {'class': "dateInput token-input-list"}
        
        model = Service
        fields = ["title", "start_date", "start_time", "end_time", "organiser", "speaker", "meeting_leader", "technician", "host", "music", "organ", "bible_reader", "personal_prayer", "prayer" ,"facebook_publish", "publish_date", "description", "internal_notes"]
        
        widgets = {
            'start_date': DateInput(attrs=datewidgetoptions),
            'publish_date': DateInput(attrs=datewidgetoptions),
            'description': Textarea(),
            'internal_notes':Textarea(),
        }
        
    def __init__(self, *args, **kwargs):        
        user = kwargs.pop('user', None)
        
        super(ServiceForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = "event_form"
        self.helper.form_action = "/planner/Service/form"
        self.helper.layout = Layout(
            Column("title", "start_date", "start_time", "end_time", "organiser", "speaker", "meeting_leader", "host", "technician", "music", "organ", "bible_reader", "personal_prayer", "prayer", "facebook_publish", "publish_date"),
            Column("description", "internal_notes", css_id="left_div"),
            Div(
                Submit('submit', 'Spara', css_id="submit"), 
                Button('delete', 'Ta bort evenemang', css_id="delete"),
                css_id="submit_div"),
        ) 
           
        for fieldname in ['host', 'music', 'personal_prayer']:
                self.fields[fieldname].help_text = None 
                
        
        
        if not self.is_bound and self.instance.pk:

            
            start_time = self.instance.event.start_time.astimezone(pytz.timezone("Europe/Stockholm"))
            self.fields['start_date'].initial = start_time.date().strftime("%Y-%m-%d")
            self.fields['start_time'].initial = start_time.time().strftime("%X")
            if self.instance.event.end_time:
                #self.fields['end_date'].initial = self.instance.event.end_time.date().strftime("%Y-%m-%d")
                self.fields['end_time'].initial = self.instance.event.end_time.time().strftime("%X")
                
    
          
    def save(self, commit=True):
        instance = super(ServiceForm, self).save(commit=False)
        start_time= datetime.datetime.combine(self.cleaned_data['start_date'], self.cleaned_data['start_time'])
        tz = pytz.timezone("Europe/Stockholm")
        end_time = None

        print self.cleaned_data['host']
     
        if self.cleaned_data['end_time'] != None:
            end_time = tz.localize(datetime.datetime.combine(self.cleaned_data['start_date'], self.cleaned_data['end_time']))
        
        if instance.event:
            instance.event.delete()
        instance.event =  Occurrence.objects.create(start_time = tz.localize(start_time), end_time=end_time)

        if commit:
            instance.save()
            self.save_m2m()
        return instance