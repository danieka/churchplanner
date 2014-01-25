from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
                       (r'^getallevents/$', get_events),
                       (r"^event/(?P<eventtype>[A-Za-z]+)/form/(?P<pk>\d{1,6})/$", event_form),
                       (r"^event/(?P<eventtype>[A-Za-z]+)/form/$", event_form),
                       (r"^event/(?P<eventtype>[A-Za-z]+)/delete/(?P<pk>\d{1,6})/$", event_delete),
                       (r"^users/$", users),
                       )

