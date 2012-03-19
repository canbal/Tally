from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from GenericTest.models import *
import json


# Helper functions, not views
def create_video(data):
    try:
        f = data['video']
    except(KeyError):
        return None
    else:
        return Video(filename=f, description=f)

        
def get_video(data):
    try:
        f = data['video']
    except(KeyError):
        return None
    else:
        try:
            v = Video.objects.get(filename=f)
            return v
        except(Video.DoesNotExist):
            return None

            
def create_or_get_video(data):
    v = get_video(data)
    if v is None:
        v = create_video(data)
        if v is not None:
            v.save()
    return v


def create_test(data):
    try:
        f = data['title']
    except(KeyError):
        return None
    else:
        return Test(title=f, description=f+f)

        
def get_test(data):
    try:
        f = data['title']
    except(KeyError):
        return None
    else:
        try:
            t = Test.objects.get(title=f)
            return t
        except(Test.DoesNotExist):
            return None

    
def create_or_update_case(data, test):
    try:
        o = data['order']
    except(KeyError):
        return None
    else:
        v = create_or_get_video(data)
        try:
            tc = test.testcase_set.get(play_order=o)            
        except(TestCase.DoesNotExist):
            tc = TestCase(play_order=o, is_done=0, test=test, video=v)            
        else:
            tc.video = v
            tc.is_done = 0
        return tc

    
def index(request):
    latest_test_list = Test.objects.all().order_by('-create_date')[:5]
    return render_to_response('GenericTest/index.html', {'latest_test_list': latest_test_list})

    
def detail(request, testInstance_id):
    ti = get_object_or_404(TestInstance, pk=testInstance_id)
    return render_to_response('GenericTest/detail.html', {'testInstance': ti}, context_instance=RequestContext(request))


def results(request, testInstance_id):
    ti = get_object_or_404(TestInstance, pk=testInstance_id)
    return render_to_response('GenericTest/results.html', {'testInstance': ti})

    
# Views

@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def add_video(request):
    data_json = request.POST['data']
    try:
        data = json.loads(data_json)
    except(TypeError, ValueError):
        return HttpResponse("Input format is wrong\n")
    else:
        v = get_video(data)
        if v is None:
            v = create_video(data)
            if v is not None:
                v.save()
                return HttpResponse("Video created\n")
            else:
                return HttpResponse("Input format is wrong\n")
        else:
            return HttpResponse("Video already exists\n")
    

@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def add_case(request, test_id):
    t = get_object_or_404(Test, pk=test_id)
    data_json = request.POST['data']
    try:
        data = json.loads(data_json)
    except(TypeError, ValueError):
        return HttpResponse("Input format is wrong\n")
    else:
        tc = create_or_update_case(data, t)
        if tc is not None:
            tc.save()
            return HttpResponse("Test is updated\n")
        else:
            return HttpResponse("Input format is wrong\n")
                        
            
@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def add_test(request):
    data_json = request.POST['data']
    try:
        data = json.loads(data_json)
    except(TypeError, ValueError):
        return HttpResponse("Input format is wrong\n")
    else:
        t = get_test(data)
        if t is None:
            t = create_test(data)
            if t is not None:
                t.save()
                return HttpResponse("Test created\n")
            else:
                return HttpResponse("Test input format is wrong\n")
        else:
            return HttpResponse("Test already exists\n")
            
            
@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def get_media(request, testInstance_id):
# initialization not quite working.  When desktop app first requests video (counter=0, is_done=False) there is a server error.
    ti = get_object_or_404(TestInstance, pk=testInstance_id)
    errStr = json.dumps({"path":"error", "video":"error", "testDone":True});
    if ti.counter<0:
        return HttpResponse(errStr)
    elif ti.counter>ti.testcase_set.count():
        return HttpResponse(json.dumps({"path":"", "video":"", "testDone":True}))
    try:
        tc = ti.testcase_set.get(play_order=ti.counter)     # should exist but check anyway
    except(TestCase.DoesNotExist):
        return HttpResponse(errStr)
    else:
        if ti.counter==1:
            ti.counter += 1
            ti.save()
            return HttpResponse(json.dumps({"path":ti.path, "video":tc.video.all()[0].filename, "testDone":False}))
        if tc.is_done:
            ti.counter += 1
            ti.save()
            return HttpResponse(json.dumps({"path":ti.path, "video":tc.video.all()[0].filename, "testDone":False}))
        else:
            return HttpResponse(json.dumps({"path":"", "video":"", "testDone":False}))
            
            
@csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
def tally(request,testInstance_id):
# upon submitting choice, the wait page seems to be working and correctly navigates to the page, but the subsequent voting page only appears after a manual refresh.
    ti = get_object_or_404(TestInstance, pk=testInstance_id)
    try:
        tc = ti.testcase_set.get(play_order=ti.counter)
    except(TestCase.DoesNotExist):
        return HttpResponse("test over")
    try:
        selection = request.POST['value'];
    except KeyError:
        return render_to_response('GenericTest/detail.html', {
            'testInstance': ti,
            'error_message': "Please select a choice.",
        }, context_instance=RequestContext(request))
    else:
        if selection=="queryState":
            prevCount = request.POST['prevCount'];
            if prevCount < ti.counter:
                return render_to_response('GenericTest/detail.html', {
                    'testInstance': ti,
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('GenericTest/results.html', {'testInstance': ti})
        else:
            score = Score(test_case=tc, subject=Subject.objects.get(pk=1), value=selection)
            score.save()
            tc.is_done = True;
            tc.save()
            return render_to_response('GenericTest/results.html', {'testInstance': ti})
