from django import template
from django.core.urlresolvers import reverse
#import re

register = template.Library()

@register.simple_tag
def active(request, url):
    if reverse(url) == request.path:
        return 'active'
    return ''
    
    # http://gnuvince.wordpress.com/2007/09/14/a-django-template-tag-for-the-current-active-page/