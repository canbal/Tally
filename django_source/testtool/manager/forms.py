from django import forms
from django.forms import ModelForm, Textarea, ModelMultipleChoiceField, TypedMultipleChoiceField
from testtool.models import *


class TestCreateForm(ModelForm):
    collaborators = ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Testers'), required=False)
    class Meta:
        model = Test
        exclude = ('owner','create_time')
        widgets = {
            'description': Textarea(),
        }
        
        
class TestDisplayForm(ModelForm):
    class Meta:
        model = Test
        exclude = ('title',)
        widgets = {
            'description': Textarea(),
        }


class CreateTestInstanceForm(ModelForm):
    collaborators = ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Testers'), required=False)
    subjects = ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Subjects'), required=False)
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