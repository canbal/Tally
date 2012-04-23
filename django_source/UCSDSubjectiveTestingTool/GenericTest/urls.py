from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from GenericTest.models import *


urlpatterns = patterns('GenericTest.views',
    url(r'^$','index'),
    url(r'^enroll/$','enroll'),
    url(r'^(?P<test_instance_id>\d+)/add/$', 'add_test_case_item'),
    url(r'^(?P<test_instance_id>\d+)/get_media/$', 'get_media'),
    url(r'^(?P<test_instance_id>\d+)/tally/$', 'tally'),
    url(r'^(?P<test_instance_id>\d+)/reset/$', 'reset_test_instance'),
    url(r'^(?P<test_instance_id>\d+)/enroll/$', 'enroll_to_test_instance'),
)

# URLS from other apps
urlpatterns += patterns('',
    url(r'^', include('registration.urls')),
    url(r'^', include('manager.urls')),
)