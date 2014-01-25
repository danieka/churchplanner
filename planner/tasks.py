import datetime
from celery.decorators import task
from models import Service, Vardag

@task
def publish_task():
    for service in Service.objects.all():
        if service.facebook and not service.published:
            if service.publish_date <= datetime.date.today():
                service.publish()