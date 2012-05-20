from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'GenericTest.registration.views.custom_login', { 'template_name':'GenericTest/registration/login.html' }),
    url(r'^register/$', 'GenericTest.registration.views.register'),
    url(r'^profile/$', 'GenericTest.registration.views.render_profile'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)