# -*- coding: utf-8 -*-
import datetime
from planner.models import Event, Participation, generate_user_hash
from django.contrib.auth.models import User
from django.conf import settings
from django.template import loader, Context
from django.core.mail import send_mail, EmailMessage
from django.utils import timezone
from itertools import chain
import traceback


# views.py
import logging

logger = logging.getLogger("churchplanner")

status = {"null": "Obestämt", "true": "Kan medverka", "false": "Kan inte medverka"}

def publish_task():
    if not settings.PUBLISH_TO_FACEBOOK:
        return
    events = Event.objects.all()
    for event in events:
        if event.facebook and not event.published:
            if event.publish_date >= datetime.date.today():
                event.publish()
                
def send_email_task():
    if not settings.SEND_REMINDER_EMAIL:
        return
    events = Event.objects.filter(event__start_time__range=[datetime.date.today(), datetime.date.today() + datetime.timedelta(days=6)], email_sent=False)
    for event in events:
        event.send_mail()

def send_updated_participations():
    if not settings.SEND_PARTICIPATION_EMAIL:
        return
    updated = Participation.objects.filter(updated = True)
    if len(updated) == 0:
        return

    template_html = 'updated_participations.html'
    subject = "Uppdaterade anmälningar"
    participations = []
    for p in updated:
        t = {}
        t['type'] = p.event.event_type.name
        t['date'] = p.event.event.start_time
        t['role'] = p.role
        t['name'] = "%s %s" % (p.user.first_name, p.user.last_name)
        t['status'] = status[p.attending]
        participations.append(t)
    rlist = [u.email for u in User.objects.filter(is_staff = True)]
    from_email = settings.SENDER          
    html = loader.get_template(template_html)
    c = Context({ 'participations': participations})
    html_content = html.render(c)

    msg = EmailMessage(subject,html_content, from_email, rlist)
    msg.content_subtype = "html"
    try:
        msg.send()
    except ValueError as e:
        logger.error("Exception: %s" % e)
        logger.error("To: %s" % rlist)
        logger.error("From %s" % sender)
        logger.error(traceback.format_exc())
        return

    for p in updated:
        p.updated = False
        p.save()
    logger.info(html_content)
                     
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
        event_set = user.participation_set.filter(event__event__start_time__gte= timezone.now(), email_sent = False, attending="null")
        event_set = chain(event_set, user.participation_set.filter(event__event__start_time__gte= timezone.now(), attending = "null", last_email_sent__lte = datetime.date.today() - datetime.timedelta(days = 7)))
        for participation in event_set:
            events.append({'date':participation.event.event.start_time, 'type': participation.event.event_type.name, 'role': participation.role.name})
            
        if len(events) != 0:
            from_email = settings.SENDER          
            html = loader.get_template(template_html)
            c = Context({ 'events': events, 'name': user.first_name + " " + user.last_name, 'url':url })
            html_content = html.render(c)

            msg = EmailMessage(subject,html_content, from_email, [to])
            msg.content_subtype = "html"
            try:
                msg.send()
            except ValueError as e:
                logger.error("Exception: %s" % e)
                logger.error("To: %s" % to)
                logger.error("From %s" % sender)
                logger.error(traceback.format_exc())
                continue

            logger.info(html_content)

            event_set = user.participation_set.filter(event__event__start_time__gte= timezone.now(), email_sent = False)
            event_set = chain(event_set, user.participation_set.filter(event__event__start_time__gte= timezone.now(), attending = "null", last_email_sent__lte = datetime.date.today() - datetime.timedelta(days = 7)))
            for participation in event_set:
                participation.email_sent = True
                participation.last_email_sent = datetime.date.today()
                participation.save()