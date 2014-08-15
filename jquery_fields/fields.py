# -*- coding: utf-8 -*-
from django.forms import ModelMultipleChoiceField, MultipleChoiceField, ChoiceField, ModelChoiceField
from jquery_fields.widgets import TokenInputWidget


class TokenInputFieldMixin(object):
    widget = TokenInputWidget
    configuration = {'tokenLimit': 1}

    def __init__(self, choices, json_source, configuration=None, *args, **kwargs):
        if configuration is None:
            configuration = {}
        configuration.update(self.configuration)
        if 'widget' not in kwargs or kwargs['widget'] is None:
            kwargs['widget'] = self.widget(json_source, configuration)
        else:
            kwargs['widget'] = kwargs['widget'](json_source, configuration, event = kwargs.pop("event"), role = kwargs.pop("role", None))

        super(TokenInputFieldMixin, self).__init__(choices, *args, **kwargs)


class MultipleTokenInputFieldMixin(TokenInputFieldMixin):
    configuration = {}

    def clean(self, value):
        if value:
            if hasattr(value, '__iter__'):
                return value
            else:
                return super(MultipleTokenInputFieldMixin, self).clean(value.split(','))
        else:
            return []

    def prepare_value(self, value):
        if value and isinstance(value, str):
            value = value.split(',')
        value = super(MultipleTokenInputFieldMixin, self).prepare_value(value)
        return value


class ChoiceTokenInputField(TokenInputFieldMixin, ChoiceField):
    def __init__(self, choices, json_source, *args, **kwargs):
        super(ChoiceTokenInputField, self).__init__(choices, json_source, *args, **kwargs)


class ModelChoiceTokenInputField(TokenInputFieldMixin, ModelChoiceField):
    choices = []    # choices are always equal to field value, look into 'prepare_value' implementation

    def __init__(self, queryset, json_source, *args, **kwargs):
        super(ModelChoiceTokenInputField, self).__init__(queryset, json_source, *args, **kwargs)

    def prepare_value(self, value):
        # setup widget choices to current field value
        choices = []
        if value:
            obj = self.clean(value)
            choices.append((super(ModelChoiceTokenInputField, self).prepare_value(obj), self.label_from_instance(obj)))
        self.widget.choices = choices
        return super(ModelChoiceTokenInputField, self).prepare_value(value)


class MultipleChoiceTokenInputField(MultipleTokenInputFieldMixin, MultipleChoiceField):
    def __init__(self, choices, json_source, *args, **kwargs):
        super(MultipleChoiceTokenInputField, self).__init__(choices, json_source, *args, **kwargs)


class ModelMultipleChoiceTokenInputField(MultipleTokenInputFieldMixin, ModelMultipleChoiceField):
    choices = []    # choices are always equal to field value, look into 'prepare_value' implementation

    def __init__(self, queryset, json_source, *args, **kwargs):
        super(ModelMultipleChoiceTokenInputField, self).__init__(queryset, json_source, *args, **kwargs)

    def prepare_value(self, value):
        # setup widget choices to current field value
        choices = []
        for obj in self.clean(value):
            choices.append((super(ModelMultipleChoiceTokenInputField, self).prepare_value(obj), obj.first_name + " " + obj.last_name))
        self.widget.choices = choices
        return super(ModelMultipleChoiceTokenInputField, self).prepare_value(value)
