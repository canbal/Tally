from django.contrib.auth.models import Group

# setup database for the Testers group
try:
    testers = Group.objects.get(name='Testers')
except Group.DoesNotExist:
    testers = Group(name='Testers')
    testers.save()
    
# setup the database for the Subjects group
try:
    subjects = Group.objects.get(name='Subjects')
except Group.DoesNotExist:
    subjects = Group(name='Subjects')
    subjects.save()


