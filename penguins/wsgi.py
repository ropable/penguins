import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguins.settings")

from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguins.settings")
application = Cling(MediaCling(get_wsgi_application()))
