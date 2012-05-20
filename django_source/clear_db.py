from django.contrib.auth.models import User, Group
from testtool.models import *

try:
    tester = User.objects.get(username='tester')
except User.DoesNotExist:
    pass
else:
    try:
        tester_profile = UserProfile.objects.get(user=tester)
    except UserProfile.DoesNotExist:
        pass
    else:
        tester_profile.delete()
    tester.delete()

try:
    testers = Group.objects.get(name='Testers')
except Group.DoesNotExist:
    pass
else:
    testers.delete()

try:
    subject = User.objects.get(username='subject')
except User.DoesNotExist:
    pass
else:
    try:
        subject_profile = UserProfile.objects.get(user=subject)
    except UserProfile.DoesNotExist:
        pass
    else:
        subject_profile.delete()
    subject.delete()

try:
    subjects = Group.objects.get(name='Subjects')
except Group.DoesNotExist:
    pass
else:
    subjects.delete()


tests = Test.objects.filter(title='Example Test')
for t in tests:
    test_instances = TestInstance.objects.filter(test=t)
    for ti in test_instances:
        ti.delete()
    t.delete()