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
@login_required
def index(request):
    """
    View:     Renders homepage for subjects when they log in.
    Template: `testtool/main/index.html`
    """
    try:            # user may not have an associated UserProfile - i.e. SuperUser
        subject = request.user.get_profile()
    except UserProfile.DoesNotExist:
        return HttpResponse('You are not registered as a subject or a tester in the system!')
    if request.user.groups.filter(name='Testers'):
        return render_to_response('testtool/manager/home.html', context_instance=RequestContext(request))
    if request.user.groups.filter(name='Subjects'):
        latest_test_instances = TestInstance.objects.filter(subjects=subject)
        ti_list = []#latest_test_instances
        for ti in latest_test_instances:
            if is_test_instance_active(ti):
                ti_list.append(ti)
        return render_to_response('testtool/main/index.html', {'ti_list': ti_list})
    return HttpResponse('You are not registered as a subject or a tester in the system!')
    
    
@login_required
@group_required('Subjects')
def tally(request,test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    subject = request.user.get_profile()
    if subject not in ti.subjects.all():
        return HttpResponseRedirect(reverse('testtool.registration.views.render_profile'))
    if ti.test.method in method_list('Continuous'):
        return tally_continuous(request, ti, subject)
    elif ti.test.method in method_list('Discrete'):
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
            return status_continuous(request, [], max_counter)      # will return error code
        max_counter = ti.testcaseinstance_set.count()
        if ti.test.method in method_list('Continuous'):
            return status_continuous(request, ti, max_counter)
        elif ti.test.method in method_list('Discrete'):
            return status_discrete(request, ti, max_counter)
        raise Exception('Test mode must be "Continuous" or "Discrete"')
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    return render_to_response('testtool/main/status.html', {'test_instance': ti})
            
            
def method_list(mode):
    method_dict = dict(METHOD_CHOICES)
    return [x[0] for x in method_dict[mode]]
    
    
    
########################################################################################################
################################         DESKTOP APP FUNCTIONS          ################################
########################################################################################################
@csrf_exempt
def init_test_instance(request, test_instance_id):
    checks = validate_request_and_ti(request,test_instance_id)
    ti = checks['ti']
    if not checks['success']:
        return init_signal(ti,'error',checks['msg'])
    # if all checks are successful, send list of all videos so desktop app can verify that they exist    
    mediaList = list(Video.objects.filter(test=ti.test).values_list('filename',flat=True))
    return init_signal(ti,'valid','',mediaList)

    
@csrf_exempt
def get_media(request, test_instance_id):
    checks = validate_request_and_ti(request,test_instance_id)
    ti = checks['ti']
    if not checks['success']:
        return media_signal(ti,'error',checks['msg'])
    try:
        status = request.POST['status']
    except KeyError:
        return media_signal(ti,'error','Must include "status" parameter.')
    # if all checks are successful, process the signal
    maxCount = ti.testcaseinstance_set.count()
    if ti.counter < 0:                  # check bounds of counter
        return media_signal(ti,'error','Error with test instance: counter < 0.')
    elif ti.counter > maxCount:
        return media_signal(ti,'done')
    try:                                # get the current test case
        tci_current = ti.testcaseinstance_set.get(play_order=max(1,ti.counter))
    except TestCaseInstance.DoesNotExist:
        return media_signal(ti,'error','Could not find test case instance.')
    if status == 'media_done':
        tci_current.is_media_done = True
        tci_current.save()
    if status == 'test_case_done':
        tci_current.is_media_done = True
        tci_current.is_done = True
        tci_current.save()
    if tci_current.is_done:             # if current test case is done, increment counter and return next video or done signal
        ti.counter += 1
        ti.save()
        if ti.counter > maxCount:
            return media_signal(ti,'done')
        try:
            tci_next = ti.testcaseinstance_set.get(play_order=ti.counter)
        except TestCaseInstance.DoesNotExist:
            return media_signal(ti,'error','Could not find test case instance.')
        return media_signal(ti,'run','',getMediaList(tci_next))
    elif ti.counter==0:                 # if this is the first request, return first video and increment counter
        ti.run_time = datetime.datetime.now()       # set the run_time of the test instance to now
        ti.counter += 1
        ti.save()
        return media_signal(ti,'run','',getMediaList(tci_current))
    return media_signal(ti,'wait')      # otherwise, the subjects haven't finished scoring- return a wait signal
        

def validate_request_and_ti(request,ti_pk):
    # check that request is a POST and contains 'key' parameter; check that test instance exists, is active, and POST key is correct
    success = False
    ti = 0
    msg = ''
    if not request.method == 'POST':
        msg = 'Only POST requests accepted.'
    else:
        try:
            key = request.POST['key']
        except KeyError:
            msg = 'Must include "key" parameter.'
        else:
            try:
                ti = TestInstance.objects.get(pk=ti_pk)
            except TestInstance.DoesNotExist:
                msg = 'Test instance does not exist.'
            else:
                if not is_test_instance_active(ti):
                    msg = 'This test instance is not active.'
                elif not key == ti.key:
                    msg = 'Invalid key.'
                else:                       # if checks pass, return the test instance
                    success = True
    return {'success': success, 'ti': ti, 'msg': msg}
    
    
def getMediaList(tci):
    return list(tci.test_case.testcaseitem_set.order_by('play_order').values_list('video__filename',flat=True))

    
def init_signal(ti,status,msg='',mediaList=[]):
    return desktop_signal(ti,status,'init_test_instance',msg,mediaList,[['error'],['valid']])
    
        
def media_signal(ti,status,msg='',mediaList=[]):
    return desktop_signal(ti,status,'get_media',msg,mediaList,[['error','wait','done'],['run']])
    
    
def desktop_signal(ti,status,handle,msg,mediaList,validKeys):
    if len(msg) == 0:
        msg_text = ''
    else:
        msg_text = '%s: %s' % (handle,msg)
    valid_ti = isinstance(ti,TestInstance)
    if valid_ti:
        counter = ti.counter
    elif ti==0:                     # pass in ti=0 for cases when TestInstance does not exist or hasn't been queried yet
        counter = -1
    else:
        raise Exception('desktop_signal: invalid test instance.') 
    if status in validKeys[0]:      # if ti=0, it must have a failure/hold status
        path = ''
        list = []
    elif valid_ti and status in validKeys[1]:
        path = ti.path
        list = mediaList
        counter = ti.counter
    else:
        raise Exception('desktop_signal: invalid status.') 
    return HttpResponse(json.dumps({'status': status, 'msg': msg_text, 'path': path, 'mediaList': mediaList, 'counter': counter}))
        

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