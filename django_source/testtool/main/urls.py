from django.conf.urls.defaults import *


urlpatterns = patterns('testtool.main.views',
    # Subject URLs
    url(r'^$','index'),
    url(r'^(?P<test_instance_id>\d+)/tally/$', 'tally'),
    url(r'^(?P<test_instance_id>\d+)/status/$', 'status'),
    url(r'^(?P<test_instance_id>\d+)/mirror/$', 'mirror_score'),
    
    # Desktop App URLs
    url(r'^(?P<test_instance_id>\d+)/init/$', 'init_test_instance'),
    url(r'^(?P<test_instance_id>\d+)/get_media/$', 'get_media'),
    
    # Unused URLs
    url(r'^testme/$','testme'), 
    url(r'^enroll/$','enroll'),
    url(r'^(?P<test_instance_id>\d+)/enroll/$', 'enroll_to_test_instance'),
    url(r'^(?P<test_instance_id>\d+)/add/$', 'add_test_case_item'),
)
