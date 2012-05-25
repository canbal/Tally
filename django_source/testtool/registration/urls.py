from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'testtool.registration.views.custom_login', { 'template_name':'testtool/registration/login.html' }),
    url(r'^register/$', 'testtool.registration.views.register'),
    url(r'^register/subject$', 'testtool.registration.views.register_subject'),
    url(r'^register/tester$', 'testtool.registration.views.register_tester'),
    url(r'^profile/$', 'testtool.registration.views.render_profile'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)