from django.db import models
from testtool.models.registration import UserProfile
import datetime

METHOD_CHOICES = (
    ('Continuous', (
            ('SSCQE', 'SSCQE'),
        )
    ),
    ('Discrete', (
            ('DSIS', 'DSIS'),
            ('DSCQS', 'DCSQS'),
        )
    ),
)

ACTION_CHOICES = (
    ('joined', 'joined'),
    ('created', 'created'),
    ('edited', 'edited'),
    ('ran', 'ran'),
    ('shared', 'shared'),
    ('unshared', 'unshared'),
    ('deleted', 'deleted'),
)

OBJECT_CHOICES = (
    ('Tally', 'Tally'),
    ('Test', 'Test'),
    ('Test Instance', 'Test Instance'),
)

class Test(models.Model):
    owner         = models.ForeignKey(UserProfile, related_name='owner_tests')
    collaborators = models.ManyToManyField(UserProfile, related_name='collaborators_tests', null=True, blank=True)
    title         = models.CharField(max_length=200, unique=True)
    description   = models.TextField(blank=True)
    method        = models.CharField(max_length=10, choices=METHOD_CHOICES, default='DSIS')
    create_time   = models.DateTimeField('Date created', auto_now_add=True)
    
    class Meta:
        app_label = 'testtool'
    def __unicode__(self):
        return self.title
    def has_data(self):
        ti_set = TestInstance.objects.filter(test=self)
        for ti in ti_set:
            if ti.has_data():
                return True
        return False
    
    
class TestInstance(models.Model):
    test           = models.ForeignKey(Test)
    owner          = models.ForeignKey(UserProfile, related_name='owner_testinstances')
    collaborators  = models.ManyToManyField(UserProfile, related_name='collaborators_testinstances', null=True, blank=True)
    subjects       = models.ManyToManyField(UserProfile, related_name='subjects_testinstances', null=True, blank=True)
    create_time    = models.DateTimeField('Date created', auto_now_add=True)
    schedule_time  = models.DateTimeField('Date scheduled', null=True)
    run_time       = models.DateTimeField('Date run', null=True, blank=True)
    path           = models.CharField(max_length=200)
    description    = models.TextField(blank=True)
    location       = models.CharField(max_length=200)
    counter        = models.IntegerField(default=0)
    key            = models.CharField(max_length=20)
    
    class Meta:
        app_label = 'testtool'
    def __unicode__(self):
        return '%d : %s : %s' % (self.pk, self.owner.user.username, self.test.title)
    def get_status(self):
        if self.subjects.count()==0:
            return 'Invalid - no subjects'
        counter = self.counter
        max_count = self.testcaseinstance_set.count()
        if max_count == 0:
            return 'Invalid - no test cases'
        run_time = self.run_time
        if run_time is None and counter==0:
            return 'Ready to run'
        elif run_time is not None and counter > max_count:
            return 'Complete'
        elif run_time is not None and counter > 0 and counter <= max_count:
            return 'Incomplete'
        else:
            return 'Error'
    def is_active(self):
        return self.get_status() in ['Ready to run', 'Incomplete']
    def has_data(self):
        return self.get_status() in ['Complete', 'Incomplete']

        
class Video(models.Model):
    test        = models.ForeignKey(Test)
    filename    = models.CharField(max_length=200)
    file        = models.FileField(upload_to='videos/%Y/%m/%d', null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        app_label = 'testtool'
        unique_together = ('test','filename')
    def __unicode__(self):
        return self.filename
    

class TestCase(models.Model):
    test   = models.ForeignKey(Test)
    videos = models.ManyToManyField(Video, through='TestCaseItem')
    
    class Meta:
        app_label = 'testtool'
    def __unicode__(self):
        return '%s : %d' % (self.test.title, self.pk)
    

class TestCaseInstance(models.Model):
    test_instance = models.ForeignKey(TestInstance)
    test_case     = models.ForeignKey(TestCase)
    is_done       = models.BooleanField(default=False)
    is_media_done = models.BooleanField(default=False)
    play_order    = models.PositiveIntegerField()
    
    class Meta:
        app_label = 'testtool'
        unique_together = ('test_instance', 'play_order')
    def __unicode__(self):
        return '%s : %d' % (str(self.test_instance), self.play_order)

        
class TestCaseItem(models.Model):
    test_case    = models.ForeignKey(TestCase)
    video        = models.ForeignKey(Video)
    play_order   = models.PositiveIntegerField()
    is_reference = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'testtool'
        unique_together = ('test_case', 'play_order')
    def __unicode__(self):
        return '%s : %d : %s' % (unicode(self.test_case), self.play_order, self.video)

        
class LogEntry(models.Model):
    actor     = models.ForeignKey(UserProfile, related_name='actor_logentries')
    action    = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object    = models.CharField(max_length=20, choices=OBJECT_CHOICES)
    message   = models.TextField()
    timestamp = models.DateTimeField(null=True)
    tags      = models.ManyToManyField(UserProfile, through='LogTag', null=True, blank=True)
    
    class Meta:
        app_label = 'testtool'
        verbose_name_plural = 'Log entries'
    def __unicode__(self):
        return '%s : %s' % (unicode(self.actor.user.username), self.action)
        
        
class LogTag(models.Model):
    log_entry = models.ForeignKey(LogEntry)
    user      = models.ForeignKey(UserProfile)
    viewed    = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'testtool'
    def __unicode__(self):
        return '%s: viewed = %s' % (unicode(self.user.user.username), self.viewed)