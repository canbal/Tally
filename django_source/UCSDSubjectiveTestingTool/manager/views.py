from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from GenericTest.models import *
from manager.forms import *
import json, random, csv


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)):
                return True
        return False
    return user_passes_test(in_groups)

def is_video(file_type):
    if file_type.split('/')[0] == 'video':
        return True
    else:
        return False
    
@login_required
@group_required('Testers')
def create_test(request):
    try:
        up = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponse('You do not have permission to add tests!')
    else:
        if request.method == 'POST':
            tf = CreateTestForm(request.POST)
            tf.fields['collaborator'].queryset = tf.fields['collaborator'].queryset.exclude(user=up.user)
            if tf.is_valid():
                # create new test
                new_t = tf.save(commit=False)     # create new test instance from form, but don't save it yet
                new_t.owner = up                  # when an admin is logged in, they are not recognized as a user!!!!!!
                new_t.save()                      # save the new instance
                
                files = json.loads(request.POST['files_json'])
                for f in files:
                    file_type = f['name']
                    if is_video(file_type):
                        new_f = Video(test=new_t, filename=f['value'])
                        new_f.save()
                    
                # redirect to test display page
                return HttpResponseRedirect(reverse('manager.views.display_test', args=(new_t.pk,)))
        else:
            tf = CreateTestForm()
            tf.fields['collaborator'].queryset = tf.fields['collaborator'].queryset.exclude(user=up.user)
            
        return render_to_response('manager/create_test.html',{'tf':tf,},context_instance=RequestContext(request))
    
    
@login_required
@group_required('Testers')
def create_test_cases(request):
    return render_to_response('manager/create_test_cases.html',context_instance=RequestContext(request))
    
    
@login_required
@group_required('Testers')
def save_test(request):
    return render_to_response('manager/save_test.html',context_instance=RequestContext(request))


@login_required
@group_required('Testers')
def display_test(request, test_id):
    t = get_object_or_404(Test, pk=test_id)
    up = UserProfile.objects.get(user=request.user)
    if (up == t.owner) or (up in t.collaborator.all()):
        tf = DisplayTestForm(instance=t)
        return render_to_response('manager/display_test.html', {'title': t.title,
                                                                'tf': tf,
                                                                'create_time_name': t._meta.get_field('create_time').verbose_name,
                                                                'create_time': t.create_time,
                                                                'test_id': test_id,
                                                                'videos': Video.objects.filter(test=t),
                                                                'can_share': (up == t.owner) or (up == t.test.owner),
                                                                'can_export': True},  # anyone who can view it can export
                                                                context_instance=RequestContext(request))
    else:
        return HttpResponse('must be owner or collaborator of this test instance or associated test')
    


@login_required
@group_required('Testers')
def display_test_instance(request, test_id, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    up = UserProfile.objects.get(user=request.user)
    if (up == ti.owner) or (up in ti.collaborator.all()) or (up == ti.test.owner) or (up in ti.test.collaborator.all()):
        tif = DisplayTestInstanceForm(instance=ti)
        return render_to_response('manager/display_test_instance.html',  { 'tif': tif,
                                                                           'create_time_name': ti._meta.get_field('create_time').verbose_name,
                                                                           'create_time': ti. create_time,
                                                                           'test_id': test_id,
                                                                           'test_instance_id': test_instance_id,
                                                                           'already_run': ti.run_time is not None,
                                                                           'can_share': (up == ti.owner) or (up == ti.test.owner),
                                                                           'can_export': True,  # anyone who can view it can export
                                                                           'can_run': (up == ti.owner) },
                                 context_instance=RequestContext(request))
    return HttpResponse('must be owner or collaborator of this test instance or associated test')


@login_required
@group_required('Testers')
def create_test_instance(request, test_id):
    t = get_object_or_404(Test, pk=test_id)
    up = UserProfile.objects.get(user=request.user)
    if (up == t.owner) or (up in t.collaborator.all()):
        if request.method == 'POST':
            tif = CreateTestInstanceForm(request.POST)
            if tif.is_valid():
                try:
                    # A user may not have an associated UserProfile - i.e. SuperUser
                    owner = UserProfile.objects.get(user=request.user)
                except UserProfile.DoesNotExist:
                    return HttpResponse('You do not have permission to add test instances!')
                else:
                    # create new instance
                    new_ti = tif.save(commit=False)     # create new test instance from form, but don't save it yet
                    new_ti.test = t         # add in exluded fields
                    new_ti.owner = owner    # when an admin is logged in, they are not recognized as a user!!!!!!
                    new_ti.path = new_ti.path.replace("\\","/").rstrip("/")     # make sure path has only forward slashes and no trailing slashes
                    new_ti.save()           # save the new instance
                    tif.save_m2m()          # save the many-to-many data for the form
                    # create new test case instances
                    tc_all = t.testcase_set.all()
                    repeat = [1, 2, 3, 5]#tc_all.count()*[1]            # repeat each test case 1 time for testing; this list will come from somewhere else eventually
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
    return HttpResponse('must be owner or collaborator this test')


@login_required
@group_required('Testers')
def start_test(request, test_id, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    up = UserProfile.objects.get(user=request.user)
    if up == ti.owner:
        return render_to_response('manager/start_test.html',context_instance=RequestContext(request))
    return HttpResponse('must be owner of this test instance')

    
@login_required
@group_required('Testers')
def export_data(request):
    # get all test instances that have been run
    ti_ran = TestInstance.objects.exclude(run_time=None)
    up = UserProfile.objects.get(user=request.user)
    # of these, find the ones of which the user is an owner or collaborator
    ti_valid = []
    t_valid = []
    for ti in ti_ran:
        if (up == ti.owner) or (up in ti.collaborator.all()) or (up == ti.test.owner) or (up in ti.test.collaborator.all()):
            ti_valid.append(ti.pk)
            t_valid.append(ti.test.pk)
    data = {'t_valid': t_valid, 'ti_valid': ti_valid}   # lists of equal length containing pk of test instance and corresponding (non-unique) test
    # if this page was reached from a test/test instance page, select default options
    if request.method == 'POST':
        try:
            test_id = request.POST['test_id']
            test_instance_id = request.POST['test_instance_id']
        except KeyError:
            pass
        else:
            ti = get_object_or_404(TestInstance, pk=test_instance_id)
            up = UserProfile.objects.get(user=request.user)
            data = dict(data.items() + [('test_id', test_id), ('test_instance_id', test_instance_id)])
    return render_to_response('manager/export_data.html', data, context_instance=RequestContext(request))
    
    
@login_required
def save_data(request):
    # eventually this request will have test_id/test_instance_id data along with it.
    # check for owner/collaborator status
    if request.method == 'POST':
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=test_data.csv'
        writer = csv.writer(response)
        writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
        writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
        return response
    return HttpResponseRedirect(reverse('manager.views.export_data'))
    
    
@login_required
@group_required('Testers')
def share_test(request):
    # test owners can share tests and and child test instances of tests they own
    # test instance owners can share their test instances
    up = UserProfile.objects.get(user=request.user)
    tests = Test.objects.filter(owner=up)              # tests user owns
    t_own = []                                         # pk's of tests that users owns, corresponding to t_own_ti
    t_own_ti = []                                      # pk's of all test instances of tests that user owns (regardless of ownership of test instances)
    for t in tests:
        ti = TestInstance.objects.filter(test=t)
        t_own_ti.extend(ti.values_list('pk',flat=True))
        t_own.extend(ti.count()*[t.pk])
    ti_own = TestInstance.objects.filter(owner=up).values_list('pk', flat=True)     # pk's of test instances user owns
    ti_own_t = []                                                                   # pk's of tests corresponding to test instances that user owns
    for id in ti_own:
        ti_own_t.append(TestInstance.objects.get(pk=id).test.pk)
    data = {'t_own': t_own, 't_own_ti': t_own_ti, 'ti_own': ti_own, 'ti_own_t': ti_own_t}
    # if this page was reached from a test/test instance page, select default options
    if request.method == 'POST':
        try:
            test_id = request.POST['test_id']
            test_instance_id = request.POST['test_instance_id']
        except KeyError:
            pass
        else:
            ti = get_object_or_404(TestInstance, pk=test_instance_id)
            up = UserProfile.objects.get(user=request.user)
            data = dict(data.items() + [('test_id', test_id), ('test_instance_id', test_instance_id)])
    return render_to_response('manager/share_test.html', data, context_instance=RequestContext(request))
    
    