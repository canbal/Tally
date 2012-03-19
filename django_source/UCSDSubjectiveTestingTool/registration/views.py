from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from forms import RegistrationForm

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse('registration.views.render_profile'))
    else:
        form = RegistrationForm()
 
    return render_to_response("registration/register.html",  {'form': form,  },
                              context_instance=RequestContext(request))
        
@login_required
def render_profile(request):
    if not request.user.is_superuser:
        return HttpResponse("You are a normal user!")
    else:
        return HttpResponse("You are a super user! You are awesome!")

def custom_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('registration.views.render_profile'))
    else:
        return login(request, *args, **kwargs)
