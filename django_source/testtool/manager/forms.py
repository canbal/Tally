from django import forms
from testtool.models import *


class CreateTestForm(forms.ModelForm):
    class Meta:
        model = Test
        exclude = ('owner','collaborators')

        
class EditTestForm(forms.ModelForm):
    method = forms.CharField(widget=forms.TextInput(attrs={'readonly':True})) # make the field readonly
    class Meta:
        model = Test
        exclude = ('owner','collaborators')

    # to ensure that the readonly value won't be overridden by a POST
    def clean_method(self):
        return self.instance.method
    

class DisplayTestForm(forms.ModelForm):
    method = forms.CharField(widget=forms.TextInput(attrs={'readonly':True})) # make the field readonly
    class Meta:
        model = Test
        exclude = ('owner')
        
    def __init__(self, *args, **kwargs):
        super(DisplayTestForm, self).__init__(*args, **kwargs)
        self.fields['collaborators'].widget.attrs={'readonly':True}
        self.fields['collaborators'].queryset = self.instance.collaborators
        self.fields['title'].widget.attrs={'readonly':True}
        self.fields['description'].widget.attrs={'readonly':True}

    # to ensure that the readonly value won't be overridden by a POST
    def clean_collaborators(self):
        return self.instance.collaborators
    def clean_title(self):
        return self.instance.title
    def clean_description(self):
        return self.instance.description
    def clean_method(self):
        return self.instance.method

class TestCaseCreateFormDiscrete(forms.Form):
    filename1 = forms.ModelChoiceField(queryset = Video.objects.all(), required = True)
    filename2 = forms.ModelChoiceField(queryset = Video.objects.all(), required = True)

    
class TestCaseCreateFormSSCQE(forms.Form):
    filename = forms.ModelChoiceField(queryset = Video.objects.all(), required = True)


class CreateTestInstanceForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(label='Enrolled Subjects', queryset=UserProfile.objects.filter(user__groups__name__iexact='Subjects'), required=False)
    class Meta:
        model = TestInstance
        exclude = ('test', 'owner', 'collaborators', 'run_time', 'counter', 'key')
    # to ensure that the readonly value won't be overridden by a POST
    def clean_method(self):
        return self.instance.method        
        
        
class DisplayTestInstanceForm(forms.ModelForm):
    class Meta:
        model = TestInstance
        exclude = ('counter', 'key')