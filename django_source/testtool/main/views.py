from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from testtool.models import *
from testtool.main.forms import *
from testtool.decorators import group_required
from testtool.test_modes.views import tally_continuous, tally_discrete, status_continuous, status_discrete
import json


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
        subject = request.user.get_profile()
    except UserProfile.DoesNotExist:
        return HttpResponse('You are not registered as a subject or a tester in the system!')
    else:
        if request.user.groups.filter(name='Testers'):
            return render_to_response('testtool/manager/home.html', context_instance=RequestContext(request))
        elif request.user.groups.filter(name='Subjects'):
            latest_test_instances = TestInstance.objects.filter(subjects=subject).order_by('-create_time')
            return render_to_response('testtool/main/index.html', {'latest_test_instances': latest_test_instances})
        else:
            return HttpResponse('You are not registered as a subject or a tester in the system!')

        
@login_required
@group_required('Subjects')
def enroll(request):
    subject = request.user.get_profile()
    latest_test_instances = TestInstance.objects.exclude(subjects=subject).order_by('-create_time')
    return render_to_response('testtool/main/enroll.html', {'latest_test_instances': latest_test_instances})

    
@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def get_media(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    if request.method == 'POST':
        maxCount = ti.testcaseinstance_set.count()
        errStr = json.dumps({'path':'error', 'videoList':[], 'testDone':True})
        # get POST data from request
        try:
            status = request.POST['status']
        except KeyError:
            return HttpResponse('Invalid POST data.')
        # check bounds of counter
        if ti.counter<0:
            return HttpResponse(errStr)
        elif ti.counter > maxCount:
            return HttpResponse(json.dumps({'path':'', 'videoList':[], 'testDone':True}))
        # get the current test case
        try:
            tci_current = ti.testcaseinstance_set.get(play_order=max(1,ti.counter))     # should exist but check anyway
        except TestCaseInstance.DoesNotExist:
            return HttpResponse(errStr)
        else:
            if status == 'media_done':
                tci_current.is_media_done = True
                tci_current.save()
            # if the current test is done, increment the counter and return the next video or a done signal
            if tci_current.is_done:
                ti.counter += 1
                ti.save()
                if ti.counter > maxCount:
                    return HttpResponse(json.dumps({'path':'', 'videoList':[], 'testDone':True}))
                else:
                    try:
                        tci_next = ti.testcaseinstance_set.get(play_order=ti.counter)
                    except TestCaseInstance.DoesNotExist:
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
    else:
        return HttpResponse('Only POST requests accepted')
            
            
@login_required
@group_required('Subjects')
def tally(request,test_instance_id):
    # get the test instance
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    subject = request.user.get_profile()
    if not is_enrolled(subject, ti):
        return HttpResponseRedirect(reverse('testtool.registration.views.render_profile'))
    method_dict = dict(METHOD_CHOICES)
    if ti.test.method in [x[0] for x in method_dict['Continuous']]:
        return tally_continuous(request, ti, subject)
    elif ti.test.method in [x[0] for x in method_dict['Discrete']]:
        return tally_discrete(request, ti, subject)
    else:
        raise Exception('Test mode must be "Continuous" or "Discrete"')


@login_required
@group_required('Subjects')
def status(request, test_instance_id):
    if request.is_ajax():
        try:
            ti = TestInstance.objects.get(pk=test_instance_id)
        except:
            ti = []
        max_counter = ti.testcaseinstance_set.count()
        method_dict = dict(METHOD_CHOICES)
        if ti.test.method in [x[0] for x in method_dict['Continuous']]:
            return status_continuous(request, ti, max_counter)
        elif ti.test.method in [x[0] for x in method_dict['Discrete']]:
            return status_discrete(request, ti, max_counter)
        else:
            raise Exception('Test mode must be "Continuous" or "Discrete"')
    else:
        ti = get_object_or_404(TestInstance, pk=test_instance_id)
        return render_to_response('testtool/main/status.html', {'test_instance': ti})
    
    
@login_required
@group_required('Subjects')
def enroll_to_test_instance(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    try:
    # A user may not have an associated UserProfile - i.e. SuperUser
        subject = request.user.get_profile()
    except UserProfile.DoesNotExist:
        pass
    else:
        ti.subjects.add(subject)
    return HttpResponseRedirect('/')
    
    
@login_required
@permission_required('testtool.main.add_testcaseitem')
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
    return render_to_response('testtool/main/add_testcaseitem.html',  {'form': form,  'header': 'Add Test Case Item'},
                              context_instance=RequestContext(request))
                                                        

def reset_test_instance(request, test_instance_id):
    # reset test instance
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    ti.counter = 0
    ti.save()
    tci = TestCaseInstance.objects.filter(test_instance=ti)
    for t in tci:
        t.is_done = False
        t.is_media_done = False
        t.save()
        if ti.test.method == 'SSCQE':
            scores = ScoreSSCQE.objects.filter(test_case_instance=t)
        elif ti.test.method == 'DSIS' or ti.test.method == 'CUSTOM':
            scores = ScoreDSIS.objects.filter(test_case_instance=t)
        elif ti.test.method == 'DSCQS':
            scores = ScoreDSCQS.objects.filter(test_case_instance=t)
        else:
            raise Exception('Invalid test method.')
        for s in scores:
            s.delete()
    # return HttpResponse("Test Instance " + test_instance_id + " has been reset.")
    # send list of all videos so desktop app can verify that they exist
    vid = Video.objects.filter(test=ti.test)
    vidList = []
    for v in vid:
        vidList.append(v.filename)
    return HttpResponse(json.dumps({'path':ti.path, 'videoList':vidList}))

    
    # # return HTTP 401 forbidden code
    # res = HttpResponse("Unauthorized")
    # res.status_code = 401
    # return res

    # # check if request.user is in the tester_desktop group
    # if request.method=='POST':
        # username = request.POST['username']
        # password = request.POST['password']
        # user = authenticate(username=username, password=password)
        # if user is not None:
            # if user.is_active:
                # login(request, user)
                # return HttpResponse(request.user.first_name)
                # # Redirect to a success page.
            # else:
                # return HttpResponse('disabled account')
                # # Return a 'disabled account' error message
        # else:
            # return HttpResponse('invalid login')
            # # Return an 'invalid login' error message.
    # return HttpResponse(request.COOKIES)


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