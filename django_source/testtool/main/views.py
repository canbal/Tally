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
from testtool.manager.views import is_test_instance_active
import json


########################################################################################################
################################            SUBJECT FUNCTIONS           ################################
########################################################################################################
def is_enrolled(subject, ti):
    return subject in ti.subjects.all()
        

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
            latest_test_instances = TestInstance.objects.filter(subjects=subject)
            ti_list = []#latest_test_instances
            for ti in latest_test_instances:
                if is_test_instance_active(ti):
                    ti_list.append(ti)
            return render_to_response('testtool/main/index.html', {'ti_list': ti_list})
        else:
            return HttpResponse('You are not registered as a subject or a tester in the system!')
            
            
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
@group_required('Testers')
def mirror_score(request, test_instance_id):
    if request.is_ajax():
        try:
            ti = TestInstance.objects.get(pk=test_instance_id)
        except:
            return HttpResponse(json.dumps({'score':'E1'}))
        if ti.subjects.count() == 1:
            up = ti.subjects.all()[0];
            try:
                score = ScoreSSCQE.objects.filter(subject=up).latest('pk')
                return HttpResponse(json.dumps({'score':str(score.value)}))
            except:
                return HttpResponse(json.dumps({'score':'0'}))
        else:
            return HttpResponse(json.dumps({'score':'E2'}))
    else:
        ti = get_object_or_404(TestInstance, pk=test_instance_id)
        return render_to_response('testtool/last_score.html', {'test_instance': ti.pk})
            
            
########################################################################################################
################################         DESKTOP APP FUNCTIONS          ################################
########################################################################################################
@csrf_exempt
def init_test_instance(request, test_instance_id):
    # send list of all videos so desktop app can verify that they exist
    if request.method == 'POST':
        try:
            key = request.POST['key']
        except KeyError:
            errMsg = 'Must include key parameter.'
        else:
            try:
                ti = TestInstance.objects.get(pk=test_instance_id)
            except TestInstance.DoesNotExist:
                errMsg = 'Test instance does not exist.'
            else:
                if is_test_instance_active(ti):            
                    if key == ti.key:
                        vid = Video.objects.filter(test=ti.test)
                        vidList = []
                        for v in vid:
                            vidList.append(v.filename)
                        return HttpResponse(json.dumps({'status': 'valid', 'msg': '', 'path':ti.path, 'videoList':vidList}))
                    else:
                        errMsg = 'Invalid key.'
                else:
                    errMsg = 'This test instance is not active.'
    else:
        errMsg = 'Only POST requests accepted.'
    return HttpResponse(json.dumps({'status': 'error', 'msg': 'init_test_instance: ' + errMsg, 'path': '', 'videoList': []}))


@csrf_exempt
def get_media(request, test_instance_id):
    if request.method == 'POST':
        try:
            key = request.POST['key']
        except KeyError:
            return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Must include key parameter.', 'path': '', 'videoList':[]}))
        else:
            try:
                ti = TestInstance.objects.get(pk=test_instance_id)
            except TestInstance.DoesNotExist:
                return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Test instance does not exist.', 'path': '', 'videoList':[]}))
            if is_test_instance_active(ti):            
                if key == ti.key:
                    maxCount = ti.testcaseinstance_set.count()
                    # get POST data from request
                    try:
                        status = request.POST['status']
                    except KeyError:
                        return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Must send status.', 'path': '', 'videoList':[]}))
                    # check bounds of counter
                    if ti.counter<0:
                        return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Error with test instance: counter < 0.', 'path': '', 'videoList':[]}))
                    elif ti.counter > maxCount:
                        return HttpResponse(json.dumps({'status': 'done', 'msg': '', 'path': '', 'videoList':[]}))
                    # get the current test case
                    try:
                        tci_current = ti.testcaseinstance_set.get(play_order=max(1,ti.counter))
                    except TestCaseInstance.DoesNotExist:
                        return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Could not find test case instance.', 'path': '', 'videoList':[]}))
                    else:
                        if status == 'media_done':
                            tci_current.is_media_done = True
                            tci_current.save()
                        if status == 'test_case_done':
                            tci_current.is_media_done = True
                            tci_current.is_done = True
                            tci_current.save()
                        if tci_current.is_done:     # if the current test case is done, increment the counter and return the next video or a done signal
                            ti.counter += 1
                            ti.save()
                            if ti.counter > maxCount:
                                return HttpResponse(json.dumps({'status': 'done', 'msg': '', 'path': '', 'videoList':[]}))
                            else:
                                try:
                                    tci_next = ti.testcaseinstance_set.get(play_order=ti.counter)
                                except TestCaseInstance.DoesNotExist:
                                    return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Could not find test case instance.', 'path': '', 'videoList':[]}))
                                else:
                                    vidList = []
                                    for ii in range(0,tci_next.test_case.testcaseitem_set.count()):
                                        vidList.append(tci_next.test_case.testcaseitem_set.get(play_order=ii).video.filename)   # assumes play_order starts from 0
                                    return HttpResponse(json.dumps({'status': 'run', 'msg': '', 'path':ti.path, 'videoList':vidList}))
                        elif ti.counter==0:     # if this is the first request of the test instance, return the first video and increment the counter
                            ti.run_time = datetime.datetime.now()       # set the run_time of the test instance to now
                            ti.counter += 1
                            ti.save()
                            vidList = []
                            for ii in range(0,tci_current.test_case.testcaseitem_set.count()):
                                vidList.append(tci_current.test_case.testcaseitem_set.get(play_order=ii).video.filename)   # assumes play_order starts from 0
                            return HttpResponse(json.dumps({'status': 'start', 'msg': '', 'path':ti.path, 'videoList':vidList}))
                        # otherwise, the subjects haven't finished scoring- return a wait signal
                        else:
                            return HttpResponse(json.dumps({'status': 'wait', 'msg': '', 'path': '', 'videoList': []}))
                else:
                    return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Invalid key.', 'path': '', 'videoList':[]}))
            else:
                return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: This test instance is not active.', 'path': '', 'videoList':[]}))
    else:
        return HttpResponse(json.dumps({'status': 'error', 'msg': 'get_media: Only POST requests accepted.', 'path': '', 'videoList':[]}))
        
        
########################################################################################################
################################            UNUSED FUNCTIONS            ################################
########################################################################################################
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
@group_required('Subjects')
def enroll(request):
    #subject = request.user.get_profile()
    #latest_test_instances = TestInstance.objects.exclude(subjects=subject).order_by('-create_time')
    #return render_to_response('testtool/main/enroll.html', {'latest_test_instances': latest_test_instances})
    return HttpResponseRedirect('/')

        
@login_required
@group_required('Subjects')
def enroll_to_test_instance(request, test_instance_id):
    # ti = get_object_or_404(TestInstance, pk=test_instance_id)
    # try:
    # A user may not have an associated UserProfile - i.e. SuperUser
        # subject = request.user.get_profile()
    # except UserProfile.DoesNotExist:
        # pass
    # else:
        # ti.subjects.add(subject)
    return HttpResponseRedirect('/')
    
    
@login_required
@permission_required('testtool.main.add_testcaseitem')
def add_test_case_item(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    t = ti.test
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