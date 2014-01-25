import datetime
from celery.decorators import task
from models import Service, Vardag

@task
def publish_task():
    services = Service.objects.all().order_by('event__start_time')
    vardagar = Vardag.objects.all().order_by('event__start_time')
    events = chain(services, vardagar)
    for event in events:
        if event.facebook and not event.published:
            if event.publish_date >= datetime.date.today():
                event.publish()
                
@task
def send_email_task():
    services = Service.objects.all().order_by('event__start_time')
    vardagar = Vardag.objects.all().order_by('event__start_time')
    events = chain(services, vardagar)
    for event in events:
        if not event.email_sent and event.event.start_time.date() > (datetime.date.today() - datetime.timedelta(days=5)):
            event.send_reminder()