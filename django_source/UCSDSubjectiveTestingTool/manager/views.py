from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from GenericTest.models import *
import json



@login_required
def create_test(request):
    return render_to_response('manager/create_test.html',context_instance=RequestContext(request))
    
    
@login_required
def create_test_cases(request):
    return render_to_response('manager/create_test_cases.html',context_instance=RequestContext(request))
    
    
@login_required
def save_test(request):
    return render_to_response('manager/save_test.html',context_instance=RequestContext(request))


@login_required
def display_test(request, test_id):
    return render_to_response('manager/display_test.html',context_instance=RequestContext(request))


@login_required
def display_test_instance(request, test_id, test_instance_id):
    return render_to_response('manager/display_test_instance.html',context_instance=RequestContext(request))


@login_required
def create_test_instance(request, test_id):
    return render_to_response('manager/create_test_instance.html',context_instance=RequestContext(request))


@login_required
def save_test_instance(request, test_id):
    return render_to_response('manager/save_test_instance.html',context_instance=RequestContext(request))


@login_required
def start_test(request, test_id, test_instance_id):
    return render_to_response('manager/start_test.html',context_instance=RequestContext(request))
