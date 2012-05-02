from django.conf.urls.defaults import *

urlpatterns = patterns('manager.views',

    ### Create Test
    url(r'^createtest/$', 'create_test'),
        # Function:   Allows user to input test details (name, title, etc.) and possibly add videos for a Test to create
        # Links From: homepage
        # Links To:   homepage, /createtest/cases/
        
    url(r'^createtest/cases/$', 'create_test_cases'),
        # Function:   Allows user to create TestCases using a drag-and-drop tool
        # Links From: /createtest/
        # Links To:   homepage, /createtest/, /createtest/save/
        
    url(r'^createtest/save/$', 'save_test'),
        # Function:   Saves a Test and all associated Video, TestCase, and TestCaseItem objects to the database.  Redirects to /<test_id>/, maybe display a note that this Test was just successfully created.
        # Links From: /createtest/cases/
        # Links To:   same as /<test_id>/
    
    
    ### Display Test and TestInstance
    url(r'^(?P<test_id>\d+)/$', 'display_test'),
        # Function:   Displays data for an existing test
        # Links From: homepage, redirected from /createtest/save/
        # Links To:   homepage, /<test_id>/<test_instance_id>/, /<test_id>/instance/, other pages to export data, view test instances, delete, edit, etc.

    url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/$', 'display_test_instance'),
        # Function:   Displays data for an existing TestInstance of <test_id>.
        # Links From: /<test_id>/
        # Links To:   /<test_id>/, /<test_id>/<test_instance_id>/start/, other pages to export data, delete, edit, etc.


    ### Create TestInstance and run
    url(r'^(?P<test_id>\d+)/instance/$', 'create_test_instance'),
        # Function:   Allows a user to create a TestInstance of <test_id>.  Saves a TestInstance to the database, along with associated TestCaseInstances.  Redirects to /<test_id>/<test_instance_id>/, maybe display a note that this TestInstance was just successfully created.
        # Links From: /<test_id>/
        # Links To:   same as /<test_id>/<test_instance_id>/
        
    url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/start/$', 'start_test'),
        # Function:   This page prompts the user to press the start button on the Qt app, which can extract the data it needs from the URL
        # Links From: /<test_id>/<test_instance_id>/,
        # Links To:   homepage, some sort of test instance status page
        
        
    ### Export data
    url(r'^export/$', 'export_data'),
        # Function:   This page allows the user to select options for exporting data: test, test instance, and format.  When accessed from a test or test instance page, those options should be pre-populated.  Data formats should include CSV, Excel, some kind of file or module to read the data into Python, and a *.m file to read the data into Matlab.  A test report showing all options, parameters, videos, test cases, and randomization should be automatically generated as well.
        # Links From: homepage, /<test_id>/, /<test_id>/<test_instance_id>/,
        # Links To:   homepage, /<test_id>/ pages, /<test_id>/<test_instance_id>/ pages

    url(r'^export/save/$', 'save_data'),
        # Function:   This page exports the data based on the test method.  There is no template, it simply returns the data files.
        # Links From: /export/
        # Links To:   homepage
)
