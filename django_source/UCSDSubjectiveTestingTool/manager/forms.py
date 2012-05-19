from django import forms
from django.forms import ModelForm, ModelMultipleChoiceField
from GenericTest.models import *

class CreateTestForm(ModelForm):
    collaborator = ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Testers'), required=False)
    
    class Meta:
        model = Test
        exclude = ('owner','create_time')
        
class DisplayTestForm(ModelForm):
    class Meta:
        model = Test
        exclude = ('title',)
            
class CreateTestInstanceForm(ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('test', 'owner', 'run_time', 'counter')
        
        
class DisplayTestInstanceForm(ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('counter')