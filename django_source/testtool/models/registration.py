from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class UserProfile(models.Model):
    birth_date = models.DateField()
    sex        = models.CharField(max_length=1, choices = GENDER_CHOICES)
    user       = models.OneToOneField(User)
        
    class Meta:
        app_label = 'testtool'
    def __unicode__(self):
        return self.user.username
