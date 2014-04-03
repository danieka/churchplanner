from django.http import HttpRequest
import models

def event_processor(HttpRequest):
    """This adds all the event to the request context when the main page is loaded."""
    if HttpRequest.path == "/":
        l = []
        for event in models.EventType.objects.all():
            l.append({'type': event.name, 'verbose_name': event.name})
        return {'events': l}
    
    return {}