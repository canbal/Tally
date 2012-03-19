from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'registration.views.custom_login'),
    url(r'^register/$', 'registration.views.register'),
    url(r'^profile/$', 'registration.views.render_profile'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)