from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import login
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from testtool.shortcuts import has_user_profile
from forms import RegistrationForm, UserProfileForm

def register(request):
    return render_to_response('testtool/registration/register_select.html')

def register_subject(request):
    if request.method == 'POST':
        rform = RegistrationForm(request.POST)
        pform = UserProfileForm(request.POST)
        if rform.is_valid() and pform.is_valid():
            subject = rform.save()
            try:
                subjects = Group.objects.get(name='Subjects')
            except Group.DoesNotExist:
                subjects = Group(name='Subjects')
                subjects.save()
                perm = Permission.objects.get(codename='add_score')
                subjects.permissions.add(perm)
            subject.groups.add(subjects)
            profile = pform.save(commit=False)
            profile.user = subject
            profile.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        rform = RegistrationForm()
        pform = UserProfileForm()
 
    return render_to_response('testtool/registration/register.html',  {'rform': rform, 'pform': pform },
                              context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_superuser)
def register_tester(request):
    if request.method == 'POST':
        rform = RegistrationForm(request.POST)
        pform = UserProfileForm(request.POST)
        if rform.is_valid() and pform.is_valid():
            tester = rform.save()
            try:
                testers = Group.objects.get(name='Testers')
            except Group.DoesNotExist:
                testers = Group(name='Testers')
                testers.save()
            tester.groups.add(testers)
            profile = pform.save(commit=False)
            profile.user = tester
            profile.save()
            return HttpResponseRedirect(reverse('admin:index'))
    else:
        rform = RegistrationForm()
        pform = UserProfileForm()
 
    return render_to_response('testtool/registration/register.html',  {'rform': rform, 'pform': pform },
                              context_instance=RequestContext(request))
        
@login_required
@user_passes_test(has_user_profile)
def render_profile(request):
    if request.user.groups.filter(name='Testers'):
        return HttpResponseRedirect(reverse('tester_profile'))
    elif request.user.groups.filter(name='Subjects'):
        return HttpResponseRedirect('/')
    else:
        return HttpResponse('You are not registered as a subject or a tester in the system!')
    

def custom_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return login(request, *args, **kwargs)
