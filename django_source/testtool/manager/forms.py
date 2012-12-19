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
    create_time = forms.DateTimeField()
    class Meta:
        model = Test
        widgets = {'owner': forms.TextInput(), 'method': forms.TextInput()}
        
    def __init__(self, *args, **kwargs):
        super(DisplayTestForm, self).__init__(*args, **kwargs)
        # set fields to read-only
        for key in ['owner', 'create_time', 'method', 'collaborators', 'title', 'description']:
            self.fields[key].widget.attrs['readonly'] = True
        # override initial values
        self.initial['owner'] = self.instance.owner.user.username
        # define querysets
        self.fields['collaborators'].queryset = self.instance.collaborators.all()
        # define extra fields
        self.fields['create_time'].label = self.instance._meta.get_field('create_time').verbose_name
        self.fields['create_time'].initial = self.instance.create_time

    # to ensure that the readonly value won't be overridden by a POST
    def clean_collaborators(self):
        return self.instance.collaborators.all()
    def clean_title(self):
        return self.instance.title
    def clean_description(self):
        return self.instance.description
    def clean_method(self):
        return self.instance.method


class CreateTestCaseFormDiscrete(forms.Form):
    filename1 = forms.ModelChoiceField(label = 'Reference video', queryset = Video.objects.all(), required = True)
    filename2 = forms.ModelChoiceField(label = 'Test video', queryset = Video.objects.all(), required = True)
    repeat    = forms.IntegerField(min_value=1,max_value=10,required=True,initial=1)
    
    
class CreateTestCaseFormSSCQE(forms.Form):
    filename = forms.ModelChoiceField(label = 'Video', queryset = Video.objects.all(), required = True)
    repeat   = forms.IntegerField(min_value=1,max_value=10,required=True,initial=1)

        
class CreateEditTestInstanceForm(forms.ModelForm):
    available = forms.ModelMultipleChoiceField(label='Available subjects', queryset=UserProfile.objects.filter(user__groups__name__iexact='Subjects'), required=False)
    subjects = forms.ModelMultipleChoiceField(label='Enrolled subjects', queryset=UserProfile.objects.filter(user__groups__name__iexact='Subjects'), required=False)
    
    class Meta:
        model = TestInstance
        fields = ('path', 'location', 'description', 'schedule_time', 'available', 'subjects')
        
    def __init__(self, *args, **kwargs):
        super(CreateEditTestInstanceForm, self).__init__(*args, **kwargs)
        status = ''
        if self.instance.pk:
            status = self.instance.get_status()
            if status=='Complete':
                self.fields['path'].widget.attrs['readonly'] = True
                self.fields['schedule_time'].widget.attrs['readonly'] = True
                self.fields['subjects'].widget.attrs['readonly'] = True
                self.fields['available'].widget.attrs['readonly'] = True
            elif status=='Incomplete':
                self.fields['schedule_time'].widget.attrs['readonly'] = True
            self.fields['available'].queryset = UserProfile.objects.filter(user__groups__name__iexact='Subjects').exclude(pk__in=self.instance.subjects.all().values_list('pk', flat=True))
        self.status = status
        
    def clean_path(self):
        if self.instance.pk and self.status=='Complete':
            return self.instance.path
        return self.cleaned_data['path']
    def clean_schedule_time(self):
        if self.instance.pk and self.status in ['Complete', 'Incomplete']:
            return self.instance.schedule_time
        return self.cleaned_data['schedule_time']
    # def clean_subjects(self):                                 # this code seems correct, but is causing a bug.  When a test instance is 'Complete',
        # if self.instance.pk and self.status=='Complete':      # and the user clicks 'edit' and then 'save', all of the subjects are removed from
            # return self.instance.subjects.all()               # the test instance.  Commenting out this function removes this problem, but makes
        # return self.cleaned_data['subjects']                  # the edit form susceptible to POST attacks.  However, this is a very small risk.
        
        
class DisplayTestInstanceForm(forms.ModelForm):
    create_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'readonly':True}))
    status = forms.CharField(widget=forms.TextInput(attrs={'readonly':True}))
    class Meta:
        model = TestInstance
        fields = ('status', 'create_time', 'test', 'owner', 'path', 'location', 'description', 'schedule_time', 'run_time', 'collaborators', 'subjects')
        widgets = {'test': forms.TextInput(), 'owner': forms.TextInput()}   # do not use default dropdown menu
        
    def __init__(self, *args, **kwargs):
        super(DisplayTestInstanceForm, self).__init__(*args, **kwargs)
        # set fields to read-only
        for key in ['test', 'owner', 'collaborators', 'subjects', 'schedule_time', 'run_time', 'path', 'description', 'location']:
            self.fields[key].widget.attrs['readonly'] = True
        # override initial values
        self.initial['test'] = self.instance.test.__unicode__()
        self.initial['owner'] = self.instance.owner.user.username
        # define querysets
        self.fields['collaborators'].queryset = self.instance.collaborators.all()
        self.fields['subjects'].queryset = self.instance.subjects.all()
        # define extra fields
        self.fields['create_time'].label = self.instance._meta.get_field('create_time').verbose_name
        self.fields['create_time'].initial = self.instance.create_time
        self.fields['status'].label = 'Status'
        self.fields['status'].initial = self.instance.get_status()
        
    # to ensure that the readonly value won't be overridden by a POST
    def clean_test(self):
        return self.instance.test
    def clean_owner(self):
        return self.instance.owner
    def clean_collaborators(self):
        return self.instance.collaborators.all()
    def clean_subjects(self):
        return self.instance.subjects.all()
    def clean_schedule_time(self):
        return self.instance.schedule_time
    def clean_run_time(self):
        return self.instance.run_time
    def clean_path(self):
        return self.instance.path
    def clean_description(self):
        return self.instance.description
    def clean_location(self):
        return self.instance.location
    
    
class ExportDataForm(forms.Form):
    format = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices = (('report', 'Report (.pdf)'),
                                                                                       ('spreadsheet', 'Spreadsheet (.csv)'),
                                                                                       ('matlab','MATLAB (.mat)'),
                                                                                       ('python','Python (.py)')))

                                                                                       
class ShareObjectForm(forms.Form):
    available = forms.ModelMultipleChoiceField(label='Available collaborators', queryset=UserProfile.objects.filter(user__groups__name__iexact='Testers'), required=False)
    share_with = forms.ModelMultipleChoiceField(queryset=UserProfile.objects.filter(user__groups__name__iexact='Testers'))

        
class DisplayUserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('password','is_active','is_staff','is_superuser','groups','user_permissions','last_login')
    
    def __init__(self, *args, **kwargs):
        super(DisplayUserForm, self).__init__(*args, **kwargs)
        # set fields to read-only
        for key in ['username', 'first_name', 'last_name', 'email', 'date_joined']:
            self.fields[key].widget.attrs['readonly'] = True
    
    def clean_username(self):
        return self.instance.username
    def clean_first_name(self):
        return self.instance.first_name
    def clean_last_name(self):
        return self.instance.last_name
    def clean_email(self):
        return self.instance.email
    def clean_date_joined(self):
        return self.instance.date_joined
    
    
class DisplayUserProfileForm(forms.ModelForm):
    sex = forms.CharField(widget=forms.TextInput(attrs={'readonly':True}))
    class Meta:
        model = UserProfile
        exclude = ('user')
        
    def __init__(self, *args, **kwargs):
        super(DisplayUserProfileForm, self).__init__(*args, **kwargs)
        self.fields['birth_date'].widget.attrs['readonly'] = True
        
    def clean_sex(self):
        return self.instance.sex
    def clean_birth_date(self):
        return self.instance.birth_date
