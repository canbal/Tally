from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import login
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from testtool.shortcuts import has_user_profile
from forms import RegistrationForm, UserProfileForm
from testtool.manager.views import create_log_entry


@user_passes_test(lambda u: u.is_superuser)
def register_tester(request):
    return register(request,'tester')
                              
                              
def register(request,type):
    if type not in ['subject','tester']:
        raise Exception('register: invalid type.')
    if request.method == 'POST':
        rform = RegistrationForm(request.POST)
        pform = UserProfileForm(request.POST)
        if rform.is_valid() and pform.is_valid():
            user = rform.save()
            if type=='subject':
                group = Group.objects.get(name='Subjects')
            elif type=='tester':
                group = Group.objects.get(name='Testers')
            user.groups.add(group)
            profile = pform.save(commit=False)
            profile.user = user
            profile.save()
            if type=='tester':
                create_log_entry(profile,'joined',[])
            return HttpResponseRedirect(reverse('home'))
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
    return HttpResponseRedirect('/')
    

def custom_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return login(request, *args, **kwargs)
