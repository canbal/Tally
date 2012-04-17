from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from GenericTest.models import *


urlpatterns = patterns('GenericTest.views',
    url(r'^$',
        ListView.as_view(
            queryset=TestInstance.objects.order_by('-create_time')[:10],
            context_object_name='latest_test_instances',
            template_name='GenericTest/index.html')),
    url(r'^(?P<test_instance_id>\d+)/add/$', 'add_test_case_item'),
    url(r'^(?P<test_instance_id>\d+)/get_media/$', 'get_media'),
    url(r'^(?P<test_instance_id>\d+)/tally/$', 'tally'),
)

# URLS from other apps
urlpatterns += patterns('',
    url(r'^accounts/', include('registration.urls')),
    url(r'^', include('manager.urls')),
)