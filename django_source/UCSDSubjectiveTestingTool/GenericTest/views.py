from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from GenericTest.models import *
from GenericTest.forms import *
import json


def index(request):
    latest_test_list = Test.objects.all().order_by('-create_date')[:5]
    return render_to_response('GenericTest/index.html', {'latest_test_list': latest_test_list})


@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def get_media(request, testInstance_id):
    ti = get_object_or_404(TestInstance, pk=testInstance_id)
    errStr = json.dumps({"path":"error", "video":"error", "testDone":True})
    # check bounds of counter
    if ti.counter<0:
        return HttpResponse(errStr)
    elif ti.counter>ti.testcase_set.count():
        return HttpResponse(json.dumps({"path":"", "video":"", "testDone":True}))
    # get the current test case
    try:
        tc_current = ti.testcase_set.get(play_order=max(1,ti.counter))     # should exist but check anyway
    except(TestCase.DoesNotExist):
        return HttpResponse(errStr)
    else:
        # if the current test is done, increment the counter and return the next video or a done signal
        if tc_current.is_done:
            ti.counter += 1
            ti.save()
            if ti.counter > ti.testcase_set.count():
                return HttpResponse(json.dumps({"path":"", "video":"", "testDone":True}))
            else:
                try:
                    tc_next = ti.testcase_set.get(play_order=ti.counter)
                except(TestCase.DoesNotExist):
                    return HttpResponse(errStr)
                else:
                    return HttpResponse(json.dumps({"path":ti.path, "video":tc_next.video.all()[0].filename, "testDone":False}))
        # if this is the first request of the test instance, return the first video and increment the counter
        elif ti.counter==0:
            ti.counter += 1
            ti.save()
            return HttpResponse(json.dumps({"path":ti.path, "video":tc_current.video.all()[0].filename, "testDone":False}))
        # otherwise, the subjects haven't finished scoring- return a wait signal
        else:
            return HttpResponse(json.dumps({"path":"", "video":"", "testDone":False}))
            
            
@login_required
def tally(request,testInstance_id):
#    if request.method=='GET':
#        return HttpResponse("please don't navigate yourself!")
    # get the test instance
    ti = get_object_or_404(TestInstance, pk=testInstance_id)
    choices = [(5,'Imperceptible'), (4,'Perceptible, but not annoying'), (3,'Slightly annoying'), (2,'Annoying'), (1,'Very annoying')]
    # check bounds of the counter (should handle these cases better)
    try:
        tc = ti.testcase_set.get(play_order=ti.counter)
    except(TestCase.DoesNotExist):
        return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': ti.testcase_set.count()},  context_instance=RequestContext(request))
    # ensure that one of the choices was selected before submitting the form
    try:
        selection = request.POST['value']
    except KeyError:
        return render_to_response('GenericTest/detail.html', {
            'testInstance': ti, 'choices': choices,
            'error_message': "Please select a choice.",
        }, context_instance=RequestContext(request))
    else:
        # if the hidden wait form was submitted, return the next test form if the counter has incremented or loop back to the wait page
        if selection=="queryState":
            prevCount = int(request.POST['prevCount'])
            if prevCount < ti.counter:
                return render_to_response('GenericTest/detail.html', {
                    'testInstance': ti, 'choices': choices
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': ti.testcase_set.count()}, context_instance=RequestContext(request))
        # if the test form was submitted, process the data
        else:
            # make sure this subject has not submitted a score for this test case already (need to handle error better)
            subject_pk = Subject.objects.get(user=request.user)._get_pk_val()
            try:
                sc = Subject.objects.get(pk=subject_pk).score_set.get(test_case=tc)
            except(Score.DoesNotExist):
            # only submit score if it belongs to the appropriate test (protects against scores from previous test being recorded for current test by hitting back button)
                current_count = int(request.POST['current_count'])
                if current_count is ti.counter:
                    score = Score(test_case=tc, subject=Subject.objects.get(pk=subject_pk), value=selection)
                    score.save()
                else:
                    return render_to_response('GenericTest/detail.html', {'testInstance': ti, 'choices': choices
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': ti.testcase_set.count(), 'error_message': 'you fool! vote already submitted'}, context_instance=RequestContext(request))
            # if all subjects of this test instance have reported scores for this test case, mark it as done
            try:
                for ii in range(0,ti.subjects.count()):
                    sc = ti.subjects.all()[ii].score_set.get(test_case=tc)
            except(Score.DoesNotExist):
                pass
            else:
                tc.is_done = True
                tc.save()
            return render_to_response('GenericTest/results.html', {'testInstance': ti, 'maxCount': ti.testcase_set.count()}, context_instance=RequestContext(request))

@login_required
def add_test_case_item(request, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    t  = ti.test
    if request.method == 'POST':
        form = TestCaseItemForm(request.POST)
        form.fields["video"].queryset = Video.objects.filter(test=t)
        if form.is_valid():
            form.save()
            return HttpResponse('Test case item created successfully!')
    else:
        form = TestCaseItemForm()
        form.fields["video"].queryset = Video.objects.filter(test=t)
        
    return render_to_response("GenericTest/addtestcaseitem.html",  {'form': form,  },
                              context_instance=RequestContext(request))