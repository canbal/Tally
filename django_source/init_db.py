from django.contrib.auth.models import User, Group, Permission
from testtool.models import *
import datetime, random, sys

# setup database for the Testers group
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

# create a sample tester profile
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
    tester_profile = UserProfile(birth_date='2000-01-01',sex='F',user=tester)
    tester_profile.save()
    
# setup the database for the Subjects group
try:
    subjects = Group.objects.get(name='Subjects')
except Group.DoesNotExist:
    subjects = Group(name='Subjects')
    subjects.save()
    perm = Permission.objects.get(codename='add_scoredsis')
    subjects.permissions.add(perm)

# create a sample subject profile
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
    subject_profile = UserProfile(birth_date='2000-01-01',sex='M',user=subject)
    subject_profile.save()

# create a sample DSIS test
try:
    test = Test.objects.get(pk=1,title='Example Test',description='An example test with single video test cases')
except Test.DoesNotExist:
    try:
        test = Test.objects.get(pk=1)
    except Test.DoesNotExist:
        test = Test.objects.create(title='Example Test',description='An example test with single video test cases',method='DSIS',owner=tester_profile)
    else:
        sys.exit(0) # stop execution if there is already a test in the database other than the sample one
        
videoList  = [('skydiving_largeBlur_blurOne_30.mp4',    'skydiving_largeBlur_inPhase_30.mp4'),
              ('skydiving_largeBlur_outOfPhase_60.mp4', 'skydiving_smallBlur_blurOne_60.mp4')]
videoPath = 'd:/binocsupp/skydiving'
for files in videoList:
    # initiate an empty test case for each tuple
    test_case = TestCase.objects.create(test=test)

    # generate play order
    for ii in range(0,2): # repeat each video twice
        rand_order = range(0,len(files)) # TODO: check consistency of start value of play_order (TestCaseItem and TestCase)
        random.shuffle(rand_order)

        # get or create reference video
        filename = files[0]
        try:
            video = Video.objects.get(test=test,filename=filename)
        except Video.DoesNotExist:
            video = Video.objects.create(test=test,filename=filename,description=filename)

        # add to the test case
        play_order = rand_order[0] + ii*len(files)
        TestCaseItem.objects.create(test_case=test_case,video=video,play_order=play_order,is_reference=True)

        for idv in range(1,len(files)):
            # first video is reference, get or create the video to be tested
            filename = files[idv]
            try:
                video = Video.objects.get(test=test,filename=filename)
            except Video.DoesNotExist:
                video = Video.objects.create(test=test,filename=filename,description=filename)

            # add to the test case
            play_order = rand_order[idv] + ii*len(files)
            TestCaseItem.objects.create(test_case=test_case,video=video,play_order=play_order)

# delete all existing test instances that belong to the sample test
for ti in TestInstance.objects.all():
    ti.delete()

# create a test instance    
test_instance = test.testinstance_set.create(owner=tester_profile,
                                             path=videoPath,
                                             description='An instance of the example test',
                                             location='UCSD Video Processing Lab')
test_instance.subjects.add(subject_profile)
test_instance.save()

# no randomization, test cases are played sequentially
play_order = 1
for test_case in test_instance.test.testcase_set.all():
    test_case_instance = TestCaseInstance(test_instance=test_instance,test_case=test_case,play_order=play_order)
    test_case_instance.save()
    play_order += 1
    