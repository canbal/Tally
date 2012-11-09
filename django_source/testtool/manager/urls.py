from django.conf.urls.defaults import *
from testtool.manager.views import TestCreateView, TestUpdateView

urlpatterns = patterns('testtool.manager.views',

    ### Create Test
    url(r'^tests/(?P<test_pk>\d+)/addvideo/$',      'add_video',        name='add_video'),
    url(r'^deletevideo/(?P<video_pk>\d+)/$',        'delete_video',     name='delete_video'),
    url(r'^tests/(?P<test_pk>\d+)/addtestcase/$',   'add_test_case',    name='add_test_case'),
    url(r'^deletetestcase/(?P<test_case_pk>\d+)/$', 'delete_test_case', name='delete_test_case'),
    
    ### Display Test and TestInstance
    url(r'^tests/$', 'list_tests'),
    url(r'^tests/(?P<test_pk>\d+)/instances/$', 'list_test_instances'),
    url(r'^tests/(?P<test_id>\d+)/$', 'display_test'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/$', 'display_test_instance'),
    
    ### Create TestInstance and run
    url(r'^tests/(?P<test_id>\d+)/instances/create$', 'create_test_instance'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/start/$', 'start_test'),
    
    ### Export data
    url(r'^export/$', 'export_data'),
    url(r'^export/save/$', 'save_data'),
    
    ### Share data
    url(r'^share/$', 'share_test'),
    url(r'^share/save/$', 'share_test_submit'),
    
    ### Misc
    url(r'^(?P<test_instance_id>\d+)/mirror/$', 'mirror_score'),
    url(r'^about/$', 'about'),
    url(r'^help/$', 'help'),
)

urlpatterns += patterns('',
    url(r'^tests/create/$',             TestCreateView.as_view(), name='create_test'),
    url(r'^tests/(?P<pk>\d+)/update/$', TestUpdateView.as_view(), name='update_test'),
)