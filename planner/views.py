# -*- coding: utf-8 -*-
import json
import datetime
import calendar
import operator

from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from models import Token, Document
from forms import *
from open_facebook.api import FacebookAuthorization, OpenFacebook

from django.core.urlresolvers import reverse
from allaccess.views import OAuthRedirect, OAuthCallback
from django.contrib.auth import authenticate, login
from itertools import chain

import os, StringIO
from django.conf import settings
from django.views.decorators.http import require_POST
from tasks import *

class AssociateRedirect(OAuthRedirect):
    @login_required
    def get_callback_url(self, provider):
        return reverse('associate-callback', kwargs={'provider': provider.name})


class AssociateCallback(OAuthCallback):
    def handle_new_user(self, provider, access, information):
        return redirect("/register/")
    
    @login_required
    def handle_existing_user(self, provider, user, access, info):
        if user != self.request.user:
            return self.handle_login_failure(provider, "Another user is associated with this account")
        # User was already associated with this account
        return super(AssociateCallback, self).handle_existing_user(provider, user, access, info)

class LoginRedirect(OAuthRedirect):
    
    def get_additional_parameters(self, provider):
        if provider.name == 'facebook':
            return {'scope': "create_event"}
        return super(AdditionalPermissionsRedirect, self).get_additional_parameters(provider)

    def get_callback_url(self, provider):
        return reverse('login-callback', kwargs={'provider': provider.name})

class LoginCallback(OAuthCallback):
    def handle_existing_user(self, provider, user, access, info):
        if len(Token.objects.all()) < 5:
            fb = OpenFacebook(access.access_token.split("=")[1])
            me = fb.get('me/accounts')
            for page in me['data']:
                if 'Roseniuskyrkan' in page.values():
                    token = FacebookAuthorization.extend_access_token(page['access_token'])['access_token']
                
            Token.objects.create(token = token)
        
        return super(LoginCallback, self).handle_existing_user(provider, user, access, info)
    def handle_new_user(self, provider, access, information):
        return redirect("/register/")

@login_required
def get_events(request, events_to_get = 5):
    data = []
    events = []
    if 'eventtype' in request.GET:
        for eventtype in request.GET['eventtype'].split(","):
            events = chain(events, Event.objects.filter(event__start_time__gte= datetime.datetime.now(), event_type__name=eventtype))
            
    else: #Means we are returning all events
        events = Event.objects.filter(event__start_time__gte= datetime.datetime.now()).order_by("event__start_time")

    for event in events:
        data.append({'type': event.event_type.name, 'pk': event.pk, 'verbose_name': event.event_type.name, 'title': event.title, 'timestamp':calendar.timegm(event.event.start_time.timetuple()) * 1000})
    response = json.dumps({'events': data})
    return HttpResponse(response, content_type="application/json")

@login_required
def event_form(request, pk = None, eventtype = None):
    #BUG: Ändringar i vilka butiker en notering gäller ändras inte
    title = None
    l = []
    for user in User.objects.all():
        l.append({'id': user.pk, 'name': user.first_name + " " +  user.last_name})
    users = json.dumps(l, ensure_ascii=False)
    
    if pk:
            instance = Event.objects.get(pk = pk)
    
    if request.method == "GET":
        if pk:
            title = instance.title
            form = EventForm(instance = instance, user = request.user, event_type = eventtype)
        else:
            title = ("Ny %s" % eventtype)
            form = EventForm(user=request.user, event_type = eventtype)


    elif request.method == "POST":
        title = eventtype
        if pk:
            form = EventForm(request.POST, instance = instance, user = request.user, event_type = eventtype)

        else:
            form = EventForm(request.POST, user = request.user, event_type = eventtype)

        print form.is_valid()
        
        if form.is_valid():
            pk = form.save().pk           
            response = json.dumps({'pk': pk, 'response':"%s sparad" % title})
            return HttpResponse(response, content_type="application/json")
        
        else:
            print form.errors
            response = json.dumps({'pk': "fail", 'response':"%s failed" % title})
            return HttpResponse(response, content_type="application/json")
        
    return render_to_response('event_form.html', {'form': form, 'type': eventtype, 'pk':pk, 'title': title, 'users': users}, context_instance = RequestContext(request))

@login_required
def users(request):
    l = []
    for user in User.objects.all():
        l.append({'id': user.pk, 'name': user.first_name + " " +  user.last_name})
    response = json.dumps(l)
    return HttpResponse(response, content_type="application/json")

@login_required
def event_delete(request, pk, eventtype):
    eval("%s.objects.get(pk=pk).delete()" % eventtype)
    response = json.dumps("Success")
    return HttpResponse(response, content_type="application/json")

def account_initialize(request):
    user = authenticate(hash=request.GET['hash'], pk = request.GET['user'])
    if not user or not user.is_active:
        response = json.dumps("Din länk är felaktig, så det finns inte så mycket vi kan göra just nu. Prata med Daniel så listar han ut vad som är fel.")
        return HttpResponse(response, content_type="application/json")
    else:
        login(request, user)
        return render(request, 'register.html')
    
def test(request):
    resp = "a"
    send_email_participation()
    return HttpResponse(resp, content_type="application/json")

@login_required
def fileuploader(request, pk):
    files = Event.objects.get(pk = pk).documents.all()
        
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, user = request.user, pk=pk)
        if form.is_valid():
            form.save()            
     
    form = DocumentForm(user = request.user)
    return render_to_response('fileuploader.html', {'form': form, 'pk': pk, 'files': files}, context_instance = RequestContext(request))

def participation_form(request, pk = None):
    if pk and request.method == "POST":
        participation = Participation.objects.get(pk = pk)
        if request.POST["accept"] == "true":
            participation.attending = "true"
        elif request.POST["accept"] == "false":
            participation.attending = "false"
        participation.save()
            

    if not request.user:
        user = authenticate(hash=request.GET['hash'], pk = request.GET['user'])
    else:
        user = request.user
        
    unanswered = user.participation_set.filter(attending="null")
    events = []
    for event in unanswered:
        events.append({'name': event.event.title, 'date': event.event.event.start_time.isoformat(), 'role': event.role.name, 'pk': event.pk})
    return render(request, 'participation_form.html', {'events': events})


