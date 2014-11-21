# -*- coding: utf-8 -*-
from copy import copy
import json
from django.conf import settings
from django.forms import Textarea, forms
from django.forms.widgets import flatatt, DateTimeInput
from django.utils.safestring import mark_safe


class TokenInputWidget(Textarea):
    choices = []
    template = u'''
<input type="text" %(attrs)s>
<script type="text/javascript">
    $(document).ready(function() {
        $('#%(id)s').tokenInput($.users, {onAdd: function (item) { onAdd(item, $(this).prev().children().last().prev()); }, %(configuration)s});
    });
</script>
'''

    class Media:
        css = {
            'all': (
                '/static/jquery_fields/tokeninput/styles/token-input.css',
            ),
        }
        js = (
            '/static/jquery_fields/tokeninput/src/jquery.tokeninput.js',
        )

    def __init__(self, json_source, configuration=None, attrs=None):
        """
        'json_source' url where tokeninput can get JSON choices.
        'configuration' dict which will be directly sent to tokenInput constructor as second argument.

        For more info about 'json_source' and 'configuration' look http://loopj.com/jquery-tokeninput/
        """
        self.json_source = json_source
        self.configuration = configuration or {}
        super(Textarea, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        configuration = copy(self.configuration)
        if 'prePopulate' not in configuration:
            configuration['prePopulate'] = []

        if value is not None:
            configuration['prePopulate'].extend([{'id': v, 'name': label} for v, label in self.choices])

        attrs['id'] = attrs['id'].replace(" ", "")
        final_attrs = self.build_attrs(attrs, name=name)
        context = {
            'id': final_attrs.get('id', '_'),
            'attrs': flatatt(final_attrs),
            'json_source': self.json_source,
            'configuration': json.dumps(configuration)[1:-1]
        }
        return mark_safe(self.template % context)


class BootstrapDateTimePicker(DateTimeInput):
    template = u'''
<div id="%(id)s_wrapper" class="input-append">
    <input%(attrs)s/>
    <span class="add-on">
        <i data-time-icon="icon-time" data-date-icon="icon-calendar"></i>
    </span>
</div>
<script type="text/javascript">
    $(document).ready(function() {
        $('#%(id)s_wrapper').datetimepicker(%(configuration)s);
    });
</script>
'''

    def __init__(self, attrs=None, format=None, configuration=None):
        self.configuration = configuration or {}
        super(BootstrapDateTimePicker, self).__init__(attrs=attrs, format=format)

    def _media(self):
        css = {'all': ('jquery_fields/bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css',)}
        if settings.DEBUG:
            js = ('jquery_fields/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js',)
        else:
            js = ('jquery_fields/bootstrap-datetimepicker/js/bootstrap-datetimepicker.min.js',)
        language = self.configuration.get('language', 'en')
        if language and language != 'en':
            js = js + ('jquery_fields/bootstrap-datetimepicker/js/locales/bootstrap-datetimepicker.%s.js' % language,)
        return forms.Media(css=css, js=js)

    media = property(_media)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = self._format_value(value)
        context = {
            'id': final_attrs.get('id', '_').replace(" ", ""),
            'attrs': flatatt(final_attrs),
            'configuration': json.dumps(self.configuration)
        }
        return mark_safe(self.template % context)
