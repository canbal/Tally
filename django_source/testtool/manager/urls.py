from django.conf.urls.defaults import *
from testtool.manager.views import TestCreateView, TestUpdateView

urlpatterns = patterns('testtool.manager.views',

    ### Create Test
        
        # Allows user to create TestCases using a drag-and-drop tool
    url(r'^createtest/cases/$', 'create_test_cases'),
        
        # Saves a Test and all associated Video, TestCase, and TestCaseItem objects to the database.  Redirects to /<test_id>/, maybe display a note that this Test was just successfully created.
    url(r'^createtest/save/$', 'save_test'),
    
        # Adds video to a test
    url(r'^(?P<test_pk>\d+)/addvideo$', 'add_video', name='add_video'),
 
         # Deletes a video
    url(r'^deletevideo/(?P<video_pk>\d+)/$', 'delete_video', name='delete_video'),
    
    ### Display Test and TestInstance
        # Lists all tests for which the user is an owner or collaborator
    url(r'^tests/$', 'list_tests'),
    url(r'^(?P<test_pk>\d+)/testinstances$', 'list_test_instances'),
        
        # Displays data for an existing test
    url(r'^(?P<test_id>\d+)/$', 'display_test'),
        
        # Displays data for an existing TestInstance of <test_id>.
    url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/$', 'display_test_instance'),
        

    ### Create TestInstance and run
        # Allows a user to create a TestInstance of <test_id>.  Saves a TestInstance to the database, along with associated TestCaseInstances.  Redirects to /<test_id>/<test_instance_id>/, maybe display a note that this TestInstance was just successfully created.
    url(r'^(?P<test_id>\d+)/instance/$', 'create_test_instance'),
    
        # This page prompts the user to press the start button on the Qt app, which can extract the data it needs from the URL    
    url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/start/$', 'start_test'),
    
            
    ### Export data
        # This page allows the user to select options for exporting data: test, test instance, and format.  When accessed from a test or test instance page, those options should be pre-populated.  Data formats should include CSV, Excel, some kind of file or module to read the data into Python, and a *.m file to read the data into Matlab.  A test report showing all options, parameters, videos, test cases, and randomization should be automatically generated as well.
    url(r'^export/$', 'export_data'),
        
        # This page exports the data based on the test method.  There is no template, it simply returns the data files.
    url(r'^export/save/$', 'save_data'),
        

    ### Share data
        # This page allows the user to share tests and/or test instances that they own with other testers.  When accessed from a test or test instance page, those options should be pre-populated.
    url(r'^share/$', 'share_test'),
        
        # This page adds collaborators to a test or test instance.  Redirects to /<test_id>/ or /<test_id>/<test_instance_id>/    
    url(r'^share/save/$', 'share_test_submit'),
    
    url(r'^about/$', 'about'),
    url(r'^help/$', 'help'),
    
)

urlpatterns += patterns('',
    url(r'^createtest/$',         TestCreateView.as_view(), name='create_test'),
    url(r'^(?P<pk>\d+)/update/$', TestUpdateView.as_view(), name='update_test'),
)