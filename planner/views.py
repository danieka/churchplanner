# -*- coding: utf-8 -*-
import json
import datetime
import calendar

from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from models import Service, Vardag, valid_events, Token, generate_login_link
from forms import *
from open_facebook.api import FacebookAuthorization, OpenFacebook

from django.core.urlresolvers import reverse
from allaccess.views import OAuthRedirect, OAuthCallback
from django.contrib.auth import authenticate, login


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
    services = Service.objects.all().order_by('event__start_time')[:events_to_get]
    data = []
    for service in services:
        data.append({'type': service.__class__.__name__, 'pk': service.pk, 'verbose_name': service._meta.verbose_name, 'title': service.title, 'timestamp':calendar.timegm(service.event.start_time.timetuple()) * 1000})
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
    
    if pk and (eventtype in valid_events):
            instance = eval("%s.objects.get(pk=pk)" % eventtype)
    
    if request.method == "GET":
        if pk:
            title = instance.title
            form = eval("%sForm(instance = instance, user = request.user)" % eventtype)
        else:
            title = ("Ny %s" % eval("%s._meta.verbose_name" % eventtype))
            form = eval("%sForm(user=request.user)" % eventtype)


    elif request.method == "POST":
        title = eval("%s._meta.verbose_name" % eventtype)
        if pk:
            form = eval("%sForm(request.POST, user = request.user, instance=instance)" %eventtype)
        else:
            form = eval("%sForm(request.POST, user = request.user)" %eventtype)
        
        if form.is_valid():
            pk = form.save().pk           
            response = json.dumps({'pk': pk, 'response':"%s sparad" % title})
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
    resp = generate_login_link(pk=request.GET['pk'])
    return HttpResponse(resp, content_type="application/json")