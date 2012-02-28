from django.db import models
import datetime

METHOD_CHOICES = (
                  ('DS','DSIS'  ),
                  ('SQ','SAMVIQ')
)
    
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
    
class Video(models.Model):
    filename    = models.CharField(max_length=200)
    description = models.CharField(max_length=400)
    test        = models.ManyToManyField(Test)
    
    def __unicode__(self):
        return self.filename
    
class TestCase(models.Model):
    play_order  = models.PositiveIntegerField()
    is_done     = models.BooleanField(default=0)
    test        = models.ForeignKey(Test)
    video       = models.ForeignKey(Video)
        
    def __unicode__(self):
        return self.video.filename