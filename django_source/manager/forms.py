from django import forms
from django.forms import ModelForm, Textarea
from GenericTest.models import *


class CreateTestInstanceForm(ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('test', 'owner', 'collaborator', 'run_time', 'counter')
        widgets = {
            'description': Textarea(),
        }
        
        
class DisplayTestInstanceForm(ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('counter')
        widgets = {
            'description': Textarea(),
        }