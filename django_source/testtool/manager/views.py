from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.conf import settings
from testtool.models import *
from testtool.decorators import group_required
from testtool.shortcuts import has_user_profile
from forms import TestCreateForm, TestDisplayForm, CreateTestInstanceForm, DisplayTestInstanceForm
import random, csv, json, os

class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,data='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = json.dumps(data,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
    
def is_file_supported(filename):
    ext = os.path.splitext(filename)[1]
    if (ext=='.avi' or ext=='.mp4' or ext=='.m4v' or ext=='.wmv' or 
        ext=='.flv' or ext=='.mpg' or ext=='.mov'):
        return True
    else:
        return False

    
def user_can(action,up,obj):
    if isinstance(obj,Test):
        return test_permission(action,up,obj)
    elif isinstance(obj,TestInstance):
        return test_instance_permission(action,up,obj)
    else:
        raise Exception('user_can: Must pass Test or TestInstance object.')
    

def test_permission(action,up,t):
    if action is 'view':
        return True
        # test owner, collaborator, or any owner/collaborator of any child test instances
    elif action is 'export':
        return ((up == t.owner) or (up in t.collaborators.all()))
    elif action is 'share':
        return (up == t.owner)
    elif action is 'create':
        return ((up == t.owner) or (up in t.collaborators.all()))       # refers to creating test instances from the test
    else:
        raise Exception('test_permission: invalid action.')
    
    
def test_instance_permission(action,up,ti):
    if action is 'view' or 'export':
        return ((up == ti.owner) or (up in ti.collaborators.all()) or (up == ti.test.owner) or (up in ti.test.collaborators.all()))
    elif action is 'share':
        return ((up == ti.owner) or (up == ti.test.owner))
    elif action is 'run':
        return (up == ti.owner)
    else:
        raise Exception('test_instance_permission: invalid action.')

        
class TestCreateView(CreateView):
    model = Test
    form_class = TestCreateForm
    template_name = 'testtool/manager/create_test.html'
    success_url = reverse_lazy('update_test')
                
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(TestCreateView, self).dispatch(*args, **kwargs)
    
    def get_form(self, form_class):
        form = super(TestCreateView, self).get_form(form_class)
        form.fields['collaborators'].queryset = form.fields['collaborators'].queryset.exclude(user=self.request.user)
        return form
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user.get_profile()
        self.object.save()
        return HttpResponseRedirect(reverse('update_test', args=(self.object.pk,)))
    
class TestUpdateView(UpdateView):
    model = Test
    form_class = TestCreateForm
    template_name = 'testtool/manager/update_test.html'
                
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(TestUpdateView, self).dispatch(*args, **kwargs)
    
    def get_form(self, form_class):
        form = super(TestUpdateView, self).get_form(form_class)
        form.fields['collaborators'].queryset = form.fields['collaborators'].queryset.exclude(user=self.request.user)
        return form
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user.get_profile()
        self.object.save()
        return HttpResponseRedirect(reverse('update_test', args=(self.object.pk,)))    
    
    def get_context_data(self, **kwargs):
        context = super(TestUpdateView, self).get_context_data(**kwargs)
        context['files'] = Video.objects.filter(test=self.object)
        context['test_pk'] = self.object.pk
        return context

@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def add_video(request, test_pk):
    if request.method == 'POST':
        messages = {'0': 'Done', '1': 'Test does not exist', '2': 'No file provided', '3':'Video already exists', '4':'File type is not supported', '5':'Permission failed'}
        
        #checking for json data type
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
            
        try:
            t = Test.objects.get(pk=test_pk)
        except Test.DoesNotExist:
            status = 1;
        else:
            if test_permission('create',request.user.get_profile(),t):
                try:
                    filename =  request.POST['filename']
                except KeyError:
                    status = 2; #TODO: should change when file upload is supported
                else:
                    if is_file_supported(filename):
                        try:
                            f = Video.objects.get(test=t, filename=filename)
                        except Video.DoesNotExist:
                            f = Video(test=t, filename=filename)
                            f.save()
                            status = 0;
                        else:
                            status = 3;
                    else:
                        status = 4;
            else:
                status = 5;
        
        data = {'status':status,'message':messages[str(status)]}
        response = JSONResponse(data, {}, mimetype)
        return response
    else:
        return HttpResponseBadRequest('GET is not supported')

@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def delete_video(request, video_pk):
    if request.method == 'POST':
        messages = {'0': 'Done', '1': 'Video does not exist', '5': 'Permission failed'}
        
        #checking for json data type
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
            
        try:
            f = Video.objects.get(pk=video_pk)
            t = f.test
        except Video.DoesNotExist:
            status = 1;
        else:
            if test_permission('create',request.user.get_profile(),t):
                f.delete()
                status = 0;
            else:
                status = 5;
            
        data = {'status':status,'message':messages[str(status)]}
        response = JSONResponse(data, {}, mimetype)
        return response
    else:
        return HttpResponseBadRequest('GET is not supported')
    
@login_required
@group_required('Testers')
def create_test_cases(request):
    return render_to_response('testtool/manager/create_test_cases.html',context_instance=RequestContext(request))
    
    
@login_required
@group_required('Testers')
def save_test(request):
    return render_to_response('testtool/manager/save_test.html',context_instance=RequestContext(request))


@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def list_tests(request):
    up = request.user.get_profile()
    t_o = up.owner_tests.values_list('pk',flat=True)
    t_c = up.collaborators_tests.values_list('pk',flat=True)
    ti_c = up.collaborators_testinstances.values_list('test__pk',flat=True)
    test_list = list(set(list(t_o) + list(t_c) + list(ti_c)))
    tests = Test.objects.filter(pk__in=test_list)
    return render_to_response('testtool/manager/list_tests.html', { 'tests': tests }, context_instance=RequestContext(request))

  
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def display_test(request, test_id):
    t = get_object_or_404(Test, pk=test_id)
    up = request.user.get_profile()
    if (up == t.owner) or (up in t.collaborators.all()):
        tf = TestDisplayForm(instance=t)
        return render_to_response('testtool/manager/display_test.html', {'title': t.title,
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
@user_passes_test(has_user_profile)
def display_test_instance(request, test_id, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id, test__pk=test_id)   # ensures that test instance belongs to test
    up = request.user.get_profile()
    if user_can('view',up,ti):
        tif = DisplayTestInstanceForm(instance=ti)
        if request.method == 'GET':
            try:
                alert = request.GET['alert']
            except KeyError:
                alert = ''
        return render_to_response('testtool/manager/display_test_instance.html',  { 'tif': tif,
                                                                                       'create_time_name': ti._meta.get_field('create_time').verbose_name,
                                                                                       'create_time': ti.create_time,
                                                                                       'test_id': test_id,
                                                                                       'test_instance_id': test_instance_id,
                                                                                       'already_run': ti.run_time is not None,
                                                                                       'can_share': user_can('share',up,ti),
                                                                                       'can_export': user_can('export',up,ti),
                                                                                       'can_run': user_can('run',up,ti),
                                                                                       'alert': alert },
                                                                                       context_instance=RequestContext(request))
    return render_to_response('testtool/manager/display_test_instance.html',  { 'test_id': test_id,
                                                                                'test_instance_id': test_instance_id,
                                                                                'error': 'You do not have access to this test instance.'},
                                                                                context_instance=RequestContext(request))


@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def create_test_instance(request, test_id):
    t = get_object_or_404(Test, pk=test_id)
    up = request.user.get_profile()
    if user_can('create',up,t):
        if request.method == 'POST':
            tif = CreateTestInstanceForm(request.POST)
            tif.fields['collaborators'].queryset = tif.fields['collaborators'].queryset.exclude(user=up.user)
            if tif.is_valid():
                # create new instance
                new_ti = tif.save(commit=False)     # create new test instance from form, but don't save it yet
                new_ti.test = t         # add in exluded fields
                new_ti.owner = up       # when an admin is logged in, they are not recognized as a user!!!!!!
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
                return HttpResponseRedirect(reverse('testtool.manager.views.display_test_instance', args=(t.pk, new_ti.pk))+'?alert=new')
        else:
            tif = CreateTestInstanceForm()
            tif.fields['collaborators'].queryset = tif.fields['collaborators'].queryset.exclude(user=up.user)
        return render_to_response('testtool/manager/create_test_instance.html', { 'tif': tif, 'test_id': test_id }, context_instance=RequestContext(request))
    return render_to_response('testtool/manager/create_test_instance.html', { 'error': 'You must be an owner or collaborator of this test in order to create a test instance.'}, context_instance=RequestContext(request))


@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def start_test(request, test_id, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    up = request.user.get_profile()
    if user_can('run',up,ti):
        return render_to_response('testtool/manager/start_test.html',context_instance=RequestContext(request))
    return render_to_response('testtool/manager/start_test.html',{ 'error': 'You must be the owner of this test instance in order to run it.' }, context_instance=RequestContext(request))

    
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def export_data(request):
    test_instance_ran = TestInstance.objects.exclude(run_time=None)                 # all test instances that have been run
    test_id_ran = test_instance_ran.values_list('test__pk',flat=True).distinct()    # pk's of all tests that have test instances that have been run
    up = request.user.get_profile()
    # of these, find the ones of which the user is an owner or collaborator
    t_valid = []
    ti_valid = []
    t_valid_id = []
    ti_valid_id = []
    for id in test_id_ran:                              # for each run test, find its run instances
        t_ran = Test.objects.get(pk=id)
        t_ran_ti = test_instance_ran.filter(test=t_ran)
        tmp_list = []
        tmp_list_pk = []
        for ti in t_ran_ti:
            if user_can('export',up,ti):
                tmp_list.append(ti)
                tmp_list_pk.append(ti.pk)
        if len(tmp_list) > 0:
            t_valid.append(t_ran)
            ti_valid.append(tmp_list)
            ti_valid_id.append(tmp_list_pk)
            t_valid_id.append(t_ran.pk)
    # if this page was reached from a test/test instance page, select default options
    if len(t_valid) > 0:
        t_valid_index_default = 0
        ti_valid_index_default = 0
        if request.method == 'POST':
            try:
                test_id = int(request.POST['test_id'])
            except KeyError:
                pass
            else:
                if test_id in t_valid_id:
                    t_valid_index_default = t_valid_id.index(test_id)
                    try:
                        test_instance_id = int(request.POST['test_instance_id'])
                    except KeyError:
                        pass
                    else:
                        if test_instance_id in ti_valid_id[t_valid_index_default]:
                            ti_valid_index_default = ti_valid_id[t_valid_index_default].index(test_instance_id)
                        else:
                            return render_to_response('testtool/manager/export_data.html', { 'error': 'You do not have access to this test instance data' }, context_instance=RequestContext(request))
                else:
                    return render_to_response('testtool/manager/export_data.html', { 'error': 'You do not have access to this test data' }, context_instance=RequestContext(request))
        data = {'t_valid': t_valid, 'ti_valid': ti_valid, 't_valid_index_default': t_valid_index_default, 'ti_valid_index_default': ti_valid_index_default }
    else:
        data = {'error': 'There are no test instances that have been run for which you have export permissions.' }
    return render_to_response('testtool/manager/export_data.html', data, context_instance=RequestContext(request))
        
    
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
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
    return HttpResponseRedirect(reverse('testtool.manager.views.export_data'))
    
    
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def share_test(request):
    # test owners can share tests and and child test instances of tests they own
    # test instance owners can share their test instances
    up = request.user.get_profile()
    
    # tests user owns and their test instances
    t_own = Test.objects.filter(owner=up)               # tests user owns
    t_own_ti = []                                       # pk's of TestInstances of Tests that user owns
    for t in t_own:
        t_own_ti.extend(t.testinstance_set.values_list('pk',flat=True))
    
    # test instances user owns and their tests
    ti_own = TestInstance.objects.filter(owner=up)                  # test instances user owns
    ti_own_t = ti_own.values_list('test__pk',flat=True).distinct()   # pk's of Tests of TestInstances that user owns
    
    # combine them into unique lists
    t_ti_share = list(set(list(t_own.values_list('pk',flat=True)) + list(ti_own_t)))    # pk's of Tests that have TestInstances that can be shared
    ti_share = list(set(t_own_ti + list(ti_own.values_list('pk',flat=True))))     # pk's of TestInstances that can be shared
    
    # group test instances by test
    t_valid = []
    ti_valid = []
    t_valid_id = []
    ti_valid_id = []
    for id in t_ti_share:
        t = Test.objects.get(pk=id)
        tmp = TestInstance.objects.filter(test=t).filter(pk__in=ti_share)
        tmp_id = tmp.values_list('pk',flat=True)
        if tmp.count() > 0:
            t_valid.append(t)
            ti_valid.append(tmp)
            t_valid_id.append(t.pk)
            ti_valid_id.append(list(tmp_id))

    # list users who do not yet have access to test/test instances
    all_testers = Group.objects.get(name='Testers').user_set.all()
    share_test_with = []        # users with whom tests can be shared (nested list, each list corresponds to test in t_own)
    for t in t_own:
        sw1 = []
        for u in all_testers:
            if (u.userprofile != t.owner) and (u.userprofile not in t.collaborators.all()):
                sw1.append(u)
        share_test_with.append(sw1)
    share_test_instance_with = []    # users with whom test instances can be shared (double-nested list, i.e. [[[u1,u2,u3],[u1,u4]], [[u2,u3],[u3,u4]]]
    for ti_list in ti_valid:
        sw1 = []
        for ti in ti_list:
            sw2 = []
            for u in all_testers:
                if (u.userprofile != ti.owner) and (u.userprofile not in ti.collaborators.all()) and (u.userprofile != ti.test.owner) and (u.userprofile not in ti.test.collaborators.all()):
                    sw2.append(u)
            sw1.append(sw2)
        share_test_instance_with.append(sw1)

    # set defaults
    radio_default = 1
    t_valid_index_default = 0
    ti_valid_index_default = 0
    # if this page was reached from a test/test instance page, select default options
    if request.method == 'POST':
        try:
            test_id = int(request.POST['test_id'])
        except KeyError:
            # no defaults requested, use default defaults
            pass
        else:
            try:
                test_instance_id = int(request.POST['test_instance_id'])
            except KeyError:
                # a test was requested to be shared
                t_own_id_values = t_own.values_list('pk',flat=True)
                if test_id in t_own_id_values:
                    radio_default = 0
                    t_valid_index_default = list(t_own_id_values).index(test_id)
                else:
                    return render_to_response('testtool/manager/share_test.html', 'You do not have permission to share this test.', context_instance=RequestContext(request))
            else:
                # a test instance of a test was requested to be shared
                if test_id in t_valid_id:
                    t_idx = t_valid_id.index(test_id)
                    if test_instance_id in ti_valid_id[t_idx]:
                        ti_valid_index_default = ti_valid_id[t_idx].index(test_instance_id)
                        t_valid_index_default = t_idx
                    else:
                        return render_to_response('testtool/manager/share_test.html', 'You do not have access to this test instance data.', context_instance=RequestContext(request))
                else:
                    return render_to_response('testtool/manager/share_test.html', 'You do not have access to this test data.', context_instance=RequestContext(request))
    data = {'t_own': t_own,
            't_valid': t_valid,
            'ti_valid': ti_valid,
            't_valid_index_default': t_valid_index_default,
            'ti_valid_index_default': ti_valid_index_default,
            'radio_default': radio_default,
            'share_test_with': share_test_with,
            'share_test_instance_with': share_test_instance_with }
    return render_to_response('testtool/manager/share_test.html', data, context_instance=RequestContext(request))
    
    
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def share_test_submit(request):
    if request.method == 'POST':
        try:
            mode = request.POST['radio_share']
            t_pk = int(request.POST['test_select'])
            share_with = request.POST.getlist('tester_select')
        except KeyError:
            return HttpResponse('please select a choice')
        else:
            if len(share_with) == 0:
                return HttpResponse('please select a choice')
            up = request.user.get_profile()
            if mode == 'share_test':
                t = get_object_or_404(Test, pk=t_pk)
                if user_can('share',up,t):                              # check that user can share test
                    for id in share_with:                               # add collaborators to test
                        u = get_object_or_404(UserProfile, pk=int(id))
                        t.collaborators.add(u)
                    return HttpResponseRedirect(reverse('testtool.manager.views.display_test', args=(t.pk,)))
                else:
                    return HttpResponse('you cannot share this test')
            elif mode == 'share_test_instance':
                try:
                    ti_pk = int(request.POST['test_instance_select'])
                except KeyError:
                    return HttpResponse('please select a test instance')
                else:
                    ti = get_object_or_404(TestInstance, pk=ti_pk, test__pk=t_pk)   # ensures that test instance belongs to test
                    if user_can('share',up,ti):                                     # check that user can share test instance
                        for id in share_with:                                       # add collaborators to test instance
                            u = get_object_or_404(UserProfile, pk=int(id))
                            ti.collaborators.add(u)
                        return HttpResponseRedirect(reverse('testtool.manager.views.display_test_instance', args=(ti.test.pk,ti.pk,))+'?alert=share')
                    else:
                        return HttpResponse('you cannot share this test instance')
            else:
                return HttpResponse('mode must be ''share_test'' or ''share_test_instance''')
    else:
        return HttpResponseRedirect(reverse('testtool.manager.views.share_test'))

    
@login_required
@group_required('Testers')
def about(request):
    return render_to_response('testtool/manager/about.html',context_instance=RequestContext(request))
    

@login_required
@group_required('Testers')
def help(request):
    return render_to_response('testtool/manager/help.html',context_instance=RequestContext(request))