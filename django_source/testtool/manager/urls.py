from django.conf.urls.defaults import *
from testtool.manager.views import CreateTest, DisplayTest, EditTest, CreateTestInstance, DisplayTestInstance, EditTestInstance

urlpatterns = patterns('testtool.manager.views',

    ### Tests
    url(r'^tests/$',                                'list_tests',       name='list_tests'),
    url(r'^tests/(?P<test_id>\d+)/addvideo/$',      'add_video',        name='add_video'),
    url(r'^deletevideo/(?P<video_id>\d+)/$',        'delete_video',     name='delete_video'),
    url(r'^tests/(?P<test_id>\d+)/addtestcase/$',   'add_test_case',    name='add_test_case'),
    url(r'^deletetestcase/(?P<test_case_id>\d+)/$', 'delete_test_case', name='delete_test_case'),
    
    ### Test Instances
    url(r'^tests/(?P<test_id>\d+)/instances/$',                                  'list_test_instances',   name='list_test_instances'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/delete$',  'delete_test_instance',  name='delete_test_instance'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/run/$',    'run_test_instance',     name='run_test_instance'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/unshare$', 'unshare_test_instance', name='unshare_test_instance'),
    
    ### Share/Export
    url(r'^share/$',       'share_test',        name='share_test'),
    url(r'^share/save/$',  'share_test_submit', name='share_test_submit'),
    url(r'^export/$',      'export_data',       name='export_data'),
    url(r'^export/save/$', 'save_data',         name='save_data'),
    
    ### Misc
    url(r'^logbook/$',                          'log_book',     name='log_book'),
    url(r'^(?P<test_instance_id>\d+)/mirror/$', 'mirror_score', name='mirror_score'),
    url(r'^about/$',                            'about',        name='about'),
    url(r'^help/$',                             'help',         name='help'),
)

# Class-based views
urlpatterns += patterns('',
    url(r'^tests/create/$',                                                   CreateTest.as_view(),          name='create_test'),
    url(r'^tests/(?P<test_id>\d+)/$',                                         DisplayTest.as_view(),         name='display_test'),
    url(r'^tests/(?P<test_id>\d+)/edit/$',                                    EditTest.as_view(),            name='edit_test'),
    url(r'^tests/(?P<test_id>\d+)/instances/create$',                         CreateTestInstance.as_view(),  name='create_test_instance'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/$',     DisplayTestInstance.as_view(), name='display_test_instance'),
    url(r'^tests/(?P<test_id>\d+)/instances/(?P<test_instance_id>\d+)/edit$', EditTestInstance.as_view(),    name='edit_test_instance'),
)