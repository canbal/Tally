from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from GenericTest.models import *
from forms import CreateTestInstanceForm, DisplayTestInstanceForm
import json, random, csv


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
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    tif = DisplayTestInstanceForm(instance=ti)
    return render_to_response('manager/display_test_instance.html',  { 'tif': tif,
                                                                       'create_time_name': ti._meta.get_field('create_time').verbose_name, 'create_time': ti.create_time,
                                                                       'test_id': test_id,
                                                                       'test_instance_id': test_instance_id,
                                                                       'already_run': ti.run_time is not None },
                              context_instance=RequestContext(request))


@login_required
def create_test_instance(request, test_id):
    if request.method == 'POST':
        tif = CreateTestInstanceForm(request.POST)
        if tif.is_valid():
            try:
                # A user may not have an associated UserProfile - i.e. SuperUser
                owner = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return HttpResponse('You do not have permission to add test instances!')
            else:
                t = get_object_or_404(Test, pk=test_id)
                # create new instance
                new_ti = tif.save(commit=False)     # create new test instance from form, but don't save it yet
                new_ti.test = t         # add in exluded fields
                new_ti.owner = owner    # when an admin is logged in, they are not recognized as a user!!!!!!
                new_ti.path = new_ti.path.replace("\\","/").rstrip("/")     # make sure path has only forward slashes and no trailing slashes
                new_ti.save()           # save the new instance
                tif.save_m2m()          # save the many-to-many data for the form
                # create new test case instances
                tc_all = t.testcase_set.all()
                repeat = tc_all.count()*[1]            # repeat each test case 1 time for testing; this list will come from somewhere else eventually
                rand_order = range(1,sum(repeat)+1)    # play order starts from 1
                random.shuffle(rand_order)
                idx = 0
                for ii in range(0,tc_all.count()):
                    for jj in range(0,repeat[ii]):
                        tci = TestCaseInstance(test_instance=new_ti, test_case=tc_all[ii], play_order=rand_order[idx])
                        idx += 1
                        tci.save()
                # redirect to test instance display page
                return HttpResponseRedirect(reverse('manager.views.display_test_instance', args=(t.pk, new_ti.pk,)))
    else:
        tif = CreateTestInstanceForm()
    return render_to_response('manager/create_test_instance.html', { 'tif': tif }, context_instance=RequestContext(request))


@login_required
def start_test(request, test_id, test_instance_id):
    return render_to_response('manager/start_test.html',context_instance=RequestContext(request))

    
@login_required
def export_data(request):
    if request.method == 'POST':
        try:
            test_id = request.POST['test_id']
            test_instance_id = request.POST['test_instance_id']
        except KeyError:
            pass
        else:
            return render_to_response('manager/export_data.html', {'test_id': test_id, 'test_instance_id': test_instance_id }, context_instance=RequestContext(request))
    return render_to_response('manager/export_data.html',context_instance=RequestContext(request))
    
    
@login_required
def save_data(request):
    if request.method == 'POST':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=test_data.csv'
        writer = csv.writer(response)
        writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
        writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
        return response
    return HttpResponseRedirect(reverse('manager.views.export_data'))