from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from GenericTest.models.main import *
from GenericTest.models.registration import UserProfile
from GenericTest.main.forms import *
import json


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)):
                return True
        return False
    return user_passes_test(in_groups)


def is_enrolled(subject, ti):
    try:
        _ti = subject.subjects_testinstances.get(pk=ti.pk)
    except TestInstance.DoesNotExist:
        return False
    else:
        return True

        
@csrf_exempt
def testme(request):
    if request.method == 'GET':
        return HttpResponse('You successfully sent a GET request!\n')
    elif request.method == 'POST':
        data = request.POST['data']
        print data
        return HttpResponse('You successfully POSTed ' + data + '\n')
    else:
        return HttpResponse('Error: Unknown request method\n')
    
    
@login_required
def index(request):
    try:
    # A user may not have an associated UserProfile - i.e. SuperUser
        subject = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponse('You are not registered as a subject or a tester in the system!')
    else:
        if request.user.groups.filter(name='Testers'):
            return render_to_response('GenericTest/manager/home.html', context_instance=RequestContext(request))
        elif request.user.groups.filter(name='Subjects'):
            latest_test_instances = TestInstance.objects.filter(subjects=subject).order_by('-create_time')
            return render_to_response('GenericTest/main/index.html', {'latest_test_instances': latest_test_instances})
        else:
            return HttpResponse('You are not registered as a subject or a tester in the system!')

        
@login_required
@group_required('Subjects')
def enroll(request):
    subject = UserProfile.objects.get(user=request.user)
    latest_test_instances = TestInstance.objects.exclude(subjects=subject).order_by('-create_time')
    return render_to_response('GenericTest/main/enroll.html', {'latest_test_instances': latest_test_instances})

    
#@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def get_media(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    maxCount = ti.testcaseinstance_set.count()
    errStr = json.dumps({'path':'error', 'videoList':[], 'testDone':True})
    # check bounds of counter
    if ti.counter<0:
        return HttpResponse(errStr)
    elif ti.counter > maxCount:
        return HttpResponse(json.dumps({'path':'', 'videoList':[], 'testDone':True}))
    # get the current test case
    try:
        tci_current = ti.testcaseinstance_set.get(play_order=max(1,ti.counter))     # should exist but check anyway
    except(TestCaseInstance.DoesNotExist):
        return HttpResponse(errStr)
    else:
        # if the current test is done, increment the counter and return the next video or a done signal
        if tci_current.is_done:
            ti.counter += 1
            ti.save()
            if ti.counter > maxCount:
                return HttpResponse(json.dumps({'path':'', 'videoList':[], 'testDone':True}))
            else:
                try:
                    tci_next = ti.testcaseinstance_set.get(play_order=ti.counter)
                except(TestCaseInstance.DoesNotExist):
                    return HttpResponse(errStr)
                else:
                    vidList = []
                    for ii in range(0,tci_next.test_case.testcaseitem_set.count()):
                        vidList.append(tci_next.test_case.testcaseitem_set.get(play_order=ii).video.filename)   # assumes play_order starts from 0
                    return HttpResponse(json.dumps({'path':ti.path, 'videoList':vidList, 'testDone':False}))
        # if this is the first request of the test instance, return the first video and increment the counter
        elif ti.counter==0:
            ti.run_time = datetime.datetime.now()       # set the run_time of the test instance to now
            ti.counter += 1
            ti.save()
            vidList = []
            for ii in range(0,tci_current.test_case.testcaseitem_set.count()):
                vidList.append(tci_current.test_case.testcaseitem_set.get(play_order=ii).video.filename)   # assumes play_order starts from 0
            return HttpResponse(json.dumps({'path':ti.path, 'videoList':vidList, 'testDone':False}))
        # otherwise, the subjects haven't finished scoring- return a wait signal
        else:
            return HttpResponse(json.dumps({'path':'', 'videoList':[], 'testDone':False}))
            
            
@login_required
@group_required('Subjects')
@permission_required('GenericTest.main.add_score')
def tally(request,test_instance_id):
    # get the test instance
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    subject = UserProfile.objects.get(user=request.user)
    if not is_enrolled(subject, ti):
        return HttpResponseRedirect(reverse('GenericTest.registration.views.render_profile'))
    
    choices = [(5,'Imperceptible'), (4,'Perceptible, but not annoying'), (3,'Slightly annoying'), (2,'Annoying'), (1,'Very annoying')]
    # check bounds of the counter (should handle these cases better)
    try:
        tci = ti.testcaseinstance_set.get(play_order=ti.counter)
    except(TestCaseInstance.DoesNotExist):
        return render_to_response('GenericTest/main/status.html', {'test_instance': ti})
    header = 'Test '+str(ti.counter)+'/'+str(ti.testcaseinstance_set.count())
    
    # make sure this subject has not submitted a score for this test case already
    try:
        sc = subject.score_set.get(test_case_instance=tci)
    except(Score.DoesNotExist):
        if request.method == 'GET':
            return render_to_response('GenericTest/main/detail.html',
                                      {'test_instance': ti, 'header': header, 'choices': choices},
                                      context_instance=RequestContext(request))
        else:
            # ensure that one of the choices was selected before submitting the form
            try:
                selection = request.POST['value']
                current_count = int(request.POST['current_count'])
            except KeyError:
                return render_to_response('GenericTest/main/detail.html',
                                          {'test_instance': ti, 'header': header, 'choices': choices,
                                           'error_message': 'Please select a choice.'},
                                          context_instance=RequestContext(request))
            if current_count is ti.counter:
                score = Score(test_case_instance=tci, subjects=subject, value=selection)
                score.save()
                return render_to_response('GenericTest/main/status.html', {'test_instance': ti})
            else:
                return render_to_response('GenericTest/main/detail.html', 
                                          {'test_instance': ti, 'header': header, 'choices': choices},
                                          context_instance=RequestContext(request))
    else:
        return render_to_response('GenericTest/main/status.html',
                                  {'test_instance': ti,
                                   'error_message': 'You already selected a choice for this test!'})


@login_required
@group_required('Subjects')
def status(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    messages = {'0': 'Waiting for other participants. Test will begin shortly...',
                '1': 'Choice is submitted. Waiting for other participants or video to finish...',
                '2': 'Choices of all participants are recorded. Test will proceed shortly...',
                '3': 'Thank you for your participation!',
                '4': 'Get ready to vote.',
                '5': 'Server error'}
    max_counter = ti.testcaseinstance_set.count();
    if ti.counter == 0:
        status = 0 # 0: means test hasn't started yet
        header = 'Welcome'
    elif ti.counter > 0 and ti.counter <= max_counter:
        header = 'Test '+str(ti.counter)+'/'+str(max_counter)
        try:
            tci = ti.testcaseinstance_set.get(play_order=ti.counter)
        except(TestCaseInstance.DoesNotExist):
            status = 5
        else:
            # update status if current subject has not voted yet
            subject = UserProfile.objects.get(user=request.user)
            try:
                sc = subject.score_set.get(test_case_instance=tci)
            except(Score.DoesNotExist):
                status = 4
            else:
                if tci.is_done:
                    status = 2 # 2: means all subjects have voted for current test case
                else:
                    # update status if there exist any subjects who has not voted yet
                    try:
                        for subject in ti.subject.all():
                            sc = subject.score_set.get(test_case_instance=tci)
                    except(Score.DoesNotExist):
                        status = 1
                    else:
                        status = 2 # 2: means all subjects have voted for current test case
                        tci.is_done = True
                        tci.save()
    else:
        status = 3 # 3: means test has finished
        header = 'Test Complete'
    return HttpResponse(json.dumps({'status':status, 'message':messages[str(status)], 'header':header}))

    
@login_required
@group_required('Subjects')
def enroll_to_test_instance(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    try:
    # A user may not have an associated UserProfile - i.e. SuperUser
        subject = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        pass
    else:
        ti.subjects.add(subject)
    return HttpResponseRedirect('/')
    
    
@login_required
@permission_required('GenericTest.main.add_testcaseitem')
def add_test_case_item(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    t  = ti.test
    if request.method == 'POST':
        form = TestCaseItemForm(request.POST)
        form.fields['video'].queryset = Video.objects.filter(test=t)
        if form.is_valid():
            form.save()
            return HttpResponse('Test case item created successfully!')
    else:
        form = TestCaseItemForm()
        form.fields['video'].queryset = Video.objects.filter(test=t)
    return render_to_response('GenericTest/main/add_testcaseitem.html',  {'form': form,  'header': 'Add Test Case Item'},
                              context_instance=RequestContext(request))
                                                        

def reset_test_instance(request, test_instance_id):
    
    # return HTTP 401 forbidden code
    res = HttpResponse("Unauthorized")
    res.status_code = 401
    return res

    # check if request.user is in the tester_desktop group
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse(request.user.first_name)
                # Redirect to a success page.
            else:
                return HttpResponse('disabled account')
                # Return a 'disabled account' error message
        else:
            return HttpResponse('invalid login')
            # Return an 'invalid login' error message.
    return HttpResponse(request.COOKIES)


    # if request.user.groups.filter(name='Testers'):
        # ti = get_object_or_404(TestInstance, pk=test_instance_id)
        # # reset test instance
        # ti.counter = 0
        # ti.save()
        # tci = TestCaseInstance.objects.filter(test_instance=ti)
        # for t in tci:
            # t.is_done = False
            # t.save()
            # scores = Score.objects.filter(test_case_instance=t)
            # for s in scores:
                # s.delete()
        # # return HttpResponse("Test Instance " + test_instance_id + " has been reset.")
        # # send list of all videos so desktop app can verify that they exist
        # vid = Video.objects.filter(test=ti.test)
        # vidList = []
        # for v in vid:
            # vidList.append(v.filename)
        # return HttpResponse(json.dumps({'path':ti.path, 'videoList':vidList}))
    # else:
        # # return HTTP 401
        # return HttpResponse(json.dumps({'path':'nope'}))