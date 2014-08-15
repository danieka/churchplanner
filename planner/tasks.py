# -*- coding: utf-8 -*-
import datetime
from celery.decorators import task
from models import Event, generate_user_hash, sender
from django.contrib.auth.models import User
from django.conf import settings
from django.template import loader, Context
from django.core.mail import send_mail, EmailMessage

@task
def publish_task():
    events = Event.objects.all()
    for event in events:
        if event.facebook and not event.published:
            if event.publish_date >= datetime.date.today():
                event.publish()
                
@task
def send_email_task():
    if settings.SEND_REMINDER:
        events = Event.objects.filter(event__start_time__range=[datetime.date.today(), datetime.date.today() + datetime.timedelta(days=5)])
        for event in events:
            event.send_mail()
            
@task            
def send_email_participation():
    if not settings.SEND_PARTICIPATION_EMAIL:
        return
    template_html = 'participation_request.html'
    users = User.objects.all()
    subject = "Kan du hjälpa till?"
    
    for user in users:
        events = []
        to = user.email
        url = settings.SITE_ROOT + "/planner/participation/?user=" + str(user.pk) + "&hash=" + generate_user_hash(user.pk)
        print (user, user.participation_set.all())
        for participation in user.participation_set.filter(event__event__start_time__gte=datetime.datetime.now(), email_sent = False):
            events.append({'date':participation.event.event.start_time, 'type': participation.event.event_type.name, 'role': participation.role.name})
            
        if len(events) != 0:
            from_email =sender           
            html = loader.get_template(template_html)
            c = Context({ 'events': events, 'name': user.first_name + " " + user.last_name, 'url':url })
            html_content = html.render(c)

            msg = EmailMessage(subject,html_content, from_email, [to])
            msg.content_subtype = "html"
            msg.send()

            for participation in user.participation_set.filter(event__event__start_time__gte=datetime.datetime.now(), email_sent = False):
                participation.email_sent = True
                participation.save()