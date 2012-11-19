from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db.models import Q
from testtool.models import *
from testtool.decorators import group_required
from testtool.shortcuts import has_user_profile
from forms import *
from cStringIO import StringIO
from zipfile import ZipFile
from scipy import io
import string, random, csv, json, os, zipfile


########################################################################################################
########################         SUPPORT/POLICY/LOGGING/MISC FUNCTIONS         #########################
########################################################################################################
class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,data='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = json.dumps(data,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
        
    
def is_file_supported(filename):
    ext = os.path.splitext(filename)[1]
    supported_ext = ['.avi', '.mp4', 'm4v', '.wmv', '.flv', '.mpg', '.mov']
    return ext in supported_ext

    
def user_can(action,up,obj,detail=False):
    perm = user_permission(up,obj)
    perm_user = perm['status'] in perm['perm_policy'][action]
    perm_obj = perm['obj_policy'][action]
    granted = perm_user and perm_obj
    if detail:
        return {'granted': granted, 'perm_user': perm_user, 'perm_obj': perm_obj}
    return granted
    
    
def user_status(up,obj):
    perm = user_permission(up,obj)
    return perm['status']
    

def user_permission(up,obj):
    if isinstance(obj,Test):
        return user_permission_test(up,obj)
    elif isinstance(obj,TestInstance):
        return user_permission_test_instance(up,obj)
    else:
        raise Exception('user_permission: Must pass Test or TestInstance object.')
    
    
def user_permission_test(up,t):
    status = ['Owner', 'Collaborator', 'Owner (Test Instance)', 'Collaborator (Test Instance)', 'None']
    if up == t.owner:
        idx = 0
    elif up in t.collaborators.all():
        idx = 1
    elif (up.owner_testinstances.filter(test=t).count() > 0):
        idx = 2
    elif (up.collaborators_testinstances.filter(test=t).count() > 0):
        idx = 3
    else:
        idx = 4
    # policy based on user status for actions on tests
    perm_policy = { 'view':    status[0:4],
                    'export':  status[0:2],
                    'share':   status[0:1],
                    'create':  status[0:2],  # refers to creating test instances from the test
                    'edit':    status[0:1],  # refers to changing fields that WON'T affect already existing test instances
                    'modify':  status[0:1],  # refers to changing fields that WILL  affect already existing test instances
                    'delete':  status[0:1],
                    'unshare': status[1:2] }
    # policy based on test status for actions on tests
    zero_ti = TestInstance.objects.filter(test=t).count() == 0
    obj_policy = { 'view':    True,
                   'export':  True,
                   'share':   True,
                   'create':  t.testcase_set.count() > 0,
                   'edit':    True,
                   'modify':  zero_ti,
                   'delete':  zero_ti,
                   'unshare': True }
    return { 'status': status[idx], 'perm_policy': perm_policy, 'obj_policy': obj_policy }


def user_permission_test_instance(up,ti):
    status = ['Owner', 'Collaborator', 'Owner (Test)', 'Collaborator (Test)', 'None']
    if up == ti.owner:
        idx = 0
    elif up in ti.collaborators.all():
        idx = 1
    elif up == ti.test.owner:
        idx = 2
    elif up in ti.test.collaborators.all():
        idx = 3
    else:
        idx = 4
    # policy based on user status for actions on test instances
    perm_policy = { 'view':    status[0:4],
                    'export':  status[0:4],
                    'share':   status[0:3:2],
                    'run':     status[0:1],
                    'edit':    status[0:1],
                    'delete':  status[0:1],
                    'unshare': status[1:2] }
    # policy based on test instance status for actions on test instances
    obj_policy = { 'view':    True,
                   'export':  ti.run_time is not None,
                   'share':   True,
                   'run':     ti.is_active(),
                   'edit':    True,
                   'delete':  ti.collaborators.count() == 0,
                   'unshare': True }
    return { 'status': status[idx], 'perm_policy': perm_policy, 'obj_policy': obj_policy }


@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def log_book(request):
    log = get_log(request,'all')
    return render_to_response('testtool/manager/log_book.html', { 'log':log }, context_instance=RequestContext(request))
    
        
def get_log(request,mode):
    up = request.user.get_profile()    
    entries_all = LogEntry.objects.filter(logtag__user=up).order_by('-timestamp')
    entries_new = entries_all.filter(logtag__user=up,logtag__viewed=False)
    if mode=='all':
        entry_set = entries_all
    elif mode=='new':
        entry_set = entries_new
    else:
        raise Exception('get_log: Mode must be ''all'' or ''new''.')
    icon_map = {'joined':   'icon-user',
                'created':  'icon-file',
                'edited':   'icon-edit',
                'ran':      'icon-pencil',
                'shared':   'icon-share',
                'unshared': 'icon-remove',
                'deleted':  'icon-trash' }
    log = [(e, e.logtag_set.get(user=up).viewed, icon_map[e.action]) for e in entry_set]  # pass in old 'viewed' parameter to highlight new entries
    LogTag.objects.filter(user=up).update(viewed=True)                            # mark all entries as viewed
    return log
        
        
def create_log_entry(actor,action,obj,tags_arg=[]):
    ts = datetime.datetime.now()
    if action=='joined':
        os = {'object':'Tally', 'message':'%s joined Tally.' % (actor.user.username)}
        tags = []       # notify no one
    elif action=='edited':
        os = get_object_message(actor,action,obj,'')
        tags = list(obj.collaborators.all()) + [obj.owner]      # notify Test or TestInstance owner/collaborators
    elif action=='ran':
        if not isinstance(obj,TestInstance):
            raise Exception('create_log_entry: Object must be a TestInstance.')
        actor = obj.owner         # owner runs TestInstance
        os = get_object_message(actor,action,obj,'')
        tags = list(obj.test.collaborators.all()) + list(obj.collaborators.all()) + [obj.test.owner, obj.owner]     # notify Test and TestInstance owner/collaborators
    elif action=='created':
        os = get_object_message(actor,action,obj,'')
        ts = obj.create_time                    # make log timestamp match object timestamp
        tags = [obj.owner]                      # notify Test or TestInstance owner
        if os['object']=='Test Instance':       # if TestInstance, additionally notify Test owner/collaborators
            tags = tags + list(obj.test.collaborators.all()) + [obj.test.owner]
    elif action=='deleted':
        os = get_object_message(actor,action,obj,' and all related objects')
        tags = list(obj.collaborators.all()) + [obj.owner]      # notify Test or TestInstance owner/collaborators
        if os['object']=='Test Instance':                       # if TestInstance, additionally notify Test owner/collaborators
            tags = tags + list(obj.test.collaborators.all()) + [obj.test.owner]
    elif action=='shared':
        share_list = get_collaborator_string(tags_arg)
        os = get_object_message(actor,action,obj,' with %s' % (share_list))
        tags = list(obj.collaborators.all()) + [obj.owner]      # notify Test or TestInstance owner/collaborators
    elif action=='unshared':
        os = get_object_message(actor,' is no longer collaborating on',obj,'')
        tags = list(obj.collaborators.all()) + [obj.owner]      # notify Test or TestInstance owner/collaborators
    else:
        raise Exception('create_log_entry: Invalid action.')
    tags.extend(tags_arg)       # make sure collaborators are tagged (in case log entry is created before collaborators are added)
    tags.append(actor)          # make sure actor is tagged
    tags = list(set(tags))      # make sure tags are unique
    le = LogEntry(actor=actor, action=action, object=os['object'], message=os['message'], timestamp=ts)
    le.save()
    for t in tags:
        tg = LogTag(log_entry=le, user=t)
        tg.save()

    
def get_object_message(actor,action,obj,words):
    if isinstance(obj,Test):
        object = 'Test'
        message = '%s %s Test:%s%s' % (actor.user.username, action, obj.title, words)
    elif isinstance(obj,TestInstance):
        object = 'Test Instance'
        message = '%s %s Test Instance %d of Test:%s%s' % (actor.user.username, action, obj.pk, obj.test.title, words)
    else:
        raise Exception('get_object_message: Object must be Test or TestInstance.')
    return {'object':object, 'message':message}
    

def get_collaborator_string(collaborators):
    C = len(collaborators)
    if C==0:
        raise Exception('get_collaborator_string: No collaborators specified.')
    elif C==1:
        collab_str = collaborators[0].user.username
    elif C==2:
        collab_str = '%s and %s' % (collaborators[0].user.username, collaborators[1].user.username)
    else:
        collab_str_list = []
        for ii,up in enumerate(collaborators):
            if ii==C-1:
                collab_str_list.append('and %s' % (up.user.username))
            else:
                collab_str_list.append('%s, ' % (up.user.username))
        collab_str = ''.join(collab_str_list)
    return collab_str
    
    
### Misc. functions
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
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
        return HttpResponse(json.dumps({'score':'E2'}))
    ti = get_object_or_404(TestInstance, pk=test_instance_id)
    return render_to_response('testtool/last_score.html', {'test_instance': ti.pk})
    

@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def about(request):
    return render_to_response('testtool/manager/about.html',context_instance=RequestContext(request))
    

@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def help(request):
    return render_to_response('testtool/manager/help.html',context_instance=RequestContext(request))
    
    

########################################################################################################
####################################         TEST FUNCTIONS         ####################################
########################################################################################################
class CreateTest(CreateView):
    model = Test
    form_class = CreateTestForm
    template_name = 'testtool/manager/create_test.html'
                
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(CreateTest, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        up = self.request.user.get_profile()
        self.object = form.save(commit=False)
        self.object.owner = up
        self.object.save()
        form.save_m2m()
        create_log_entry(up,'created',self.object)
        return HttpResponseRedirect(reverse('edit_test', args=(self.object.pk,)))
    
    
class EditTest(UpdateView):
    model = Test
    form_class = EditTestForm
    template_name = 'testtool/manager/edit_test.html'
                
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(EditTest, self).dispatch(*args, **kwargs)
    
    def get_object(self):
        return get_object_or_404(Test, pk=self.kwargs['test_id'])

    def form_valid(self, form):
        up = self.request.user.get_profile()
        self.object = form.save(commit=False)
        self.object.owner = up
        self.object.save()
        form.save_m2m()
        create_log_entry(up,'edited',self.object)
        try:
            save = self.request.POST['save']
        except KeyError:
            return HttpResponseRedirect(reverse('edit_test', args=(self.object.pk,))+'?alert=update')
        else:
            return HttpResponseRedirect(reverse('display_test', args=(self.object.pk,))+'?alert=save')            
    
    def get_context_data(self, **kwargs):
        context = super(EditTest, self).get_context_data(**kwargs)
        up = self.request.user.get_profile()
        if user_can('edit',up,self.object):
            context['files'] = Video.objects.filter(test=self.object)
            tc_data = []
            tc_set = TestCase.objects.filter(test=self.object)
            for tc in tc_set:
                tci = tc.testcaseitem_set.order_by('play_order')
                item = [tc,tci.values_list('video__filename','is_reference')]
                tc_data.append(item)
            context['tc_data'] = tc_data
            context['test_id'] = self.object.pk
            context['allow_modify'] = user_can('modify',up,self.object)
            if self.request.method == 'GET':
                try:
                    alert = self.request.GET['alert']
                except KeyError:
                    pass
                else:
                    if alert == 'update':
                        context['alert'] = 'Test is successfully updated.'
                        context['alert_class'] = 'success'
        else:
            context['error']   = 'You do not have permission to edit this test.'
        context['header']  = 'Test %d: %s' % (self.object.pk,self.object.title)
        return context


class DisplayTest(UpdateView):
    model = Test
    form_class = DisplayTestForm
    template_name = 'testtool/manager/display_test.html'
                
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(DisplayTest, self).dispatch(*args, **kwargs)
        
    def get_object(self):
        return get_object_or_404(Test, pk=self.kwargs['test_id'])
    
    def get_context_data(self, **kwargs):
        context = super(DisplayTest, self).get_context_data(**kwargs)
        up = self.request.user.get_profile()
        if user_can('view',up,self.object):
            tc_data = []
            tc_set = TestCase.objects.filter(test=self.object)
            for tc in tc_set:
                tci = tc.testcaseitem_set.order_by('play_order')
                item = [tc,tci.values_list('video__filename','is_reference')]
                tc_data.append(item)
            context['files']     = Video.objects.filter(test=self.object)
            context['tc_data']   = tc_data
            context['test_id']   = self.object.pk
            context['can_share'] = user_can('share',up,self.object)
            context['can_edit']  = user_can('edit',up,self.object)
            if self.request.method == 'GET':
                try:
                    alert = self.request.GET['alert']
                except KeyError:
                    pass
                else:
                    if alert == 'save':
                        context['alert'] = 'Test is successfully saved.'
                        context['alert_class'] = 'success'
        else:
            context['error'] = 'You do not have access to this test.'
        context['header'] = 'Test %d: %s' % (self.object.pk,self.object.title)
        return context

        
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def add_video(request, test_id):
    if request.method == 'POST':
        messages = {'0': 'Done', '1': 'Test does not exist', '2': 'No file provided', '3':'Video already exists', '4':'File type is not supported', '5':'Permission failed'}
        
        #checking for json data type
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
            
        try:
            t = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            status = 1;
        else:
            up = request.user.get_profile()
            if user_can('modify',up,t):
                try:
                    filename =  request.POST['filename']
                except KeyError:
                    status = 2; #TODO: should change when file upload is supported
                else:
                    if is_file_supported(filename):
                        try:
                            f = Video.objects.get(test=t, filename=filename)
                        except Video.DoesNotExist:
                            f = Video.objects.create(test=t, filename=filename)
                            if t.method == 'SSCQE':
                                tc = TestCase.objects.create(test=t)
                                TestCaseItem.objects.create(test_case=tc,video=f,play_order=1)
                            create_log_entry(up,'edited',t)
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
def delete_video(request, video_id):
    if request.method == 'POST':
        messages = {'0': 'Done', '1': 'Video does not exist', '5': 'Permission failed'}
        
        #checking for json data type
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
            
        try:
            f = Video.objects.get(pk=video_id)
            t = f.test
        except Video.DoesNotExist:
            status = 1;
        else:
            up = request.user.get_profile()
            if user_can('modify',up,t):
                # delete associated test cases first
                for tc in TestCase.objects.filter(videos=f):
                    tc.delete()
                # finally delete the video
                f.delete()
                create_log_entry(up,'edited',t)
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
@user_passes_test(has_user_profile)
def add_test_case(request, test_id):
    t = get_object_or_404(Test, pk=test_id)
    up = request.user.get_profile()
    if user_can('modify',up,t):
        if t.method == 'DSIS' or t.method == 'DSCQS':
            args = add_test_case_discrete(request, t, up)
            create_log_entry(up,'edited',t)
        elif t.method == 'SSCQE':
            args = add_test_case_SSCQE(request, t, up)
            create_log_entry(up,'edited',t)
        else:
            args = { 'status': 'error',
                     'error' : 'Test mode creation for %s is not supported.' % (t.method) }
    else:
        args = { 'status': 'error',
                 'error' : 'You cannot add a new test case to this test.' }
    args['test_id']     = t.pk
    args['header']      = 'Add new test case to Test %d: %s' % (t.pk, t.title)
    if args['status'] == 'done': # success
        return HttpResponseRedirect(reverse('edit_test', args=(test_id,)))
    else:
        return render_to_response('testtool/manager/create_test_case.html', args, context_instance=RequestContext(request))

        
def add_test_case_discrete(request, test, user_profile):
    if request.method == 'POST':
        form = CreateTestCaseFormDiscrete(request.POST)
        if form.is_valid():
            tc = TestCase.objects.create(test=test)
            data = form.cleaned_data
            f1 = data['filename1']
            f2 = data['filename2']
            for ii in range(0,2): # repeat each video twice
                if test.method == 'DSIS':
                    TestCaseItem.objects.create(test_case=tc,video=f1,play_order=1+ii*2,is_reference=True)
                    TestCaseItem.objects.create(test_case=tc,video=f2,play_order=2+ii*2)
                else:
                    # generate play order
                    rand_order = range(1,3)
                    random.shuffle(rand_order)
                    TestCaseItem.objects.create(test_case=tc,video=f1,play_order=rand_order[0]+ii*2)
                    TestCaseItem.objects.create(test_case=tc,video=f2,play_order=rand_order[1]+ii*2)
            return {'status': 'done'}
    else:
        if Video.objects.filter(test=test):
            form = CreateTestCaseFormDiscrete()            
        else:
            return { 'status': 'error',
                     'error': 'There are no videos associated with this test.'}

    form.fields['filename1'].queryset = form.fields['filename1'].queryset.filter(test=test)
    form.fields['filename2'].queryset = form.fields['filename2'].queryset.filter(test=test)
        
    if test.method == 'DSIS':
        form.fields['filename1'].label = 'Reference video'
        form.fields['filename2'].label = 'Test video'
    elif test.method == 'DSCQS':
        form.fields['filename1'].label = 'First video'
        form.fields['filename2'].label = 'Second video'
    return {'status': 'incomplete', 'form': form}

    
def add_test_case_SSCQE(request, test, user_profile):
    if request.method == 'POST':
        form = CreateTestCaseFormSSCQE(request.POST)
        if form.is_valid():
            tc = TestCase.objects.create(test=test)
            data = form.cleaned_data
            f = data['filename']
            TestCaseItem.objects.create(test_case=tc,video=f,play_order=1)
            return {'status': 'done'}
    else:
        # if there are no videos associated with the Test, redirect to update view
        if Video.objects.filter(test=test):
            form = CreateTestCaseFormSSCQE()
        else:
            return { 'status': 'error',
                     'error': 'There are no videos associated with this test.'}

    form.fields['filename'].queryset = form.fields['filename'].queryset.filter(test=test)
    form.fields['filename'].label = 'Video'
    return {'status': 'incomplete', 'form': form}
    
    
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def delete_test_case(request, test_case_id):
    if request.method == 'POST':
        messages = {'0': 'Done', '1': 'Test case does not exist', '5': 'Permission failed'}
        
        #checking for json data type
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
            
        try:
            tc = TestCase.objects.get(pk=test_case_id)
            t = tc.test
        except TestCase.DoesNotExist:
            status = 1;
        else:
            up = request.user.get_profile()
            if user_can('modify',up,t):
                tc.delete()
                create_log_entry(up,'edited',t)
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
@user_passes_test(has_user_profile)
def list_tests(request):
    up = request.user.get_profile()
    tests = Test.objects.all()
    t_data = []
    for t in tests:
        status = user_status(up,t)
        if status != 'None':
            t_data.append([t.title, status, t.create_time, t.pk])
    if len(t_data)==0:
        args = { 'error': 'You do not own or have access to any tests.' }
    else:
        args = { 't_data': t_data }
    return render_to_response('testtool/manager/list_tests.html', args, context_instance=RequestContext(request))
        
        
        
########################################################################################################
###############################         TEST INSTANCE FUNCTIONS         ################################
########################################################################################################
class CreateTestInstance(CreateView):
    model = TestInstance
    form_class = CreateTestInstanceForm
    initial = {'schedule_time':datetime.datetime.now()}
    template_name = 'testtool/manager/create_test_instance.html'
                
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(CreateTestInstance, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        up = self.request.user.get_profile()
        # create new instance
        self.object = form.save(commit=False)     # create new test instance from form, but don't save it yet
        self.object.test = get_object_or_404(Test, pk=self.kwargs['test_id'])         # add in excluded fields
        self.object.owner = up       # when an admin is logged in, they are not recognized as a user!!!!!!
        self.object.path = self.object.path.replace("\\","/").rstrip("/")     # make sure path has only forward slashes and no trailing slashes
        self.object.key = ''.join([random.choice(string.ascii_letters+string.digits) for x in range(20)])
        self.object.save()           # save the new instance
        form.save_m2m()
        create_log_entry(up,'created',self.object)
        # create new test case instances
        tc_all = self.object.test.testcase_set.all()
        repeat = tc_all.count()*[1]            # repeat each test case 1 time for testing; this list will come from somewhere else eventually
        rand_order = range(1,sum(repeat)+1)    # play order starts from 1
        random.shuffle(rand_order)
        idx = 0
        for ii in range(0,tc_all.count()):
            for jj in range(0,repeat[ii]):
                tci = TestCaseInstance(test_instance=self.object, test_case=tc_all[ii], play_order=rand_order[idx])
                idx += 1
                tci.save()
        return HttpResponseRedirect(reverse('display_test_instance', args=(self.object.test.pk, self.object.pk))+'?alert=new')
                    
    def get_context_data(self, **kwargs):
        context = super(CreateTestInstance, self).get_context_data(**kwargs)
        t = get_object_or_404(Test, pk=self.kwargs['test_id'])
        perm = user_can('create',self.request.user.get_profile(),t,True)
        if perm['granted']:
            context['header']   = 'Create New Test Instance of Test %d: %s' % (t.pk, t.title)
            context['enrolled'] = UserProfile.objects.none()
            context['test_id']  = self.kwargs['test_id']
        else:
            context['header'] = 'Create New Test Instance'
            if not perm['perm_user']:
                context['error']  = 'You do not have permission to create a test instance of this test.'
            elif not perm['perm_obj']:
                context['error']  = 'The test does not have any test cases, so instances of this test cannot be created.'
        return context
        
        
class EditTestInstance(UpdateView):
    model = TestInstance
    form_class = CreateTestInstanceForm
    template_name = 'testtool/manager/edit_test_instance.html'
    
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(EditTestInstance, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('display_test_instance', args=(self.kwargs['test_id'], self.kwargs['test_instance_id']))+'?alert=edit'
        
    def get_object(self):
        return get_object_or_404(TestInstance, pk=self.kwargs['test_instance_id'], test__id=self.kwargs['test_id'])   # ensures that test instance belongs to test
    
    # def form_valid(self, form):
        # create_log_entry(self.request.user.get_profile(),'edited',self.object)
        # return super(EditTestInstance, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EditTestInstance, self).get_context_data(**kwargs)
        if user_can('edit',self.request.user.get_profile(),self.object):
            context['header']           = 'Edit Test Instance %d of Test %d: %s' % (self.object.pk, self.object.test.pk, self.object.test.title)
            context['enrolled']         = self.object.subjects.all()
            context['test_id']          = self.kwargs['test_id']
            context['test_instance_id'] = self.kwargs['test_instance_id']
        else:
            context['header'] = 'Edit Test Instance'
            context['error']  = 'You do not have permission to edit this test instance.'
        return context
        
        
class DisplayTestInstance(UpdateView):
    model = TestInstance
    form_class = DisplayTestInstanceForm
    template_name = 'testtool/manager/display_test_instance.html'
    
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(DisplayTestInstance, self).dispatch(*args, **kwargs)
        
    def get_object(self):
        return get_object_or_404(TestInstance, pk=self.kwargs['test_instance_id'], test__id=self.kwargs['test_id'])   # ensures that test instance belongs to test
                    
    def get_context_data(self, **kwargs):
        context = super(DisplayTestInstance, self).get_context_data(**kwargs)
        up = self.request.user.get_profile()
        if user_can('view',up,self.object):
            alert_str = ''
            alert_class = 'success'
            if self.request.method == 'GET':
                try:
                    alert = self.request.GET['alert']
                except KeyError:
                    alert = ''
                if alert == 'new':
                    alert_str = 'Test instance successfully created.'
                    alert_class = 'success'
                elif alert == 'edit':
                    alert_str = 'Test instance successfully edited.'
                    alert_class = 'success'
                elif alert == 'share':
                    alert_str = 'New collaborators successfully added.'
                    alert_class = 'success'
                elif alert == 'delete_err':
                    alert_str = 'Only the test instance owner can delete a test instance, after all collaborators have removed themselves.'
                    alert_class = 'error'
                elif alert == 'unshare_err':
                    alert_str = 'You are not a collaborator on this test instance.'
                    alert_class = 'error'
            tci_set = self.object.testcaseinstance_set.order_by('pk')
            tc_set = self.object.test.testcase_set.order_by('pk')
            rand = []
            for tc in tc_set:
                rand.append(tci_set.filter(test_case=tc).values_list('play_order',flat=True))
            context['header']           = 'Test Instance %d of Test %d: %s' % (self.object.pk, self.object.test.pk, self.object.test.title)
            context['test_id']          = self.kwargs['test_id']
            context['test_instance_id'] = self.kwargs['test_instance_id']
            context['rand']             = str(rand)
            context['can_share']        = user_can('share',up,self.object)
            context['can_export']       = user_can('export',up,self.object)
            context['can_edit']         = user_can('edit',up,self.object)
            context['can_delete']       = user_can('delete',up,self.object)
            context['can_unshare']      = user_can('unshare',up,self.object)
            context['can_run']          = user_can('run',up,self.object)
            context['alert']            = alert_str
            context['alert_class']      = alert_class
        else:
            context['header']           = 'Test Instance %d of Test %d' % (self.object.pk, self.object.test.pk)
            context['test_id']          = self.kwargs['test_id']
            context['test_instance_id'] = self.kwargs['test_instance_id']
            context['error']            = 'You do not have access to this test instance.'
        return context
        
        
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def delete_test_instance(request, test_id, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id, test__id=test_id)   # ensures that test instance belongs to test
    if request.method=='POST':
        up = request.user.get_profile()
        if user_can('delete',up,ti):
            create_log_entry(up,'deleted',ti)
            ti.delete()
            return HttpResponseRedirect(reverse('list_test_instances', args=(test_id))+'?alert=delete&pk='+str(test_instance_id))
        else:
            return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk, ti.pk))+'?alert=delete_err')
    else:
        return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk, ti.pk)))

        
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def unshare_test_instance(request, test_id, test_instance_id):
    ti = get_object_or_404(TestInstance, pk=test_instance_id, test__id=test_id)   # ensures that test instance belongs to test
    if request.method=='POST':
        up = request.user.get_profile()
        if user_can('unshare',up,ti):
            ti.collaborators.remove(up)
            create_log_entry(up,'unshared',ti)
            return HttpResponseRedirect(reverse('list_test_instances', args=(test_id))+'?alert=unshare&pk='+str(test_instance_id))
        else:
            return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk, ti.pk))+'?alert=unshare_err')
    else:
        return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk, ti.pk)))        


@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def list_test_instances(request,test_id):
    alert_str = ''
    alert_class = 'success'
    if request.method == 'GET':
        try:
            alert = request.GET['alert']
            pk = int(request.GET['pk'])
            if alert == 'delete':
                alert_str = 'Test Instance %d successfully deleted.' % (pk)
            elif alert == 'unshare':
                alert_str = 'You are no longer collaborating on Test Instance %d.' % (pk)
        except KeyError:
            pass
    up = request.user.get_profile()
    t = get_object_or_404(Test, pk=test_id)
    ti_set = TestInstance.objects.filter(test=t)
    ti_data = []
    for ti in ti_set:
        status = user_status(up,ti)
        if status != 'None':
            ti_data.append([ti.pk, status, ti.get_status(), ti.subjects.count()])
    if len(ti_data)==0:
        if user_status(up,t) in ['Owner', 'Collaborator']:
            errMsg = 'No instances of this test exist.'
        else:
            errMsg = 'No instances of this test exist to which you have access.'
        args = { 'error': errMsg }
    else:
        args = { 'ti_data': ti_data }
    args['header']      = 'Test Instances of Test %d: %s' % (t.pk, t.title)
    args['test_id']     = t.pk
    args['alert']       = alert_str
    args['alert_class'] = alert_class
    return render_to_response('testtool/manager/list_test_instances.html', args, context_instance=RequestContext(request))
   

@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def run_test_instance(request, test_id, test_instance_id):
    # when this page is hit, it places the test instance key in the URL for the desktop app to extract (by redirecting to itself with the key as a GET parameter).  If the key is already present, it checks if the key matches the database and then renders the page.  Otherwise, it shows an error message.
    key_name = 'key'
    if request.method == 'GET':
        ti = get_object_or_404(TestInstance, pk=test_instance_id, test__id=test_id)
        up = request.user.get_profile()
        perm = user_can('run',up,ti,True)
        if perm['granted']:
            try:
                key = request.GET[key_name]
            except KeyError:
                return HttpResponseRedirect(reverse('run_test_instance', args=(test_id, test_instance_id))+'?%s=%s'%(key_name,ti.key))
            else:
                if key == ti.key:
                    return render_to_response('testtool/manager/run_test_instance.html', context_instance=RequestContext(request))
                else:
                    msg = 'Invalid key.'
        elif ti.get_status() == 'Complete':
            msg = 'This test instance has already been run.'
        else:
            if not perm['perm_user']:
                msg = 'You do not have permission to run this test instance.'
            elif not perm['perm_obj']:
                msg = 'This test instance is invalid and cannot be run.'
        return render_to_response('testtool/manager/run_test_instance.html',{ 'error': msg }, context_instance=RequestContext(request))
    return HttpResponseRedirect(reverse('run_test_instance', args=(test_id)))


    
########################################################################################################
#############################         SHARING/EXPORTING FUNCTIONS         ##############################
########################################################################################################
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def export_data(request):
    test_id_ran = TestInstance.objects.exclude(run_time=None).values_list('test__id',flat=True).distinct()    # pk's of all tests that have test instances that have been run
    up = request.user.get_profile()
    # of these, find the ones of which the user is an owner or collaborator
    t_valid = []
    ti_valid = []
    t_valid_id = []
    ti_valid_id = []
    for id in test_id_ran:                              # for each run test, find its run instances
        t_ran = Test.objects.get(pk=id)
        t_ran_ti = t_ran.testinstance_set.exclude(run_time=None)
        tmp_list = []
        tmp_list_id = []
        for ti in t_ran_ti:
            if user_can('export',up,ti):
                tmp_list.append(ti)
                tmp_list_id.append(ti.pk)
        if len(tmp_list) > 0:
            t_valid.append(t_ran)
            ti_valid.append(tmp_list)
            ti_valid_id.append(tmp_list_id)
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
    #
    # doesn't do any checking for existence of objects (i.e. try-catch)!!!
    # 
    if request.method == 'POST':
        try:
            t_id = int(request.POST['test_select'])
            ti_id = int(request.POST['test_instance_select'])
            format_list = request.POST.getlist('format')
        except KeyError:
            return HttpResponse('Please select a choice')
        else:
            up = request.user.get_profile()
            ti = get_object_or_404(TestInstance, pk=ti_id)
            if user_can('export',up,ti):        # check that user can export test instances
                if len(format_list) == 0:
                    response = HttpResponse('Please select a data format')
                else:
                    raw_data = get_raw_data(ti)
                    if len(format_list) == 1:
                        data = get_formatted_data(raw_data, format_list[0])
                        response = HttpResponse(content_type=data['type'])
                        response['Content-Disposition'] = 'attachment; filename=%s_instance_%d.%s' % (ti.test.title, ti_id, data['ext'])
                        response.write(data['buffer'].getvalue())
                        data['buffer'].close()
                    else:
                        zip_buffer = StringIO()
                        zip = zipfile.ZipFile(zip_buffer,'a',zipfile.ZIP_DEFLATED)
                        for format in format_list:
                            data = get_formatted_data(raw_data, format)
                            zip.writestr('%s_instance_%d.%s' % (ti.test.title, ti_id, data['ext']), data['buffer'].getvalue())
                            data['buffer'].close()
                        for file in zip.filelist:       # fix for Linux zip files read in Windows (http://bitkickers.blogspot.com/2010/07/django-zip-files-create-dynamic-in.html)
                            file.create_system = 0
                        zip.close()
                        response = HttpResponse(content_type='application/zip')
                        response['Content-Disposition'] = 'attachment; filename=%s_instance_%d.zip' % (ti.test.title, ti_id)
                        response.write(zip_buffer.getvalue())
                        zip_buffer.close()
                return response
            else:
                return HttpResponse('You do not have permission to export this test instance.')
    return HttpResponseRedirect(reverse('export_data'))


def get_raw_data(ti):
    # this should eventually extract the data out of the test instance so that the database only needs to be accessed once for returning a variety of formats
    return ti
    
    
def get_formatted_data(raw_data, format):
    buffer = StringIO()
    if format == 'report':
        data = format_as_report(raw_data,buffer)
        type = 'application/pdf'
        ext = 'pdf'
    elif format == 'csv':
        data = format_as_csv(raw_data,buffer)
        type = 'text/csv'
        ext = 'csv'
    elif format == 'matlab':
        data = format_as_matlab(raw_data,buffer)
        type = 'application/octet-stream'
        ext = 'mat'
    elif format == 'python':
        data = format_as_python(raw_data,buffer)
        type = 'text/plain'
        ext = 'py'
    return { 'buffer': data, 'type': type, 'ext': ext }
    
    
def format_as_report(raw_data, buffer):
    #http://www.djangobook.com/en/beta/chapter11/
    return buffer
    
    
def format_as_csv(ti, buffer):
    # setup
    writer = csv.writer(buffer)
    method = ti.test.method
    # write header
    writer.writerow(['Test', ti.test.title])
    writer.writerow(['Method', ti.test.method])
    writer.writerow(['Test Notes', ti.test.description])
    writer.writerow(['Test Instance ID', ti.pk])
    writer.writerow(['Run Time', ti.run_time])
    writer.writerow(['Test Instance Notes', ti.description])
    writer.writerow(['Location', ti.location])
    writer.writerow('')
    # write method-specific data
    if method == 'SSCQE':
        all_subjects = ti.subjects.all()
        all_test_cases = ti.test.testcase_set.all()
        for subject in all_subjects:
            writer.writerow(['User Name',  subject.user.username])
            writer.writerow(['First Name', subject.user.first_name])
            writer.writerow(['Last Name',  subject.user.last_name])
            writer.writerow(['Birth Date', subject.birth_date])
            writer.writerow(['Gender',     subject.sex])
            writer.writerow('')
            for ii,tc in enumerate(all_test_cases):
                all_tci = tc.testcaseinstance_set.filter(test_instance=ti).all()
                for tci in all_tci:
                    scores = tci.scoresscqe_set.filter(subject=subject).order_by('pk')
                    ts = scores.values_list('timestamp',flat=True)
                    val = scores.values_list('value',flat=True)
                    writer.writerow(['Test Case', ii+1])
                    writer.writerow(['Play Order', tci.play_order])
                    writer.writerow(['Timestamp'] + list(ts))
                    writer.writerow(['Score'] + list(val))
                    writer.writerow('')
            writer.writerow('')
            writer.writerow('')
    elif method == 'DSIS':
        subject_data = ti.subjects.order_by('pk').values_list
        user_names = subject_data('user__username',flat=True)
        writer.writerow(['User Name',  ''] + list(user_names))
        writer.writerow(['First Name', ''] + list(subject_data('user__first_name',flat=True)))
        writer.writerow(['Last Name',  ''] + list(subject_data('user__last_name',flat=True)))
        writer.writerow(['Birth Date', ''] + list(subject_data('birth_date',flat=True)))
        writer.writerow(['Gender',     ''] + list(subject_data('sex',flat=True)))
        writer.writerow('')
        writer.writerow(['Test Case', 'Play Order'] + ['Score: ' + u for u in user_names])
        all_test_cases = ti.test.testcase_set.all()
        for ii,tc in enumerate(all_test_cases):
            all_tci = tc.testcaseinstance_set.filter(test_instance=ti).all()
            for jj,tci in enumerate(all_tci):
                subj_scores = []
                for pk in subject_data('pk',flat=True):     # have to loop through subjects in case of empty scores
                    try:
                        obj = ScoreDSIS.objects.get(test_case_instance=tci,subject__id=pk)
                        val = obj.value
                    except ScoreDSIS.DoesNotExist:
                        val = ''
                    subj_scores.append(val)
                writer.writerow([str(ii+1), tci.play_order] + subj_scores)
    return buffer
    
    
def format_as_matlab(raw_data, buffer):
    data = process_mat_py_data(raw_data)
    io.savemat(buffer,{ 'data': data }, oned_as='column')
    return buffer

    
def format_as_python(raw_data, buffer):
    data = process_mat_py_data(raw_data)
    buffer.write('data = %s\n' % str(data))
    return buffer

    
def process_mat_py_data(ti):
    subject_data = []
    all_subjects = ti.subjects.all()
    all_test_cases = ti.test.testcase_set.all()
    method = ti.test.method
    for subject in all_subjects:
        subj = { 'username':   subject.user.username,
                 'first_name': subject.user.first_name,
                 'last_name':  subject.user.last_name,
                 'dob':        str(subject.birth_date),
                 'gender':     subject.sex }
        test_cases = []
        for ii,tc in enumerate(all_test_cases):
            all_tci = tc.testcaseinstance_set.filter(test_instance=ti).order_by('pk').all()
            instances = []
            for tci in all_tci:     # convert to floats for Matlab
                try:
                    if method == 'SSCQE':
                        subj_score = tci.scoresscqe_set.filter(subject=subject).order_by('pk')
                        ts = subj_score.values_list('timestamp',flat=True)
                        val = subj_score.values_list('value',flat=True)
                        score = { 'timestamp': [str(t) for t in list(ts)], 'value': [float(v) for v in list(val)] }
                    elif method == 'DSIS':
                        subj_score = tci.scoredsis_set.get(subject=subject)
                        score = { 'value': float(subj_score.value) }
                    elif method == 'DSCQS':
                        subj_score = tci.scoredscqs_set.get(subject=subject)
                        score = { 'value1': float(subj_score.value1), 'value2': float(subj_score.value2) }
                    else:
                        raise Exception('get_raw_data: invalid test method.')
                except ObjectDoesNotExist:
                    score = []
                instances.append({ 'test_case': ii+1,
                                   'play_order': tci.play_order,
                                   'score': score })
            test_cases.append(instances)
        subj['test_cases'] = test_cases
        subject_data.append(subj)
    return subject_data

    
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def share_test(request):
    up = request.user.get_profile()
    t_own = Test.objects.filter(owner=up)
    t_share = list(set(list(t_own.values_list('pk',flat=True)) + list(TestInstance.objects.filter(owner=up).values_list('test__id',flat=True))))
    
    # group test instances by test
    t_valid = []
    ti_valid = []
    t_valid_id = []
    ti_valid_id = []
    for id in t_share:      # all Tests that can be shared or have TestInstances that can be shared
        t = Test.objects.get(pk=id)
        tmp = t.testinstance_set.filter(Q(test__owner=up) | Q(owner=up)).distinct()
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
        share_test_with.append(list(all_testers.exclude(userprofile=t.owner).exclude(userprofile__in=t.collaborators.all())))
    share_test_instance_with = []    # users with whom test instances can be shared (double-nested list, i.e. [[[u1,u2,u3],[u1,u4]], [[u2,u3],[u3,u4]]]
    for ti_list in ti_valid:
        sw1 = []
        for ti in ti_list:
            sw1.append(list(all_testers.exclude(userprofile=ti.owner).exclude(userprofile__in=ti.collaborators.all()).exclude(userprofile=ti.test.owner).exclude(userprofile__in=ti.test.collaborators.all())))
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
                        return render_to_response('testtool/manager/share_test.html', 'You do not have permission to share this test instance.', context_instance=RequestContext(request))
                else:
                    return render_to_response('testtool/manager/share_test.html', 'You do not have permission to share this test.', context_instance=RequestContext(request))
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
            t_id = int(request.POST['test_select'])
            share_with = request.POST.getlist('tester_select')
        except KeyError:
            return HttpResponse('please select a choice')
        else:
            if len(share_with) == 0:
                return HttpResponse('please select a choice')
            up = request.user.get_profile()
            if mode == 'share_test':
                t = get_object_or_404(Test, pk=t_id)
                if user_can('share',up,t):                              # check that user can share test
                    share_list = []
                    for id in share_with:                               # add collaborators to test
                        u = get_object_or_404(UserProfile, pk=int(id))
                        share_list.append(u)
                    t.collaborators.add(*share_list)
                    create_log_entry(up,'shared',t,share_list)
                    return HttpResponseRedirect(reverse('display_test', args=(t.pk,)))
                else:
                    return HttpResponse('You do not have permission to share this test.')
            elif mode == 'share_test_instance':
                try:
                    ti_id = int(request.POST['test_instance_select'])
                except KeyError:
                    return HttpResponse('please select a test instance')
                else:
                    ti = get_object_or_404(TestInstance, pk=ti_id, test__id=t_id)   # ensures that test instance belongs to test
                    if user_can('share',up,ti):                                     # check that user can share test instance
                        share_list = []
                        for id in share_with:                                       # add collaborators to test instance
                            u = get_object_or_404(UserProfile, pk=int(id))
                            share_list.append(u)
                        ti.collaborators.add(*share_list)
                        create_log_entry(up,'shared',ti,share_list)
                        return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk,ti.pk,))+'?alert=share')
                    else:
                        return HttpResponse('You do not have permission to share this test instance.')
            else:
                return HttpResponse('mode must be ''share_test'' or ''share_test_instance''')
    else:
        return HttpResponseRedirect(reverse('share_test'))
