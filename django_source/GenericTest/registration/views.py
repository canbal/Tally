from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from GenericTest.models.registration import *
from forms import RegistrationForm, UserProfileForm


def register(request):
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
            return HttpResponseRedirect(reverse('GenericTest.registration.views.render_profile'))
    else:
        rform = RegistrationForm()
        pform = UserProfileForm()
 
    return render_to_response('GenericTest/registration/register.html',  {'rform': rform, 'pform': pform },
                              context_instance=RequestContext(request))
        
@login_required
def render_profile(request):
    try:
    # A user may not have an associated UserProfile - i.e. SuperUser
        up = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return HttpResponse('You are not registered as a subject or a tester in the system!')
    else:
        if request.user.groups.filter(name='Testers'):
            return render_to_response('GenericTest/manager/profile.html', context_instance=RequestContext(request))
        elif request.user.groups.filter(name='Subjects'):
            return HttpResponseRedirect('/')
        else:
            return HttpResponse('You are not registered as a subject or a tester in the system!')
    

def custom_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('GenericTest.main.views.index'))
    else:
        return login(request, *args, **kwargs)
