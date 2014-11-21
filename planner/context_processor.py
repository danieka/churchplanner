from django.http import HttpRequest
import planner.models

def event_processor(HttpRequest):
    """This adds all the event to the request context when the main page is loaded."""
    l = []
    for event in planner.models.EventType.objects.all():
        l.append(event.name)
    return {'eventtype': l}