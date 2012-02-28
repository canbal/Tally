from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from GenericTest.models import Test 

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Test.objects.order_by('-create_date')[:5],
            context_object_name='latest_test_list',
            template_name='GenericTest/index.html')),
    url(r'^(?P<pk>\d+)/$',
        DetailView.as_view(
            model=Test,
            template_name='GenericTest/test_cases.html')),
    url(r'^add_video/$', 'GenericTest.views.add_video'),  
    url(r'^(?P<test_id>\d+)/add_case/$', 'GenericTest.views.add_case'),
)