from django.conf.urls.defaults import *
from testtool.manager.views import TestCreateView, TestUpdateView

urlpatterns = patterns('testtool.manager.views',

    ### Create Test
    #url(r'^createtest/cases/$', 'create_test_cases'),
    #url(r'^createtest/save/$', 'save_test'),
    #url(r'^(?P<test_pk>\d+)/addvideo$', 'add_video', name='add_video'),
    url(r'^deletevideo/(?P<video_pk>\d+)/$', 'delete_video', name='delete_video'),
    url(r'^tests/create/cases/$', 'create_test_cases'),
    url(r'^tests/create/save/$', 'save_test'),
    url(r'^tests/(?P<test_pk>\d+)/addvideo$', 'add_video', name='add_video'),
    
    ### Display Test and TestInstance
    url(r'^tests/$', 'list_tests'),
    #url(r'^(?P<test_pk>\d+)/testinstances/$', 'list_test_instances'),
    #url(r'^(?P<test_id>\d+)/$', 'display_test'),
    #url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/$', 'display_test_instance'),
    url(r'^tests/(?P<test_pk>\d+)/instances/$', 'list_test_instances'),
    url(r'^tests/(?P<test_id>\d+)/$', 'display_test'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/$', 'display_test_instance'),
    
    ### Create TestInstance and run
    #url(r'^(?P<test_id>\d+)/instance/$', 'create_test_instance'),
    #url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/start/$', 'start_test'),
    url(r'^tests/(?P<test_id>\d+)/instances/create$', 'create_test_instance'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/start/$', 'start_test'),
    
    ### Export data
    url(r'^export/$', 'export_data'),
    url(r'^export/save/$', 'save_data'),
        
    ### Share data
    url(r'^share/$', 'share_test'),
    url(r'^share/save/$', 'share_test_submit'),
    
    ### Misc
    url(r'^about/$', 'about'),
    url(r'^help/$', 'help'),
)

urlpatterns += patterns('',
    #url(r'^createtest/$',         TestCreateView.as_view(), name='create_test'),
    #url(r'^(?P<pk>\d+)/update/$', TestUpdateView.as_view(), name='update_test'),
    url(r'^tests/create/$',         TestCreateView.as_view(), name='create_test'),
    url(r'^tests/(?P<pk>\d+)/update/$', TestUpdateView.as_view(), name='update_test'),
)