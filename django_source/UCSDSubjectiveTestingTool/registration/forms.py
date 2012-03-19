from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
 
class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name  = forms.CharField(max_length=30, label='Last Name')
    email = forms.EmailField(label="E-Mail")
 
    class Meta:
        model = User
        fields = ("username", "email", )
        
    def clean_email(self):
        email = self.cleaned_data["email"]
 
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
 
        raise forms.ValidationError("A user with that email address already exists.")