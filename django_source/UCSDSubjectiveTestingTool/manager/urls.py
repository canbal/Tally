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
        # Function:   Allows a user to create a TestInstance of <test_id>
        # Links From: /<test_id>/
        # Links To:   homepage, /<test_id>/instance/save/

    url(r'^(?P<test_id>\d+)/instance/save/$', 'save_test_instance'),
        # Function:   Saves a TestInstance to the database.  Redirects to /<test_id>/<test_instance_id>/, maybe display a note that this TestInstance was just successfully created.
        # Links From: /<test_id>/instance/
        # Links To:   same as /<test_id>/<test_instance_id>/
        
    url(r'^(?P<test_id>\d+)/(?P<test_instance_id>\d+)/start/$', 'start_test'),
        # Function:   This page prompts the user to press the start button on the Qt app, which can extract the data it needs from the URL
        # Links From: /<test_id>/<test_instance_id>/,
        # Links To:   homepage, some sort of test instance status page
)
