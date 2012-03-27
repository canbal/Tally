from django.db import models
from django.contrib.auth.models import User
import datetime

METHOD_CHOICES = (
                  ('DS','DSIS'  ),
                  ('SQ','SAMVIQ')
)

SEX_CHOICES = ( ('M', 'Male'), ('F', 'Female') )

class Test(models.Model):
    title       = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    method      = models.CharField(max_length=2, choices=METHOD_CHOICES, default='DS')
    create_date = models.DateTimeField('Date created', auto_now_add=True)
    
    def __unicode__(self):
        return self.title
    
    def was_created_today(self):
        return self.create_date == datetime.date.today()
    was_created_today.short_description = 'Created today?'

    
class Subject(models.Model):
    first_name = models.CharField(max_length=200)
    last_name  = models.CharField(max_length=200)
    age        = models.PositiveIntegerField()
    sex        = models.CharField(max_length=1, choices = SEX_CHOICES)
    user       = models.OneToOneField(User)
    
    def __unicode__(self):
        return self.first_name + ' ' + self.last_name
    
    
class TestInstance(models.Model):
    owner       = models.CharField(max_length=200)
    create_time = models.DateTimeField('Date created', auto_now_add=True)
    run_time    = models.DateTimeField('Date run')
    test        = models.ForeignKey(Test)
    path        = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    location    = models.CharField(max_length=200)
    counter     = models.IntegerField(default=0)
    subjects    = models.ManyToManyField(Subject)

    def __unicode__(self):
        return self.owner + ' ' + self.test.title


class Video(models.Model):
    filename    = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    test        = models.ForeignKey(Test)
    
    def __unicode__(self):
        return self.filename
        
        
class TestCase(models.Model):
    is_done       = models.BooleanField(default=0)
    test_instance = models.ForeignKey(TestInstance)
    play_order    = models.PositiveIntegerField()
    video         = models.ManyToManyField(Video, through='TestCaseItem')
    def getTest(self):
        return self.test_instance.test
    def __unicode__(self):
        return '%s : %d' % (unicode(self.test_instance), self.play_order)

class TestCaseItem(models.Model):
    test_case  = models.ForeignKey(TestCase)
    video      = models.ForeignKey(Video)
    play_order = models.PositiveIntegerField()
    class Meta:
        unique_together = ("test_case", "play_order")
    def __unicode__(self):
        return '%s : %d : %s' % (unicode(self.test_case), self.play_order, self.video)
        
class Score(models.Model):
    test_case_item = models.ForeignKey(TestCaseItem)
    subject = models.ForeignKey(Subject)
    value = models.IntegerField()
    def __unicode__(self):
        return '%s : %s : %d' % (unicode(self.test_case_item), unicode(self.subject), self.value)