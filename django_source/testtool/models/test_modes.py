from django.db import models
from testtool.models.main import TestCaseInstance
from testtool.models.registration import UserProfile


class Score(models.Model):
    test_case_instance = models.ForeignKey(TestCaseInstance)
    subject            = models.ForeignKey(UserProfile)
    
    class Meta:
        app_label = 'testtool'
        abstract = True
        
        
class ScoreSSCQE(Score):
    value     = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s : %s : %5.2f' % (str(self.test_case_instance), str(self.subject), self.value)
        
        
class ScoreDSIS(Score):
    value = models.IntegerField()
    
    def __unicode__(self):
        return '%s : %s : %d' % (str(self.test_case_instance), str(self.subject), self.value)
        
        
class ScoreDSCQS(Score):
    value1 = models.DecimalField(max_digits=3, decimal_places=2)
    value2 = models.DecimalField(max_digits=3, decimal_places=2)
    
    def __unicode__(self):
        return '%s : %s : %4.2f %4.2f' % (str(self.test_case_instance), str(self.subject), self.value1, self.value2)
