from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
                       (r'^getevents/$', get_events),
                       (r"^event/(?P<eventtype>[\w|\W]+)/form/(?P<pk>\d{1,6})/$", event_form),
                       (r"^event/(?P<eventtype>[\w|\W]+)/form/$", event_form),
                       (r"^event/(?P<eventtype>[\w|\W]+)/delete/(?P<pk>\d{1,6})/$", event_delete),
                       (r"^users/$", users),
                       (r"^participation/$", participation_form),
                       (r"^participation/(?P<pk>\d{1,6})/$", participation_form),
                       )

