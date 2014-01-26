from django.http import HttpRequest, HttpResponseBadRequest
from models import valid_events

class SecurityMiddleware(object):
    """This removes illegal events form all requests. 
    This is important since these things goes into eval statements."""
    def process_request(self, request):
        if "eventtype" in request.GET:
            for event in request.GET['eventtype'].split(","):
                if event not in valid_events:
                    return HttpResponseBadRequest()
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if "eventtype" in view_kwargs:
            if view_kwargs['eventtype'] not in valid_events:
                return HttpResponseBadRequest()
        return None