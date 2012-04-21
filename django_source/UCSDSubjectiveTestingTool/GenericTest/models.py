from django.db import models
from registration.models import UserProfile
import datetime

METHOD_CHOICES = (
    ('DS','DSIS'),
    ('SQ','SAMVIQ'),
    ('CU','CUSTOM')
)

class Test(models.Model):
    title       = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    method      = models.CharField(max_length=2, choices=METHOD_CHOICES, default='DS')
    create_time = models.DateTimeField('Date created', auto_now_add=True)
    
    def __unicode__(self):
        return self.title
    def was_created_today(self):
        return self.create_time == datetime.date.today()
        was_created_today.short_description = 'Created today?'
    
    
class TestInstance(models.Model):
    test          = models.ForeignKey(Test)
    owner         = models.ForeignKey(UserProfile, related_name='testinstance_owner')
    subject       = models.ManyToManyField(UserProfile, related_name='testinstance_subjects', null=True)
    create_time   = models.DateTimeField('Date created', auto_now_add=True)
    schedule_time = models.DateTimeField('Date scheduled', null=True)
    run_time      = models.DateTimeField('Date run', null=True)
    path          = models.CharField(max_length=200)
    description   = models.CharField(max_length=400)
    location      = models.CharField(max_length=200)
    counter       = models.IntegerField(default=0)
    
    def __unicode__(self):
        return str(self.id) + ' : ' + self.owner.user.username + ' : ' + self.test.title


class Video(models.Model):
    test        = models.ForeignKey(Test)
    filename    = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    
    def __unicode__(self):
        return self.filename
    
    class Meta:
        unique_together = ('test','filename')


class TestCase(models.Model):
    test  = models.ForeignKey(Test)
    video = models.ManyToManyField(Video, through='TestCaseItem')
    
    def __unicode__(self):
        return '%s : %d' % (str(self.test.title), self.pk)
    def getTest(self):
        return self.test
    

class TestCaseInstance(models.Model):
    test_instance = models.ForeignKey(TestInstance)
    test_case     = models.ForeignKey(TestCase)
    is_done       = models.BooleanField(default=0)
    play_order    = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ('test_instance', 'play_order')
    def __unicode__(self):
        return '%s : %d' % (str(self.test_instance), self.play_order)

        
class TestCaseItem(models.Model):
    test_case    = models.ForeignKey(TestCase)
    video        = models.ForeignKey(Video)
    play_order   = models.PositiveIntegerField()
    is_reference = models.BooleanField(default=0)
    
    class Meta:
        unique_together = ('test_case', 'play_order')
    def __unicode__(self):
        return '%s : %d : %s' % (unicode(self.test_case), self.play_order, self.video)
        
        
class Score(models.Model):
    test_case_instance = models.ForeignKey(TestCaseInstance)
    subject            = models.ForeignKey(UserProfile)
    value              = models.IntegerField()

    def __unicode__(self):
        return '%s : %s : %d' % (str(self.test_case_instance), str(self.subject), self.value)