from django.conf.urls.defaults import *


urlpatterns = patterns('testtool.main.views',
    url(r'^$','index'),
    url(r'^testme/$','testme'), 
    url(r'^enroll/$','enroll'),
    url(r'^(?P<test_instance_id>\d+)/add/$', 'add_test_case_item'),
    url(r'^(?P<test_instance_id>\d+)/get_media/$', 'get_media'),
    url(r'^(?P<test_instance_id>\d+)/tally/$', 'tally'),
    url(r'^(?P<test_instance_id>\d+)/status/$', 'status'),
    url(r'^(?P<test_instance_id>\d+)/reset/$', 'reset_test_instance'),
    url(r'^(?P<test_instance_id>\d+)/enroll/$', 'enroll_to_test_instance'),
)
