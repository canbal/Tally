from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
from GenericTest.models import *
from GenericTest.forms import *
from registration.models import UserProfile
import json


def index(request):
    latest_test_list = Test.objects.all().order_by('-create_date')[:5]
    return render_to_response('GenericTest/index.html', {'latest_test_list': latest_test_list})


@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
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
@permission_required('GenericTest.add_score')
def tally(request,test_instance_id):
#    if request.method=='GET':
#        return HttpResponse('please don't navigate yourself!')
    # get the test instance
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    maxCount = ti.testcaseinstance_set.count();
    choices = [(5,'Imperceptible'), (4,'Perceptible, but not annoying'), (3,'Slightly annoying'), (2,'Annoying'), (1,'Very annoying')]
    # check bounds of the counter (should handle these cases better)
    try:
        tci = ti.testcaseinstance_set.get(play_order=ti.counter)
    except(TestCaseInstance.DoesNotExist):
        return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': maxCount},  context_instance=RequestContext(request))
    # ensure that one of the choices was selected before submitting the form
    try:
        selection = request.POST['value']
    except KeyError:
        return render_to_response('GenericTest/detail.html', {
            'testInstance': ti, 'maxCount': maxCount, 'choices': choices,
            'error_message': 'Please select a choice.',
        }, context_instance=RequestContext(request))
    else:
        # if the hidden wait form was submitted, return the next test form if the counter has incremented or loop back to the wait page
        if selection=='queryState':         # using 'is' causes a bug here???
            prevCount = int(request.POST['prevCount'])
            if prevCount < ti.counter:
                return render_to_response('GenericTest/detail.html', {
                    'testInstance': ti, 'maxCount': maxCount, 'choices': choices
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': maxCount}, context_instance=RequestContext(request))
        # if the test form was submitted, process the data
        else:
            # make sure this subject has not submitted a score for this test case already (need to handle error better)
            subject_pk = UserProfile.objects.get(user=request.user)._get_pk_val()
            try:
                sc = UserProfile.objects.get(pk=subject_pk).score_set.get(test_case_instance=tci)
            except(Score.DoesNotExist):
            # only submit score if it belongs to the appropriate test (protects against scores from previous test being recorded for current test by hitting back button)
                current_count = int(request.POST['current_count'])
                if current_count is ti.counter:
                    score = Score(test_case_instance=tci, subject=UserProfile.objects.get(pk=subject_pk), value=selection)
                    score.save()
                else:
                    return render_to_response('GenericTest/detail.html', {'testInstance': ti, 'maxCount': maxCount, 'choices': choices
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': maxCount, 'error_message': 'you fool! vote already submitted'}, context_instance=RequestContext(request))
            # if all subjects of this test instance have reported scores for this test case, mark it as done
            try:
                for ii in range(0,ti.subject.count()):
                    sc = ti.subject.all()[ii].score_set.get(test_case_instance=tci)
            except(Score.DoesNotExist):
                pass
            else:
                tci.is_done = True
                tci.save()
            return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': maxCount}, context_instance=RequestContext(request))

            
@login_required
@permission_required('GenericTest.add_testcaseitem')
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
        
    return render_to_response('GenericTest/add_testcaseitem.html',  {'form': form,  'header': 'Add Test Case Item'},
                              context_instance=RequestContext(request))