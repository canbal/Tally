from django.conf.urls.defaults import *


# URLS from all sub-apps
urlpatterns = patterns('',
    url(r'^', include('testtool.main.urls')),
    url(r'^', include('testtool.manager.urls')),
    url(r'^', include('testtool.registration.urls')),
)