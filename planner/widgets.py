# -*- coding: utf-8 -*-
from planner.models import Participation
import json
from copy import copy
from django.forms.widgets import flatatt
from jquery_fields.widgets import TokenInputWidget
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

class ParticipationTokenInputWidget(TokenInputWidget):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop("event", None)
        self.role = kwargs.pop("role", None)
        super(ParticipationTokenInputWidget, self).__init__(*args, **kwargs)

        self.template = u'''
<input type="text" %(attrs)s>
<script type="text/javascript">
    $(document).ready(function() {
        $('#%(id)s').tokenInput($.users, {
            onAdd: function (item) { onAdd(item, $(this).prev().children().last().prev()); }, 
            onDelete: function (item) { onDelete(item, $(this)); }, 
            preventDuplicates: true,
            tokenFormatter: function(item){ return "<li><p>" + item.name + "</p>" + "<span style='float:left;padding-left:0.5em'>" + item.status + "</span></li>"}, 
            %(configuration)s
            });
    });
</script>
'''

    def render(self, name, value, attrs=None):
        configuration =  copy(self.configuration)

        if 'prePopulate' not in configuration:
            configuration['prePopulate'] = []

        if value is not None:
            if self.event == None:
                configuration['prePopulate'].extend([{'id': v, 'name': label} for v, label in self.choices])
            else:
                for v, label in self.choices:
                    if User.objects.get(pk=v).participation_set.get(event=self.event, role=self.role).attending == "null":
                        src = "/static/images/yellow_circle.png"
                    if User.objects.get(pk=v).participation_set.get(event=self.event, role=self.role).attending == "true":
                        src = "/static/images/tick.png"                    
                    if User.objects.get(pk=v).participation_set.get(event=self.event, role=self.role).attending == "false":
                        src = "/static/images/cross.png"

                    status = "<img style='float:right;height:9px; margin-right:15px' src='%s'>" % src
                    configuration['prePopulate'].extend([{'id': v, 'name': label, 'status': status}])


        attrs['id'] = attrs['id'].replace(" ", "")
        final_attrs = self.build_attrs(attrs, name=name)
        context = {
            'id': final_attrs.get('id', '_'),
            'attrs': flatatt(final_attrs),
            'json_source': self.json_source,
            'configuration': json.dumps(configuration)[1:-1],
            'event': self.event,
        }
        return mark_safe(self.template % context)