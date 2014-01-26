from django.http import HttpRequest
import models
from models import valid_events

def event_processor(HttpRequest):
    """This adds all the event to the request context when the main page is loaded."""
    if HttpRequest.path == "/":
        l = []
        for event in valid_events:
            l.append({'type': event, 'verbose_name': eval("models.%s._meta.verbose_name" % event)})
        return {'events': l}
    
    return {}