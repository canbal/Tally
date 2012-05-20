from django.conf.urls.defaults import *


# URLS from all sub-apps
urlpatterns = patterns('',
    url(r'^', include('GenericTest.main.urls')),
    url(r'^', include('GenericTest.manager.urls')),
    url(r'^', include('GenericTest.registration.urls')),
)