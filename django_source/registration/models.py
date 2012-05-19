from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class UserProfile(models.Model):
    age        = models.PositiveIntegerField()
    sex        = models.CharField(max_length=1, choices = GENDER_CHOICES)
    user       = models.OneToOneField(User)
        
    def __unicode__(self):
        return self.user.username
