import os
import sys

path = 'C:/Users/Ankit/Desktop/Tally/django_source/Tally'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Tally.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


