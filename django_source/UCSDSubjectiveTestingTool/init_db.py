from django.contrib.auth.models import User, Group, Permission
from registration.models import UserProfile
from GenericTest.models import *
import datetime

try:
    testers = Group.objects.get(name='Testers')
except Group.DoesNotExist:
    testers = Group(name='Testers')
    testers.save()
    perm = Permission.objects.get(codename='add_test')
    testers.permissions.add(perm)
    perm = Permission.objects.get(codename='add_testinstance')
    testers.permissions.add(perm)
    perm = Permission.objects.get(codename='add_video')
    testers.permissions.add(perm)
    perm = Permission.objects.get(codename='add_testcase')
    testers.permissions.add(perm)
    perm = Permission.objects.get(codename='add_testcaseinstance')
    testers.permissions.add(perm)
    perm = Permission.objects.get(codename='add_testcaseitem')
    testers.permissions.add(perm)

try:
    tester = User.objects.get(username='tester')
except User.DoesNotExist:
    tester = User.objects.create_user('tester','','1234')
    tester.first_name = 'Tester'
    tester.groups.add(testers)
    tester.save()
    
try:
    tester_profile = UserProfile.objects.get(user=tester)
except UserProfile.DoesNotExist:
    tester_profile = UserProfile(age=0,sex='F',user=tester)
    tester_profile.save()
    

try:
    subjects = Group.objects.get(name='Subjects')
except Group.DoesNotExist:
    subjects = Group(name='Subjects')
    subjects.save()
    perm = Permission.objects.get(codename='add_score')
    subjects.permissions.add(perm)

try:
    subject = User.objects.get(username='subject')
except User.DoesNotExist:
    subject = User.objects.create_user('subject','','1234')
    subject.first_name = 'Subject'
    subject.groups.add(subjects)
    subject.save()
    
try:
    subject_profile = UserProfile.objects.get(user=subject)
except UserProfile.DoesNotExist:
    subject_profile = UserProfile(age=0,sex='M',user=subject)
    subject_profile.save()

try:
    test = Test.objects.get(title='Example Test',description='An example test with single video test cases')
except Test.DoesNotExist:
    test = Test(title='Example Test',description='An example test with single video test cases',method='CU',owner=tester_profile)
    test.save()
    
    
videoList = ['skydiving_largeBlur_blurOne_30.mp4', 'skydiving_largeBlur_inPhase_30.mp4', 'skydiving_largeBlur_outOfPhase_60.mp4', 'skydiving_smallBlur_blurOne_60.mp4']
videoPath = '/Users/canbal/Desktop/test'
for filename in videoList:
    try:
        video = Video.objects.get(test=test,filename=filename)
    except Video.DoesNotExist:
        video = Video(test=test,filename=filename,description=filename)
        video.save()
    
    try:
        test_case_item = TestCaseItem.objects.get(test_case__test=test,video=video)
    except TestCaseItem.DoesNotExist:
        test_case = TestCase(test=test)
        test_case.save()
        test_case_item = TestCaseItem(test_case=test_case,video=video,play_order=0)
        test_case_item.save()        
        
test_instance = test.testinstance_set.create(owner=tester_profile,
                                             path=videoPath,
                                             description='An instance of the example test',
                                             location='UCSD Video Processing Lab')
test_instance.subject.add(subject_profile)
test_instance.save()

play_order = 1
for test_case in test_instance.test.testcase_set.all():
    test_case_instance = TestCaseInstance(test_instance=test_instance,test_case=test_case,play_order=play_order)
    test_case_instance.save()
    play_order = play_order + 1
    