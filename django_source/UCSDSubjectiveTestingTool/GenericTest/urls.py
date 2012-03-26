from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from GenericTest.models import *

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Test.objects.order_by('-create_date')[:5],
            context_object_name='latest_test_list',
            template_name='GenericTest/index.html')),
    url(r'^(?P<testInstance_id>\d+)/scored$', 'GenericTest.views.results'),
    url(r'^add_video/$', 'GenericTest.views.add_video'),  
    url(r'^add_test/$', 'GenericTest.views.add_test'),  
    url(r'^(?P<test_id>\d+)/add_case/$', 'GenericTest.views.add_case'),
    url(r'^(?P<testInstance_id>\d+)/get_media/$', 'GenericTest.views.get_media'),
    url(r'^(?P<testInstance_id>\d+)/tally/$', 'GenericTest.views.tally'),
    url(r'^accounts/', include('registration.urls')),
)