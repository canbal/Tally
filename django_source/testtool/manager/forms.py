from django import forms
from testtool.models import *


class TestCreateForm(forms.ModelForm):
    collaborators = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Testers'), required=False)
    class Meta:
        model = Test
        exclude = ('owner','create_time')

class TestUpdateForm(forms.ModelForm):
    collaborators = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Testers'), required=False)
    method = forms.CharField(widget=forms.TextInput(attrs={'readonly':True})) # make the field readonly
    class Meta:
        model = Test
        exclude = ('owner','create_time')

    # to ensure that the readonly value won't be overridden by a POST
    def clean_method(self):
        return self.instance.method
    
class TestCaseCreateForm(forms.Form):
    filename1 = forms.ModelChoiceField(queryset = Video.objects.all(), required = True)
    filename2 = forms.ModelChoiceField(queryset = Video.objects.all(), required = True)

class TestDisplayForm(forms.ModelForm):
    class Meta:
        model = Test
        exclude = ('title',)

class CreateTestInstanceForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(user__groups__name__iexact='Subjects'), required=False)
    class Meta:
        model = TestInstance
        exclude = ('test', 'owner', 'collaborators', 'run_time', 'counter', 'key')
        
        
class DisplayTestInstanceForm(forms.ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('counter', 'key')