from django.db import models
import datetime

METHOD_CHOICES = (
                  ('DS','DSIS'  ),
                  ('SQ','SAMVIQ')
)

SEX_CHOICES = ( ('M', 'male'), ('F', 'female') )

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

    
class TestInstance(models.Model):
    owner       = models.CharField(max_length=200)
    create_time = models.DateTimeField('Date created', auto_now_add=True)
    run_time    = models.DateTimeField('Date run')
    test        = models.ForeignKey(Test)
    path        = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    location    = models.CharField(max_length=200)
    counter     = models.IntegerField(default=0)

    def __unicode__(self):
        return self.owner + self.test.title


class Video(models.Model):
    filename    = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    test        = models.ForeignKey(Test)
    
    def __unicode__(self):
        return self.filename

        
class Subject(models.Model):
    first_name = models.CharField(max_length=200)
    last_name  = models.CharField(max_length=200)
    age        = models.PositiveIntegerField()
    sex        = models.CharField(max_length=1, choices = SEX_CHOICES)
    
    def __unicode__(self):
        return self.first_name + self.last_name

        
class TestCase(models.Model):
    is_done       = models.BooleanField(default=0)
    test_instance = models.ForeignKey(TestInstance)
    play_order    = models.PositiveIntegerField()
    #video = models.ManyToManyField(Video,limit_choices_to=Video.objects.filter(test=lambda self.test_instance.test))
    video         = models.ManyToManyField(Video)
    # handle play order of videos within test case
    def getTest(self):
        return self.test_instance.test
    def __unicode__(self):
        return '%s : %d : %s' % (unicode(self.test_instance), self.play_order, self.video.all()[0].filename)

        
class Score(models.Model):
    test_case = models.ForeignKey(TestCase)
    subject = models.ForeignKey(Subject)
    value = models.IntegerField()
    def __unicode__(self):
        return '%s : %s : %d' % (unicode(self.test_case), unicode(self.subject), self.value)