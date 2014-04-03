# -*- coding: utf-8 -*-
import datetime
from celery.decorators import task
from models import Event, generate_user_hash, sender
from django.contrib.auth.models import User
from django.conf import settings
from django.template import loader, Context
from django.core.mail import send_mail

@task
def publish_task():
    events = Event.objects.all()
    for event in events:
        if event.facebook and not event.published:
            if event.publish_date >= datetime.date.today():
                event.publish()
                
@task
def send_email_task():
    if not settings.SEND_REMINDER_EMAIL:
        return
    events = Event.objects.all()
    for event in events:
        if not event.email_sent and event.event.start_time.date() > (datetime.date.today() - datetime.timedelta(days=5)):
            event.send_reminder()
            
@task            
def send_email_participation():
    if not settings.SEND_PARTICIPATION_EMAIL:
        return
    template_html = 'participation_request.html'
    users = User.objects.all()
    subject = "Kan du hjälpa till?"
    events = []
    for user in users:
        to = user.email
        url = settings.SITE_ROOT + "/planner/participation/?user=" + str(user.pk) + "&hash=" + generate_user_hash(user.pk)
        for participation in user.participation_set.all():
            if not participation.email_sent:
                events.append({'date':participation.event.event.start_time.isoformat(), 'name': participation.event.title, 'role': participation.role.name})
            
        if len(events) != 0:
            from_email =sender           
            html = loader.get_template(template_html)
            c = Context({ 'events': events, 'name': user.first_name + " " + user.last_name, 'url':url })
            html_content = html.render(c)

            msg = send_mail(subject,html_content, from_email, [to])
            
        for participation in user.participation_set.all():
            if not participation.email_sent:
                participation.email_sent = True