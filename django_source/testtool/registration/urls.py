from django.conf.urls.defaults import *

urlpatterns = patterns('testtool.registration.views',
    url(r'^login/$',           'custom_login',    { 'template_name':'testtool/registration/login.html' }, name='login'),
    url(r'^register/subject$', 'register',        { 'type':'subject' }, name='register_subject'),
    url(r'^register/tester$',  'register_tester', name='register_tester'),
    url(r'^profile/$',         'render_profile',  name='profile'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout_then_login', name='logout'),
)