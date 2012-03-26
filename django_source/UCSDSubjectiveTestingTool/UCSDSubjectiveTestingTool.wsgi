import os
import sys

path = 'C:/Users/Ankit/Desktop/UCSD-Subjective-Testing-Tool/django_source/UCSDSubjectiveTestingTool'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'UCSDSubjectiveTestingTool.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


