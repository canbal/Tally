from django import forms
from django.forms import ModelForm
from GenericTest.models import *


class CreateTestInstanceForm(ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('test', 'owner', 'run_time', 'counter')
        
        
class DisplayTestInstanceForm(ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('counter')