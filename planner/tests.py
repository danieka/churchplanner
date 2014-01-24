# -*- coding: utf-8 -*-
import os, sys
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.test import TestCase
from models import Service
import pdb


from jquery_fields.fields import ModelMultipleChoiceTokenInputField
from jquery_fields.widgets import TokenInputWidget

class TestForm(ModelForm):
    configuration = {
            'hintText': 'Skriv in ett namn',
            'noResultsText': "Ingen träff",
            'searchingText': 'Söker',
            }
    
    host = ModelMultipleChoiceTokenInputField(User.objects.all(), json_source=('users'), configuration=configuration)
    
    class Meta:
        fields = ['host']
        
        

        model = Service

        
class TestModelMultipleChoiceTokenInputField(TestCase):
    def setUp(self):
        self.form = TestForm()
        
    def testWidget(self):
        print self.form.fields['host'].widget
        self.assertIsInstance(self.form.fields['host'].widget, TokenInputWidget)
        
        

if __name__ == '__main__':
    unittest.main()