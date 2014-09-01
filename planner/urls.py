from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from views import *

urlpatterns = patterns('',
                       (r'^extended/$', login_required(TemplateView.as_view(template_name='main.html'))),

                       (r'^table/$', login_required(TemplateView.as_view(template_name='event_table.html'))),
                       (r'^table/(?P<eventtype>[\w|\W]+)/$', event_table),
                       (r'^getevents/$', get_events),
                       (r'^getevents/(\d{4}-\d{2}-\d{2})--(\d{4}-\d{2}-\d{2})/$', get_events),
                       (r"^event/(?P<pk>\d{1,6})/participation/(?P<participation_name>[\w|\W]+)/add/(?P<user>\d{1,6})/$", participation_add),
                       (r"^event/(?P<pk>\d{1,6})/participation/(?P<participation_name>[\w|\W]+)/delete/(?P<user>\d{1,6})/$", participation_delete),
                       (r"^event/(?P<eventtype>[\w|\W]+)/form/(?P<pk>\d{1,6})/$", event_form),
                       (r"^event/(?P<eventtype>[\w|\W]+)/form/$", event_form),
                       (r"^event/(?P<eventtype>[\w|\W]+)/delete/(?P<pk>\d{1,6})/$", event_delete),

                       (r"^users/$", get_users),
                       (r"^participation/$", participation_form),
                       (r"^participation/(?P<pk>\d{1,6})/$", participation_form),
                       (r"^participation/thanks/$", TemplateView.as_view(template_name='participation_thanks.html')),
                       )

