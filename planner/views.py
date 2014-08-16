# -*- coding: utf-8 -*-
import json
import datetime
import calendar
import operator
import urllib

from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.encoding import iri_to_uri
from django.views.generic.edit import FormView

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
import tasks
from mailsnake import MailSnake
from mailsnake.exceptions import *



class AssociateRedirect(OAuthRedirect):
    """This is the view that redirects to facebook when someone wants to link their
    account with facebook."""
    def get_callback_url(self, provider):
        return reverse('associate-callback', kwargs={'provider': provider.name})


class AssociateCallback(OAuthCallback):
    """This is what happens when the user has authenticated with facebook."""

    def get_or_create_user(self, provider, access, info):
        return self.request.user
    
    def handle_existing_user(self, provider, user, access, info):
        """Here we actually associate fb-account with the our local account."""
        if user != self.request.user:
            return self.handle_login_failure(provider, "Another user is associated with this account")
        # User was already associated with this account
        return super(AssociateCallback, self).handle_existing_user(provider, user, access, info)

class LoginRedirect(OAuthRedirect):    
    def get_additional_parameters(self, provider):
        """We need to ask facebook for permissions to create events on the facebook page."""
        if provider.name == 'facebook':
            return {'scope': "create_event"}
        return super(AdditionalPermissionsRedirect, self).get_additional_parameters(provider)

    def get_callback_url(self, provider):
        return reverse('login-callback', kwargs={'provider': provider.name})

class LoginCallback(OAuthCallback):
    def handle_existing_user(self, provider, user, access, info):
        """Here we store the access token for the facebook page that we got from facebook."""
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
def get_events(request):
    """This returns all events, or a subset of them. Parameters are passed in the GET request."""
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
    """View for creating and modifying events."""
    #BUG: Ändringar i vilka butiker en notering gäller ändras inte
    if eventtype != None:
        try:
            eventtype = urllib.unquote(eventtype.encode('ascii')).decode('utf-8')
        except:
            pass

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
def get_users(request):
    """Returns all users, this is used for typeahead in all forms."""
    l = []
    for user in User.objects.all():
        l.append({'id': user.pk, 'name': user.first_name + " " +  user.last_name})
    response = json.dumps(l)
    return HttpResponse(response, content_type="application/json")

@login_required
def event_delete(request, pk, eventtype):
    Event.objects.get(pk=pk).delete()
    response = json.dumps("Success")
    return HttpResponse(response, content_type="application/json")

def account_initialize(request):
    """This view displays the choice between creating a local account or linking with facebook."""
    user = authenticate(hash=request.GET['hash'], pk = request.GET['user'])
    if not user or not user.is_active:
        response = json.dumps("Din länk är felaktig, så det finns inte så mycket vi kan göra just nu. Prata med Daniel K så listar han ut vad som är fel.")
        return HttpResponse(response, content_type="application/json")
    else:
        login(request, user)
        return render(request, 'register.html')
    
def test(request):
    """This is just a function I use when I want to test a function."""
    resp = "a"
    return HttpResponse(resp, content_type="application/json")

@login_required
def fileuploader(request, pk):
    """This is the form that displays and uploads documents."""
    files = Event.objects.get(pk = pk).documents.all()
        
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, user = request.user, pk=pk)
        if form.is_valid():
            form.save()            
     
    form = DocumentForm(user = request.user)
    return render_to_response('fileuploader.html', {'form': form, 'pk': pk, 'files': files}, context_instance = RequestContext(request))

def participation_form(request, pk = None):
    """This is the view that contributers see when they accept/decline participation."""
    if pk and request.method == "POST":
        participation = Participation.objects.get(pk = pk)
        if request.POST["accept"] == "true":
            participation.attending = "true"
        elif request.POST["accept"] == "false":
            participation.attending = "false"
        participation.save()
        participation.attending
            

    if not request.user:
        user = authenticate(hash=request.GET['hash'], pk = request.GET['user'])
    else:
        user = request.user
        
    upcoming = user.participation_set.filter(event__event__start_time__gte=datetime.datetime.now())
    events = []
    for event in upcoming:
        events.append({'name': event.event.title, 'date': event.event.event.start_time, 'role': event.role.name, 'pk': event.pk, 'attending': event.attending, 'type': event.event.event_type.name})
    return render(request, 'participation_form.html', {'events': events, 'pk': pk})

@login_required
def viewer(request, pk):
    """The view for the fileviewer."""
    documents = Event.objects.get(pk = pk).documents.all()
    return render(request, 'viewer.html', {'documents': documents, 'initial': iri_to_uri(request.GET['file'])})

class SendInvitationsView(FormView):
    template_name = 'send_invitations.html'
    form_class = SendInvitationsForm
    success_url = '/administration/send_invitations_confirmation/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        for user in form.cleaned_data["users"]:
            user.send_login()
        return super(FormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FormView, self).get_context_data(**kwargs)
        l = []
        for user in User.objects.all():
          l.append({'id': user.pk, 'name': user.first_name + " " +  user.last_name})
        context["users"] = json.dumps(l, ensure_ascii=False)
        return context

def get_mailchimp_users(request):
    list_id = "63c4d992d8"
    try:
        m = MailSnake('c1ef033d26e799af744c00edc821634b-us8', api='export')
        members = m.list(id=list_id)
        print len(members)
    
    # except mailchimp.ListDoesNotExistError:
    #     messages.error(request, "The list does not exist")
    #     return redirect('/')
    
    except mailchimp.Error, e:
        print(request, 'An error occurred: %s - %s' % (e.__class__, e))
        return redirect('/')
    
    new_users = 0
    for member in members[1:]:
        if len(User.objects.filter(email = member[0])) == 0 and len(User.objects.filter(username = member[1] + "." + member[2])) == 0:
            new_user = User.objects.create_user(username=member[1] + "." + member[2], email=member[0])
            new_user.first_name = member[1]
            new_user.last_name = member[2]
            new_user.save()
            new_users += 1

    return render_to_response('get_mailchimp_users.html', {'new_users': new_users}, context_instance=RequestContext(request))

def send_email_participation(request):
    tasks.send_email_participation()
    return HttpResponse("Email successfully sent", content_type="application/json")
