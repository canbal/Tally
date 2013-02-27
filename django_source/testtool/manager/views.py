from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.conf import settings
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
    zero_ti   = TestInstance.objects.filter(test=t).count() == 0
    zero_coll = t.collaborators.all().count() == 0
    zero_ti_coll = TestInstance.objects.filter(test=t,collaborators=up).count() == 0
    zero_ti_coll = zero_ti_coll and (TestInstance.objects.filter(test=t,owner=up).count() == 0)
    exclude_list = [t.owner.pk] + [x.pk for x in t.collaborators.all()]
    available_collaborators = get_available_collaborators(t)
    obj_policy = { 'view':    True,
                   'export':  t.has_data(),
                   'share':   available_collaborators.count() > 0,
                   'create':  t.testcase_set.count() > 0,
                   'edit':    True,
                   'modify':  zero_ti and zero_coll,
                   'delete':  zero_ti and zero_coll,
                   'unshare': zero_ti_coll }
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
    available_collaborators = get_available_collaborators(ti)
    obj_policy = { 'view':    True,
                   'export':  ti.has_data(),
                   'share':   available_collaborators.count() > 0,
                   'run':     ti.is_active(),
                   'edit':    True,
                   'delete':  ti.collaborators.count() == 0,
                   'unshare': True }
    return { 'status': status[idx], 'perm_policy': perm_policy, 'obj_policy': obj_policy }


def set_alert(request,alert,pk=None):
    request.session['alert'] = alert
    if pk is not None:
        request.session['pk'] = pk
    
    
def get_alert_context(request,obj):
    # read the alert from request, and clear it so that it doesn't persist
    alert = request.session.get('alert',[])
    obj_pk = str(request.session.get('pk',''))
    if 'alert' in request.session:
        del request.session['alert']
    if 'pk' in request.session:
        del request.session['pk']
    # if there exists any alerts build right context
    context = {'alert':'','alert_class':''}
    if alert:
        if isinstance(obj,Test):
            obj_str = 'Test'
        elif isinstance(obj,TestInstance):
            obj_str = 'Test Instance'
        else:
            raise Exception('get_alert_context: Must pass Test or TestInstance object.')
        if alert == 'new':
            context['alert'] = '%s successfully created.' % (obj_str)
            context['alert_class'] = 'success'
        elif alert == 'edit':
            context['alert'] = '%s %s successfully edited.' % (obj_str,obj_pk)
            context['alert_class'] = 'success'
        elif alert == 'share':
            context['alert'] = 'New collaborators successfully added to %s %s.' % (obj_str,obj_pk)
            context['alert_class'] = 'success'
        elif alert == 'update':
            context['alert'] = '%s %s successfully updated.' % (obj_str,obj_pk)
            context['alert_class'] = 'success'
        elif alert == 'save':
            context['alert'] = 'Changes to %s %s are successfully saved.' % (obj_str,obj_pk)
            context['alert_class'] = 'success'
        elif alert == 'delete':
            context['alert'] = '%s %s successfully deleted.' % (obj_str,obj_pk)
            context['alert_class'] = 'success'
        elif alert == 'unshare':
            context['alert'] = 'You are no longer collaborating on %s %s.' % (obj_str,obj_pk)
            context['alert_class'] = 'success'            
        elif alert == 'delete_err':
            context['alert'] = 'A %s can only be deleted by its owner, after all collaborators have removed themselves.' % (obj_str)
            context['alert_class'] = 'error'
        elif alert == 'unshare_err':
            context['alert'] = 'You are not a collaborator on this %s.' % (obj_str)
            context['alert_class'] = 'error'
    return context


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
        os = {'object':'Tally', 'message':'%s joined Tally' % (actor.user.username)}
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
            set_alert(self.request,'update',self.object.pk)
            return HttpResponseRedirect(reverse('edit_test', args=(self.object.pk,)))
        else:
            set_alert(self.request,'save')
            return HttpResponseRedirect(reverse('display_test', args=(self.object.pk,)))
    
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
            context.update(get_alert_context(self.request,self.object))
        else:
            context['error'] = 'You do not have permission to edit this test.'
        context['header'] = 'Test %d: %s' % (self.object.pk,self.object.title)
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
            context['files']       = Video.objects.filter(test=self.object)
            context['tc_data']     = tc_data
            context['test_id']     = self.object.pk
            context['ti_exist']    = TestInstance.objects.filter(test=self.object).count() > 0
            context['can_share']   = user_can('share',up,self.object)
            context['can_export']  = user_can('export',up,self.object)
            context['can_edit']    = user_can('edit',up,self.object)
            context['can_delete']  = user_can('delete',up,self.object)
            context['can_unshare'] = user_can('unshare',up,self.object)
            context['can_create']  = user_can('create',up,self.object)
            context['header']      = 'Test %d: %s' % (self.object.pk,self.object.title)
            context.update(get_alert_context(self.request,self.object))
        else:
            context['error'] = 'You do not have access to this test.'
            context['header'] = 'Test %d' % (self.object.pk)
        return context

        
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def unshare_delete_test(request, test_id, action):
    if action not in ['unshare', 'delete']:
        raise Exception('unshare_delete_test: invalid action.')
    t = get_object_or_404(Test, pk=test_id)
    if request.method=='POST':
        up = request.user.get_profile()
        if user_can(action,up,t):
            create_log_entry(up,action+'d',t)
            if action=='unshare':
                t.collaborators.remove(up)
            elif action=='delete':
                t.delete()
            set_alert(request,action,test_id)
            return HttpResponseRedirect(reverse('list_tests'))
        else:
            set_alert(request,action+'_err')
            return HttpResponseRedirect(reverse('display_test', args=(test_id,)))
    else:
        return HttpResponseRedirect(reverse('display_test', args=(test_id,)))    

        
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
                            # # uncomment to enable adding test cases automatically for SSCQE
                            # if t.method == 'SSCQE':
                            #     tc = TestCase.objects.create(test=t)
                            #     TestCaseItem.objects.create(test_case=tc,video=f,play_order=1)
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
            data = form.cleaned_data
            f1 = data['filename1']
            f2 = data['filename2']
            r  = data['repeat']
            tc = TestCase.objects.create(test=test,repeat=r)
            # generate play order for DSCQS
            rand_order = range(1,3)
            random.shuffle(rand_order)
            for ii in range(0,2): # repeat each video twice
                if test.method == 'DSIS':
                    TestCaseItem.objects.create(test_case=tc,video=f1,play_order=1+ii*2,is_reference=True)
                    TestCaseItem.objects.create(test_case=tc,video=f2,play_order=2+ii*2)
                else:
                    TestCaseItem.objects.create(test_case=tc,video=f1,play_order=rand_order[0]+ii*2,is_reference=True)
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
    return {'status': 'incomplete', 'form': form}

    
def add_test_case_SSCQE(request, test, user_profile):
    if request.method == 'POST':
        form = CreateTestCaseFormSSCQE(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            f = data['filename']
            r = data['repeat']
            tc = TestCase.objects.create(test=test,repeat=r)
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
    args.update(get_alert_context(request,Test()))
    return render_to_response('testtool/manager/list_tests.html', args, context_instance=RequestContext(request))
        
        
        
########################################################################################################
###############################         TEST INSTANCE FUNCTIONS         ################################
########################################################################################################
class CreateTestInstance(CreateView):
    model = TestInstance
    form_class = CreateEditTestInstanceForm
    initial = {'schedule_time':datetime.datetime.now()}
    template_name = 'testtool/manager/create_edit_test_instance_share.html'
                
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
        repeat = []
        for tc in tc_all:
            repeat.append(tc.repeat)
        rand_order = range(1,sum(repeat)+1)    # play order starts from 1
        random.shuffle(rand_order)
        idx = 0
        for ii in range(0,tc_all.count()):
            for jj in range(0,repeat[ii]):
                tci = TestCaseInstance(test_instance=self.object, test_case=tc_all[ii], play_order=rand_order[idx])
                idx += 1
                tci.save()
        set_alert(self.request,'new')
        return HttpResponseRedirect(reverse('display_test_instance', args=(self.object.test.pk, self.object.pk,)))
                    
    def get_context_data(self, **kwargs):
        context = super(CreateTestInstance, self).get_context_data(**kwargs)
        t = get_object_or_404(Test, pk=self.kwargs['test_id'])
        perm = user_can('create',self.request.user.get_profile(),t,True)
        if perm['granted']:
            context['header']       = 'Create New Test Instance of Test %d: %s' % (t.pk, t.title)
            context['enrolled']     = UserProfile.objects.none()
            context['to_enroll']    = 'subjects'
            context['cancel_url']   = reverse('display_test', args=(self.kwargs['test_id'],))
            context['submit_value'] = 'Create'
        else:
            context['header'] = 'Create New Test Instance'
            if not perm['perm_user']:
                context['error']  = 'You do not have permission to create a test instance of this test.'
            elif not perm['perm_obj']:
                context['error']  = 'The test does not have any test cases, so instances of this test cannot be created.'
        return context
        
        
class EditTestInstance(UpdateView):
    model = TestInstance
    form_class = CreateEditTestInstanceForm
    template_name = 'testtool/manager/create_edit_test_instance_share.html'
    
    @method_decorator(login_required)
    @method_decorator(group_required('Testers'))
    @method_decorator(user_passes_test(has_user_profile))
    def dispatch(self, *args, **kwargs):
        return super(EditTestInstance, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        set_alert(self.request,'edit',self.kwargs['test_instance_id'])
        return reverse('display_test_instance', args=(self.kwargs['test_id'], self.kwargs['test_instance_id'],))
        
    def get_object(self):
        return get_object_or_404(TestInstance, pk=self.kwargs['test_instance_id'], test__id=self.kwargs['test_id'])
    
    def form_valid(self, form):
        create_log_entry(self.request.user.get_profile(),'edited',self.object)
        return super(EditTestInstance, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EditTestInstance, self).get_context_data(**kwargs)
        if user_can('edit',self.request.user.get_profile(),self.object):
            context['header']       = 'Edit Test Instance %d of Test %d: %s' % (self.object.pk, self.object.test.pk, self.object.test.title)
            context['enrolled']     = self.object.subjects.all()
            context['to_enroll']    = 'subjects'
            context['cancel_url']   = reverse('display_test_instance', args=(self.kwargs['test_id'],self.kwargs['test_instance_id'],))
            context['submit_value'] = 'Save'
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
            context.update(get_alert_context(self.request,self.object))
        else:
            context['header']           = 'Test Instance %d of Test %d' % (self.object.pk, self.object.test.pk)
            context['test_id']          = self.kwargs['test_id']
            context['test_instance_id'] = self.kwargs['test_instance_id']
            context['error']            = 'You do not have access to this test instance.'
        return context

        
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def unshare_delete_test_instance(request, test_id, test_instance_id, action):
    if action not in ['unshare', 'delete']:
        raise Exception('unshare_delete_test_instance: invalid action.')
    ti = get_object_or_404(TestInstance, pk=test_instance_id, test__id=test_id)   # ensures that test instance belongs to test
    if request.method=='POST':
        up = request.user.get_profile()
        if user_can(action,up,ti):
            create_log_entry(up,action+'d',ti)
            if action=='unshare':
                ti.collaborators.remove(up)
            elif action=='delete':
                ti.delete()
            set_alert(request,action,test_instance_id)
            return HttpResponseRedirect(reverse('list_test_instances', args=(test_id,)))
        else:
            set_alert(request,action+'_err')
            return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk, ti.pk,)))
    else:
        return HttpResponseRedirect(reverse('display_test_instance', args=(ti.test.pk, ti.pk,)))  
        

@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def list_test_instances(request,test_id):
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
    args['header'] = 'Test Instances of Test %d: %s' % (t.pk, t.title)
    args['test_id'] = t.pk
    args['can_create'] = user_can('create',up,t)
    args.update(get_alert_context(request,TestInstance()))
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
                return HttpResponseRedirect(reverse('run_test_instance', args=(test_id, test_instance_id,))+'?%s=%s'%(key_name,ti.key))
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
    return HttpResponseRedirect(reverse('run_test_instance', args=(test_id,)))


    
########################################################################################################
#############################         SHARING/EXPORTING FUNCTIONS         ##############################
########################################################################################################
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def share_export_obj(request,action,test_id,test_instance_id=None):
    if action not in ['share', 'export']:
        raise Exception('share_export_obj: invalid parameter action.')
    if test_instance_id is None:
        mode = 'Test'
        obj = get_object_or_404(Test, pk=test_id)
        hdr = '%s Test %d: %s' % (action, obj.pk, obj.title)
        cancel_url = reverse('display_test', args=(test_id,))
    else:
        mode = 'Test Instance'
        obj = get_object_or_404(TestInstance, pk=test_instance_id, test__pk=test_id)
        hdr = '%s Test Instance %d of Test %d: %s' % (action, obj.pk, obj.test.pk, obj.test.title)
        cancel_url = reverse('display_test_instance', args=(test_id,test_instance_id,))
    args = {'header': hdr[0].capitalize()+hdr[1:], 'cancel_url': cancel_url}
    up = request.user.get_profile()
    perm = user_can(action,up,obj,True)
    if action=='share':
        return share_obj(request,obj,mode,perm,args,up)
    elif action=='export':
        return export_obj(request,obj,mode,perm,args)
    
        
def share_obj(request,obj,mode,perm,args,up):
    if perm['granted']:
        if request.method == 'POST':
            form = ShareObjectForm(request.POST)
            if form.is_valid():
                share_list = form.cleaned_data['share_with']
                obj.collaborators.add(*share_list)
                create_log_entry(up,'shared',obj,share_list)
                set_alert(request,'share',obj.pk)
                if mode=='Test':        # remove users as collaborators from test instances (i.e. elevate their status to test collaborator)
                    for u in share_list:
                        coll_ti = TestInstance.objects.filter(test=obj,collaborators=u)
                        for ti in coll_ti:
                            ti.collaborators.remove(u)
                    return HttpResponseRedirect(reverse('display_test', args=(obj.pk,)))
                elif mode=='Test Instance':
                    ti_list = [obj]
                    return HttpResponseRedirect(reverse('display_test_instance', args=(obj.test.pk,obj.pk,)))
        else:
            form = ShareObjectForm()
        form.fields['available'].queryset = get_available_collaborators(obj)
        args['form'] = form
    else:
        if not perm['perm_user']:
            args['error'] = 'You do not have permission to share this %s.' % (mode)
            args['header'] = 'Share %s' % (mode)
        elif not perm['perm_obj']:
            args['error'] = 'There are no available collaborators for this %s.' % (mode)
    args['to_enroll'] = 'share_with'
    args['submit_value'] = 'Share'
    return render_to_response('testtool/manager/create_edit_test_instance_share.html', args, context_instance=RequestContext(request))
    
    
def get_available_collaborators(obj):
    # all user profiles who the object can be shared with (all Testers excluding object owner/collaborators)
    exclude_list = [obj.owner.pk] + [x.pk for x in obj.collaborators.all()]
    if isinstance(obj,Test):
        pass
    elif isinstance(obj,TestInstance):      # additionally exclude Test owner/collaborators
        exclude_list = exclude_list + [obj.test.owner.pk] + [x.pk for x in obj.test.collaborators.all()]
    else:
        raise Exception('user_permission: Must pass Test or TestInstance object.')
    return UserProfile.objects.filter(user__groups__name__iexact='Testers').exclude(pk__in=exclude_list)
        
        
def export_obj(request,obj,mode,perm,args):
    if perm['granted']:
        if request.method == 'POST':
            form = ExportDataForm(request.POST)
            if form.is_valid():
                if mode=='Test':
                    ti_set = TestInstance.objects.filter(test=obj)
                    ti_list = []
                    for ti in ti_set:
                        if ti.has_data():
                            ti_list.append(ti)
                elif mode=='Test Instance':
                    ti_list = [obj]
                return export_data(form.cleaned_data['format'],ti_list)
        else:
            form = ExportDataForm()
        args['form'] = form
    else:
        if not perm['perm_user']:
            args['error'] = 'You do not have permission to export this %s.' % (mode)
            args['header'] = 'Export %s' % (mode)
        elif not perm['perm_obj']:
            args['error'] = 'This %s does not have any data.' % (mode)
    return render_to_response('testtool/manager/export_data.html', args, context_instance=RequestContext(request))
        
        
def export_data(format_list, ti_list):
    num_format = len(format_list)
    num_ti = len(ti_list)
    if num_format==0 or num_ti==0:
        raise Exception('export_data: empty list.')
    if num_format==1 and num_ti==1:
        ti = ti_list[0]
        raw_data = get_raw_data(ti)
        data = get_formatted_data(raw_data, format_list[0])
        response = HttpResponse(content_type=data['type'])
        response['Content-Disposition'] = 'attachment; filename=%s_instance_%d.%s' % (ti.test.title, ti.pk, data['ext'])
        response.write(data['buffer'].getvalue())
        data['buffer'].close()
    else:
        zip_buffer = StringIO()
        zip = zipfile.ZipFile(zip_buffer,'a',zipfile.ZIP_DEFLATED)
        for ti in ti_list:
            raw_data = get_raw_data(ti)
            for format in format_list:
                data = get_formatted_data(raw_data, format)
                zip.writestr('%s_instance_%d.%s' % (ti.test.title, ti.pk, data['ext']), data['buffer'].getvalue())
                data['buffer'].close()
        for file in zip.filelist:       # fix for Linux zip files read in Windows (http://bitkickers.blogspot.com/2010/07/django-zip-files-create-dynamic-in.html)
            file.create_system = 0
        zip.close()
        response = HttpResponse(content_type='application/zip')
        if num_ti==1:
            response['Content-Disposition'] = 'attachment; filename=%s_instance_%d.zip' % (ti.test.title, ti.pk)
        else:
            response['Content-Disposition'] = 'attachment; filename=%s_data.zip' % (ti.test.title)
        response.write(zip_buffer.getvalue())
        zip_buffer.close()
    return response
       
                
def get_raw_data(ti):
    # this should eventually extract the data out of the test instance so that the database only needs to be accessed once for returning a variety of formats
    return ti
    
    
def get_formatted_data(raw_data, format):
    buffer = StringIO()
    if format == 'report':
        data = format_as_report(raw_data,buffer)
        type = 'application/pdf'
        ext = 'pdf'
    elif format == 'spreadsheet':
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
    elif method in ['DSIS', 'DSCQS']:
        subject_data = ti.subjects.order_by('pk').values_list
        user_names = subject_data('user__username',flat=True)
        if method=='DSIS':
            numBlanks = 0;
        elif method=='DSCQS':
            numBlanks = 1;
        writer.writerow(['User Name',  ''] + insertBlankColumns(list(user_names),numBlanks))
        writer.writerow(['First Name', ''] + insertBlankColumns(list(subject_data('user__first_name',flat=True)),numBlanks))
        writer.writerow(['Last Name',  ''] + insertBlankColumns(list(subject_data('user__last_name',flat=True)),numBlanks))
        writer.writerow(['Birth Date', ''] + insertBlankColumns(list(subject_data('birth_date',flat=True)),numBlanks))
        writer.writerow(['Gender',     ''] + insertBlankColumns(list(subject_data('sex',flat=True)),numBlanks))
        writer.writerow('')
        writer.writerow(['Test Case', 'Play Order'] + insertBlankColumns(['Score: ' + u for u in user_names],numBlanks))
        if method=='DSCQS':
            writer.writerow(['', ''] + [type for u in user_names for type in ['Reference', 'Test']])
        all_test_cases = ti.test.testcase_set.all()
        for ii,tc in enumerate(all_test_cases):
            all_tci = tc.testcaseinstance_set.filter(test_instance=ti).all()
            for jj,tci in enumerate(all_tci):
                subj_scores = []
                for pk in subject_data('pk',flat=True):     # have to loop through subjects in case of empty scores
                    if method=='DSIS':
                        try:
                            obj = ScoreDSIS.objects.get(test_case_instance=tci,subject__id=pk)
                            val = obj.value
                        except ScoreDSIS.DoesNotExist:
                            val = ''
                        subj_scores.append(val)
                    elif method=='DSCQS':
                        try:
                            obj = ScoreDSCQS.objects.get(test_case_instance=tci,subject__id=pk)
                            first_item = TestCaseItem.objects.get(test_case=tci.test_case,play_order=1)
                        except ObjectDoesNotExist:
                            val_ref = ''
                            val_test = ''
                        else:
                            if first_item.is_reference:     # reference video was played first, so value1 corresponds to it
                                val_ref = obj.value1
                                val_test = obj.value2
                            else:                           # test video was played first, and has value = value1
                                val_ref = obj.value2
                                val_test = obj.value1
                        subj_scores.extend([val_ref,val_test])
                writer.writerow([str(ii+1), tci.play_order] + subj_scores)
    return buffer
    
    
def insertBlankColumns(list_in,numBlanks):
    out = []
    for x in list_in:
        out.append(x)
        out.extend(['' for y in range(0,numBlanks)])
    return out
    
    
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
                        first_item = TestCaseItem.objects.get(test_case=tci.test_case,play_order=1)
                        if first_item.is_reference:     # reference video was played first, so value1 corresponds to it
                            val_ref = subj_score.value1
                            val_test = subj_score.value2
                        else:                           # test video was played first, and has value = value1
                            val_ref = subj_score.value2
                            val_test = subj_score.value1
                        score = { 'val_ref': float(val_ref), 'val_test': float(val_test) }
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

    
    
########################################################################################################
##################################         PROFILE FUNCTIONS        ####################################
########################################################################################################
@login_required
@group_required('Testers')
@user_passes_test(has_user_profile)
def render_profile(request):
    u = request.user
    up = u.get_profile()
    args = {'uform':DisplayUserForm(instance=u),'upform':DisplayUserProfileForm(instance=up)}
    return render_to_response('testtool/manager/profile.html', args, context_instance=RequestContext(request))
