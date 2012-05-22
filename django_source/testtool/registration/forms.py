from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget
from testtool.models import UserProfile
import datetime

now = datetime.datetime.now()

class UserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(label='Date of birth', widget=SelectDateWidget(years=range(now.year,1940,-1)))
    class Meta:
        model = UserProfile
        exclude = ('user',)
        
class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='First name', max_length=30)
    last_name  = forms.CharField(label='Last name', max_length=30)
    email      = forms.EmailField(label='E-Mail')
 
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        
    def clean_email(self):
        email = self.cleaned_data['email']
 
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
 
        raise forms.ValidationError('A user with that email address already exists.')