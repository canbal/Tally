from django.contrib.auth.decorators import login_required
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


@login_required, @csrf_exempt #remove later, add csrf_token (in cookie) and csrfmiddlewaretoken (within POST data) handling!
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